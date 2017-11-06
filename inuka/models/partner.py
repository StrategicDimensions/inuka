# -*- coding: utf-8 -*-

import random
import string
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from random import randint

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char("First Name")
    last_name = fields.Char("Last Name")
    passport_no = fields.Char("ID/Passport No")
    home_phone = fields.Char("Home Phone")
    join_date = fields.Date("Join Date")
    dob = fields.Date("DOB")
    status = fields.Selection([
        ('candidate', 'Candidate'),
        ('new', 'New'),
        ('junior​', 'Junior'),
        ('senior', 'Senior'),
        ('pearl', 'Pearl'),
        ('ruby', 'Ruby'),
        ('emerald', 'Emerald'),
        ('sapphire', 'Sapphire'),
        ('diamond', 'Diamond'),
        ('double_diamond', 'Double Diamond'),
        ('triple_diamond', 'Triple Diamond'),
        ('exective_diamond', 'Exective Diamond'),
        ('presidential', 'Presidential')
        ], string='Status', required=True, default='candidate')
    upline = fields.Many2one("res.partner", string="Upline")
    upline_id = fields.Char(related="upline.ref", string="Upline ID")
    candidate_registrar = fields.Boolean("Candidate Registrar")
    bulk_custodian = fields.Boolean("Bulk Custodian")
    up_front_kits = fields.Boolean("Up-front Kits")
    personal_pv = fields.Float("Personal PV")
    pv_downline_1 = fields.Float("PV Downline 1")
    pv_downline_2 = fields.Float("PV Downline 2")
    pv_downline_3 = fields.Float("PV Downline 3")
    pv_downline_4 = fields.Float("PV Downline 4")
    pv_tot_group = fields.Float("PV Tot Group")
    personal_members = fields.Integer("Active Personal Members")
    new_members = fields.Integer("New Members")
    kit = fields.Selection([
        ('small', 'Small Kit'),
        ('medium', 'Medium Kit'),
        ('large', 'Large Kit'),
        ('junior', 'Junior kit'),
        ('senior', 'Senior kit')
        ], string='Kit', required=True, default='small')
    source = fields.Selection([
        ('email', 'Email'),
        ('facebook', 'Facebook'),
        ('fax', 'Fax'),
        ('inuka', 'Inuka'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('whatsapp', 'Whatsapp'),
        ('portal', 'Portal')
        ], string='Source', required=True, default='email')
    is_admin = fields.Boolean(compute="_compute_is_admin", string="Admin")

    _sql_constraints = [
        ('mobile_uniq', 'unique(mobile)', 'Mobile should be unique.'),
        ('email_uniq', 'unique(email)', 'Email should be unique.'),
        ('ref_uniq', 'unique(ref)', 'Internal Reference should be unique.'),
    ]

    def _compute_is_admin(self):
        for partner in self:
            if partner.env.user._is_superuser():
                partner.is_admin = True
            else:
                partner.is_admin = False

    @api.constrains('dob')
    def _check_dob(self):
        for partner in self:
            if partner.dob:
                dob = datetime.strptime(partner.dob, DF)
                today = date.today()
                age = relativedelta(today, dob)
                if age.years < 18:
                    raise ValidationError(_('Member should be 18 years and above.'))

    @api.onchange('first_name', 'last_name')
    def _onchange_first_name(self):
        if self.customer:
            self.name = (self.first_name or '') + ' ' + (self.last_name or '')

    @api.model
    def create(self, vals):
        vals['ref'] = ''.join(random.choice(string.ascii_letters).upper() for x in range(3)) + (str(randint(100,999)))
        return super(ResPartner, self).create(vals)
