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
    sms_recipients_count = fields.Integer(compute="_compute_sms_recipients_count", string="Number of Recipients")

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


class MassSms(models.Model):
    _name = 'mass.sms'
    _description = 'Mass SMS'

    name = fields.Char(string="Name")
    from_mobile_id = fields.Many2one("sms.number", string="From")
    recipient_ids = fields.Many2many('sms.list', 'mass_sms_list_rel', 'mass_sms_id', 'list_id', string='Recipients')
    sms_template_id = fields.Many2one("sms.template", string="Template")
    sms_content = fields.Text("SMS Body")
    scheduled_date = fields.Datetime("Scheduled Date")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('queue', 'In Queue'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled')
        ], string='Status', default='draft', track_visibility='onchange')
    batch_mode = fields.Boolean("Batch Mode")
    batch_size = fields.Integer("Batch Size", default=1000)
    sent = fields.Integer("SMS Sent's")
    pending = fields.Integer("SMS Pending")
    received = fields.Integer("SMS Received")
    errors = fields.Integer("Errors")
    next_departure = fields.Datetime(compute="_compute_next_departure", string='Scheduled date')
    participants = fields.One2many('sms.participant', 'mass_sms_id', string="Participants")
    sms_participant_count = fields.Integer(compute="_compute_sms_participant_count", string="Number of Participants")

    def _compute_sms_participant_count(self):
        for record in self:
            record.sms_participant_count = len(record.participants)

    def _compute_next_departure(self):
        cron_next_call = self.env.ref('inuka_sms.ir_cron_mass_sms_queue').sudo().nextcall
        str2dt = fields.Datetime.from_string
        cron_time = str2dt(cron_next_call)
        for mass_sms in self:
            if mass_sms.schedule_date:
                schedule_date = str2dt(mass_sms.schedule_date)
                mass_sms.next_departure = max(schedule_date, cron_time)
            else:
                mass_sms.next_departure = cron_time

    @api.model
    def _process_mass_sms_queue(self):
        mass_sms = self.search([('state', 'in', ('queue', 'sending')), '|', ('scheduled_date', '<', fields.Datetime.now()), ('scheduled_date', '=', False)])
        for sms in mass_sms:
            if len(sms.get_remaining_recipients()) > 0:
                sms.state = 'sending'
                sms.send_mail()
            else:
                sms.state = 'sent'

    @api.multi
    def generate_participants(self):
        participant = self.env['sms.participant']
        smslist = self.env['sms.list']
        recipient = self.env['sms.recipients']
        for record in self:
            for list in record.recipient_ids:
                recipients = recipient.search([('sms_list_id', '=', list.id)])
                for recipient in recipients:
                    participant.create({'partner_id': recipient.partner_id.id, 'mass_sms_id': record.id})

    @api.multi
    def view_participants(self):
        self.ensure_one()
        action = self.env.ref('inuka_sms.action_sms_participant_form').read()[0]
        action['domain'] = [('id', 'in', self.participants.ids)]
        return action

    @api.multi
    def view_stastics(self):
        return True

    @api.multi
    def button_test_sms(self):
        return True

    @api.multi
    def button_send_all(self):
        self.write({'state': 'queue'})

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancelled'})


class SmsParticipant(models.Model):
    _name = 'sms.participant'
    _description = 'SMS Participant'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one("res.partner", string="Member")
    mass_sms_id = fields.Many2one('mass.sms', string='Mass SMS', ondelete='cascade', required=True)
    state = fields.Selection([
        ('running', 'Running'),
        ('completed', 'Completed'),
        ], default='running', index=True, required=True,
    )


class SmsShortcode(models.Model):
    _name = 'sms.shortcode'
    _description = 'SMS Shortcode'
    _rec_name = 'keyword'

    keyword = fields.Char("Keyword")
    sms_template_id = fields.Many2one("sms.template", string="Template")
    member_required = fields.Boolean("Member Required")
    active = fields.Boolean(default=True)
