# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    product_ids = fields.Many2many('product.product', 'helpdesk_ticket_product_rel', 'ticket_id', 'product_id', string="Products")
