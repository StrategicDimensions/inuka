# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    product_ids = fields.Many2many('product.product', 'helpdesk_ticket_product_rel', 'ticket_id', 'product_id', string="Products")
    mobile = fields.Char("Customer Mobile")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        super(HelpdeskTicket, self)._onchange_partner_id()
        if self.partner_id:
            self.mobile = self.partner_id.mobile
