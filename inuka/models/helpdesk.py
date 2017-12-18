# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    ticket_line = fields.One2many('helpdesk.ticket.line', 'ticket_id', string='Ticket Lines', copy=True)


class HelpdeskTicketLine(models.Model):
    _name = 'helpdesk.ticket.line'
    _description = 'Ticket Lines'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    qty_available = fields.Float("Quantity On Hand")
    virtual_available = fields.Float("Forecast Quantity")
    barcode = fields.Char("Barcode")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return {}
        self.name = self.product_id.name_get()[0][1]
        self.price_unit = self.product_id.lst_price
        self.barcode = self.product_id.barcode
        self.qty_available = self.product_id.qty_available
        self.virtual_available = self.product_id.virtual_available
