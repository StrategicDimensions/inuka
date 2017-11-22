# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

import logging

_logger = logging.getLogger(__name__)


class PaymentAcquirerMygate(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('mygate', 'mygate')])
    mygate_merchant_id = fields.Char(string='Merchant Key', required_if_provider='mygate', groups='base.group_user')
    mygate_application_id = fields.Char(string='Merchant Application', required_if_provider='mygate', groups='base.group_user')

    def _get_mygate_urls(self, environment):
        """ mygate URLs"""
        if environment == 'prod':
            return {'mygate_form_url': ''}
        else:
            return {'mygate_form_url': 'https://virtual.mygateglobal.com/PaymentPage.cfm'}

    @api.multi
    def mygate_form_generate_values(self, values):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        mygate_values = dict(values,
                            mode=0,
                            merchantID=self.mygate_merchant_id,
                            applicationID=self.mygate_application_id,
                            merchantReference=values['reference'],
                            amount=values['amount'],
                            txtCurrencyCode=values['currency'] and values['currency'].name or '',
                            redirectSuccessfulURL=urls.url_join(base_url, '/payment/mygate/return'),
                            redirectFailedURL=urls.url_join(base_url, '/payment/mygate/error'),
                            recipient=values.get('partner_name'),
                            shippingAddress1=values.get('partner_address'),
                            shippingAddress2=values.get('partner_zip'),
                            shippingAddress3=values.get('partner_city'),
                            shippingAddress4=values.get('partner_state').name,
                            shippingAddress5=values.get('partner_country').name,
                            email=values.get('partner_email'),
                            phone=values.get('partner_phone'))
        return mygate_values

    @api.multi
    def mygate_get_form_action_url(self):
        self.ensure_one()
        return self._get_mygate_urls(self.environment)['mygate_form_url']


class PaymentTransactionmygate(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _mygate_form_get_tx_from_data(self, data):
        """ Given a data dict coming from mygate, verify it and find the related
        transaction record. """
        reference = data.get('txnid')
        pay_id = data.get('mihpayid')
        shasign = data.get('hash')
        if not reference or not pay_id or not shasign:
            raise ValidationError(_('mygate: received data with missing reference (%s) or pay_id (%s) or shashign (%s)') % (reference, pay_id, shasign))

        transaction = self.search([('reference', '=', reference)])

        if not transaction:
            error_msg = (_('mygate: received data for reference %s; no order found') % (reference))
            raise ValidationError(error_msg)
        elif len(transaction) > 1:
            error_msg = (_('mygate: received data for reference %s; multiple orders found') % (reference))
            raise ValidationError(error_msg)

        #verify shasign
        shasign_check = transaction.acquirer_id._mygate_generate_sign('out', data)
        if shasign_check.upper() != shasign.upper():
            raise ValidationError(_('mygate: invalid shasign, received %s, computed %s, for data %s') % (shasign, shasign_check, data))
        return transaction

    @api.multi
    def _mygate_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if self.acquirer_reference and data.get('mihpayid') != self.acquirer_reference:
            invalid_parameters.append(
                ('Transaction Id', data.get('mihpayid'), self.acquirer_reference))
        #check what is buyed
        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(
                ('Amount', data.get('amount'), '%.2f' % self.amount))

        return invalid_parameters

    @api.multi
    def _mygate_form_validate(self, data):
        status = data.get('status')
        transaction_status = {
            'success': {
                'state': 'done',
                'acquirer_reference': data.get('mygateId'),
                'date_validate': fields.Datetime.now(),
            },
            'pending': {
                'state': 'pending',
                'acquirer_reference': data.get('mygateId'),
                'date_validate': fields.Datetime.now(),
            },
            'failure': {
                'state': 'cancel',
                'acquirer_reference': data.get('mygateId'),
                'date_validate': fields.Datetime.now(),
            },
            'error': {
                'state': 'error',
                'state_message': data.get('error_Message') or _('mygate: feedback error'),
                'acquirer_reference': data.get('mygateId'),
                'date_validate': fields.Datetime.now(),
            }
        }
        vals = transaction_status.get(status, False)
        if not vals:
            vals = transaction_status['error']
            _logger.info(vals['state_message'])
        return self.write(vals)
