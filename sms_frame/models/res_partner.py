# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from openerp import api, fields, models

class ResPartnerSms(models.Model):
    _inherit = "res.partner"

    @api.multi
    def sms_action(self):
        self.ensure_one()
        default_mobile = self.env['sms.number'].search([])[0]
        return {
            'name': 'SMS Compose',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sms.compose',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_from_mobile_id': default_mobile.id,'default_to_number':self.mobile, 'default_record_id':self.id,'default_model':'res.partner'}
         }

    @api.onchange('country_id','mobile')
    def _onchange_mobile(self):
        """Tries to convert a local number to e.164 format based on the partners country, don't change if already in e164 format"""
        if self.mobile:
            if self.country_id and self.country_id.mobile_prefix:
                if self.mobile.startswith("0"):
                    self.mobile = self.country_id.mobile_prefix + self.mobile[1:].replace(" ","")
                elif self.mobile.startswith("+"):
                    self.mobile = self.mobile.replace(" ","")
                else:
                    self.mobile = self.country_id.mobile_prefix + self.mobile.replace(" ","")
            else:
                self.mobile = self.mobile.replace(" ","")

    @api.model
    def create(self, vals):
        res = super(ResPartnerSms, self).create(vals)
        sms_template = self.env.ref('sms_frame.sms_template_inuka_international')
        msg_compose = self.env['sms.compose'].create({
            'record_id': res.id,
            'model': 'res.partner',
            'sms_template_id': sms_template.id,
            'from_mobile_id': self.env.ref('sms_frame.sms_number_inuka_international').id,
            'to_number': res.mobile,
            'sms_content': """ INUKA Welcomes YOU^Thank you for your Registration^ %s %s,your MemberID %s will be active once Kit payment is receipted^More info 27219499850""" %(res.first_name, res.last_name, res.ref)
        })
        msg_compose.send_entity()

        sms_template = self.env.ref('sms_frame.sms_template_inuka_international_referrer')
        msg_compose = self.env['sms.compose'].create({
            'record_id': res.upline.id,
            'model': 'res.partner',
            'sms_template_id': sms_template.id,
            'from_mobile_id': self.env.ref('sms_frame.sms_number_inuka_international').id,
            'to_number': res.upline.mobile,
            'sms_content': """ INUKA New Registration received^WELL DONE, %s^New MemberID %s for %s %s activated once kit is receipted^Info 27219499850""" %(res.upline.name, res.ref, res.first_name, res.last_name)
        })
        msg_compose.send_entity()

        return res
