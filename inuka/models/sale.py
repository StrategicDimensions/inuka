# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


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
        ('collect', 'Collect / No Shipping'),
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
    paid = fields.Boolean(readonly=True, copy=False)
    order_status = fields.Selection([
        ('new', 'New Order'),
        ('open', 'Open'),
        ('general', 'Snag General'),
        ('payment', 'Snag Payment Option'),
        ('unreadable', 'Snag Unreadable')
    ], string="Order Status", default="new", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    delivery_status = fields.Selection([
        ('to_deliver', 'To Deliver'),
        ('partially', 'Partially Delivered'),
        ('fully', 'Fully Delivered'),
    ], compute="_compute_delivery_status", string="Delivery Status", store=True)

    @api.depends('state', 'order_line', 'order_line.qty_delivered', 'order_line.product_uom_qty')
    def _compute_delivery_status(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('sale', 'done'):
                order.delivery_status = 'to_deliver'
                continue

            if any(float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) != 0 for line in order.order_line if line.qty_delivered):
                order.delivery_status = 'partially'
            elif all(float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 0 for line in order.order_line):
                order.delivery_status = 'fully'
            else:
                order.delivery_status = 'to_deliver'

    def _compute_reserve(self):
        ReservedFund = self.env['reserved.fund']
        for order in self:
            res_funds = self.env['reserved.fund'].search([('customer_id', '=', order.partner_id.id)])
            amount_reserve = sum([x.amount for x in res_funds])
            order.reserve = - (order.partner_id.credit - order.partner_id.debit) - amount_reserve

    @api.multi
    def dummy_redirect(self):
        return

    @api.multi
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        for order in self:
            order.write({'pv': order.total_pv, 'order_total': order.amount_total})
        self.action_unlink_reserved_fund()
        self.write({'paid': True})
        return True

    @api.multi
    def action_cancel(self):
        super(SaleOrder, self).action_cancel()
        self.action_unlink_reserved_fund()

    @api.multi
    def action_add_reserved_fund(self):
        ReservedFund = self.env['reserved.fund']
        for order in self:
            if order.reserve >= order.amount_total:
                ReservedFund.create({
                    'date': fields.Datetime.now(),
                    'desctiption': 'Reservation for %s for Order %s for an amount of %d by %s' % (order.partner_id.name, order.name, order.amount_total, order.user_id.name),
                    'amount': order.amount_total,
                    'order_id': order.id,
                    'customer_id': order.partner_id.id,
                })
                order.paid = True
                msg = "<b>Fund Reserved</b><ul>"
                msg += "<li>Reservation for %s <br/> for Order %s for an amount of <br/> %s %d by %s" % (order.partner_id.name, order.name, order.company_id.currency_id.symbol, order.amount_total, order.user_id.name)
                msg += "</ul>"
                order.message_post(body=msg)
            else:
                raise UserError(_('Insufficient Funds Available'))

    @api.multi
    def action_unlink_reserved_fund(self):
        ReservedFund = self.env['reserved.fund']
        for order in self:
            res_funds = ReservedFund.search([('order_id', '=', order.id)])
            # res_funds.unlink()
            res_funds.write({
                'active': False,
            })
            order.paid = False
            msg = "<b>Fund unreserved</b><ul>"
            msg += "<li>Reservation Reversed for %s <br/> for Order %s for an amount of <br/> %s %d by %s" % (order.partner_id.name, order.name, order.company_id.currency_id.symbol, order.amount_total, order.user_id.name)
            msg += "</ul>"
            order.message_post(body=msg)


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


class ReservedFund(models.Model):
    """Master should be added which will be used to reserve funds on a quotation"""
    _name = "reserved.fund"
    _description = "Reserved Fund"
    _rec_name = 'order_id'

    date = fields.Datetime(readonly=True, requied=True, default=lambda self: fields.Datetime.now())
    desctiption = fields.Char(readonly=True, requied=True)
    amount = fields.Float(readonly=True, requied=True)
    order_id = fields.Many2one('sale.order', readonly=True, requied=True)
    customer_id = fields.Many2one('res.partner', readonly=True, requied=True)
    active = fields.Boolean(default=True, readonly=True)
