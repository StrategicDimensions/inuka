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
    sent_date = fields.Datetime(string='Sent Date', copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('queue', 'In Queue'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled')
        ], string='Status', default='draft', track_visibility='onchange')
    batch_mode = fields.Boolean("Batch Mode")
    batch_size = fields.Integer("Batch Size", default=1000)
    sent_ratio = fields.Integer(compute="_compute_statistics", string="SMS Sent's")
    pending_ratio = fields.Integer(compute="_compute_statistics", string="SMS Pending")
    received_ratio = fields.Integer(compute="_compute_statistics", string="SMS Received")
    errors_ratio = fields.Integer(compute="_compute_statistics", string="Errors")
    total = fields.Integer(compute="_compute_statistics")
    sent = fields.Integer(compute="_compute_statistics")
    pending = fields.Integer(compute="_compute_statistics")
    received = fields.Integer(compute="_compute_statistics")
    errors = fields.Integer(compute="_compute_statistics")
    next_departure = fields.Datetime(compute="_compute_next_departure", string='Scheduled date')
    participants = fields.One2many('sms.participant', 'mass_sms_id', string="Participants")
    sms_participant_count = fields.Integer(compute="_compute_sms_participant_count", string="Number of Participants")
    participant_generated = fields.Boolean(copy=False)
    color = fields.Integer()

    def _compute_statistics(self):
        for record in self:
            total = len(record.participants) or 1
            pending = len(record.participants.filtered(lambda r: r.state == 'running'))
            sent = len(record.participants.filtered(lambda r: r.state == 'completed'))
            record.pending_ratio = 100 * pending / total
            record.sent_ratio = 100 * sent / total
            record.received_ratio = 100 * sent / total
            record.errors_ratio = 0
            record.total = len(record.participants)
            record.sent = sent
            record.pending = pending
            record.received = sent
            record.errors = 0

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

    @api.multi
    def get_remaining_recipients(self):
        self.ensure_one()
        return self.participants.filtered(lambda r: r.state == 'running')

    @api.model
    def _process_mass_sms_queue(self):
        mass_sms = self.search([('state', 'in', ('queue', 'sending')), '|', ('scheduled_date', '<', fields.Datetime.now()), ('scheduled_date', '=', False)])
        for sms in mass_sms:
            if len(sms.get_remaining_recipients()) > 0:
                sms.state = 'sending'
                sms.send_sms()
            else:
                sms.state = 'sent'

    def send_sms(self):
        self.ensure_one()
        SmsCompose = self.env['sms.compose']
        participants = self.get_remaining_recipients()
        for participant in participants:
            if participant.partner_id.mobile:
                msg_compose = SmsCompose.create({
                    'record_id': participant.partner_id.id,
                    'model': 'res.partner',
                    'sms_template_id': self.sms_template_id.id,
                    'from_mobile_id': self.env.ref('sms_frame.sms_number_inuka_international').id,
                    'to_number': participant.partner_id.mobile,
                    'sms_content': self.sms_content,
                })
                msg_compose.send_entity()
            participant.state = 'completed'

    @api.multi
    def generate_participants(self):
        participant = self.env['sms.participant']
        recipient = self.env['sms.recipients']
        for record in self:
            if not record.participant_generated:
                for list in record.recipient_ids:
                    recipients = recipient.search([('sms_list_id', '=', list.id)])
                    for recipient in recipients:
                        participant.create({'partner_id': recipient.partner_id.id, 'mass_sms_id': record.id})
                record.participant_generated = True

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
    def button_send_all(self):
        self.write({'sent_date': fields.Datetime.now(), 'state': 'queue'})

    @api.multi
    def button_cancel(self):
        self.mapped('participants').write({'state': 'cancelled'})
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
        ('cancelled', 'Cancelled')
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