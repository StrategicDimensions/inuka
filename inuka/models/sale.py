# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line','order_line.pv')
    def _compute_tot_pv(self):
        for order in self:
            tot_pvs = 0.0
            for line in order.order_line:
                tot_pvs += line.pv
            order.total_pv = tot_pvs

    order_sent_by = fields.Selection([
        ('email', 'Email'),
        ('facebook', 'Facebook'),
        ('fax',' Fax'),
        ('inuka', 'Inuka'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('whatsapp', 'Whatsapp'),
        ('portal', 'Portal')],
        string="Order Sent By", default="email", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    order_type = fields.Selection([
        ('collect', 'Collect / No Shopping'),
        ('bulk', 'Part of Bulk'),
        ('single', 'Single'),
        ('upfront', 'Upfront'),
        ('stock', 'Stock (for Up front)')],
        string='Order Type', default="collect", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    sale_date = fields.Date('Sale Date', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    order_total = fields.Float('Order Total', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    product_cost = fields.Float('Product Cost', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    shipping_cost = fields.Float('Shipping Cost', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    pv = fields.Float('PV', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    total_pv = fields.Float(compute='_compute_tot_pv', store=True)
    reserve = fields.Monetary(string='Available Funds', compute="_compute_reserve")

    def _compute_reserve(self):
        for order in self:
            order.reserve = - (order.partner_id.credit - order.partner_id.debit)

    @api.multi
    def dummy_redirect(self):
        return

    @api.multi
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        for order in self:
            order.write({'pv': order.total_pv, 'order_total': order.amount_total})
        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pv = fields.Float("PV's")

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()
        self.pv = self.product_id.categ_id.category_pv * self.product_uom_qty

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        self.pv = self.product_id.categ_id.category_pv * self.product_uom_qty


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(default='delivered')
