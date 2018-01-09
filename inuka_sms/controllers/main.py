# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class SMSPushNotification(http.Controller):

    @http.route('/sms/push-notifications/', type="http", auth="public", csrf=False)
    def sms_push_notification(self, *args, **kwargs):
        print ('>>>', args, kwargs,request)
        if kwargs.get('apiMsgId') and kwargs.get('status'):
            self.env['sms.message'].search([('sms_gateway_message_id', '=', kwargs.get('apiMsgId'))]).write({'status_code': kwargs.get('status')})
        return 'Done'
