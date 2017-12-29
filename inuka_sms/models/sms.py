# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SmsList(models.Model):
    _name = 'sms.list'
    _description = 'SMS List'

    name = fields.Char(string="Name")
    var1 = fields.Char("VAR 1")
    var2 = fields.Char("VAR 2")
    var3 = fields.Char("VAR 3")
    var4 = fields.Char("VAR 4")
    var5 = fields.Char("VAR 5")
    var6 = fields.Char("VAR 6")
    description = fields.Text()
    active = fields.Boolean(default=True)
    sms_recipients_count = fields.Integer(compute="_compute_sms_recipients_count")

    def _compute_sms_recipients_count(self):
        SmsRecipients = self.env['sms.recipients']
        for record in self:
            record.sms_recipients_count = SmsRecipients.search_count([('sms_list_id', '=', record.id)])

    @api.multi
    def view_sms_recipients(self):
        self.ensure_one()
        recipients = self.env['sms.recipients'].search([('sms_list_id', '=', self.id)])
        action = self.env.ref('inuka_sms.action_sms_recipients_form').read()[0]
        action['domain'] = [('id', 'in', recipients.ids)]
        return action


class SmsRecipients(models.Model):
    _name = 'sms.recipients'
    _description = 'SMS Recipients'

    name = fields.Char(string="Name")
    partner_id = fields.Many2one("res.partner", string="Member")
    member_id = fields.Char(related="partner_id.ref", string="Member ID")
    mobile = fields.Char()
    var1 = fields.Char("VAR 1")
    var2 = fields.Char("VAR 2")
    var3 = fields.Char("VAR 3")
    var4 = fields.Char("VAR 4")
    var5 = fields.Char("VAR 5")
    var6 = fields.Char("VAR 6")
    unsubscription_date = fields.Datetime("Unsubscription Date")
    optout = fields.Boolean("Opt Out")
    sms_list_id = fields.Many2one("sms.list", string="SMS List")
