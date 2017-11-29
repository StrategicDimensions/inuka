# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BulkMaster(models.Model):
    _name = 'bulk.master'
    _description = 'Bulk Master'

    name = fields.Char(string="Reference")
    partner_id = fields.Many2one("res.partner", string="Member", required=True)
    member_id = fields.Char(related="partner_id.ref", string="Member ID", required=True)
    partner_shipping_id = fields.Many2one("res.partner", string="Delivery Address")
    bulk_type = fields.Selection([
        ('bulk', 'Bulk'),
        ('consolidated', 'Consolidated')
        ], string='Type', required=True)
    date = fields.Datetime("Date", readonly=True, required=True, default=fields.Datetime.now())
    schedule_date = fields.Datetime("Scheduled Date")
    user_id = fields.Many2one("res.users", string="Managed By", required=True, default=lambda self: self.env.uid)
    product_total = fields.Float(compute="_compute_order_totals", string="Products Total")
    shipping_total = fields.Float(compute="_compute_order_totals", string="Shipping Total")
    unpaid_total = fields.Float(compute="_compute_order_totals", string="Unpaid Amount")
    pv_total = fields.Float(compute="_compute_order_totals", string="Total PV")
    waybill = fields.Char("Waybill")
    carrier_id = fields.Many2one("delivery.carrier", string="Dispatch Method", required=True)
    unpaid_pv = fields.Float(compute="_compute_order_totals", string="Unpaid PV")
    bulk_lock = fields.Boolean("Bulk Lock", readonly=True)
    pack_lock = fields.Boolean("Pack Lock", readonly=True)
    description = fields.Text("Comment")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
        ], string='Status', default='draft')
    sale_orders = fields.Many2many('sale.order', 'bulk_master_sale_order_rel', 'bulk_master_id', 'sale_order_id', string="Orders")
    sale_order_count = fields.Integer(compute="_compute_sale_order_count", string="Sale Orders")
    delivery_count = fields.Integer(compute='_compute_picking_ids', string='Delivery Orders')

    def _compute_order_totals(self):
        for bulk in self:
            product_total = shipping_total = unpaid_total = pv_total = unpaid_pv = 0.0
            for order in bulk.sale_orders:
                product_total += order.product_cost
                shipping_total += order.shipping_cost
                pv_total += order.total_pv
                if not order.paid:
                    unpaid_total += order.product_cost
                    unpaid_pv += order.total_pv
            bulk.product_total = product_total
            bulk.shipping_total = shipping_total
            bulk.unpaid_total = unpaid_total
            bulk.pv_total = pv_total
            bulk.unpaid_pv = unpaid_pv

    def _compute_sale_order_count(self):
        for bulk in self:
            bulk.sale_order_count = len(bulk.sale_orders)

    def _compute_picking_ids(self):
        for bulk in self:
            count = 0
            for order in bulk.sale_orders:
                count += len(order.picking_ids)
            bulk.delivery_count = count

    @api.model
    def create(self, vals):
        vals['name'] = self.env.ref('inuka.seq_bulk_master').next_by_id()
        return super(BulkMaster, self).create(vals)

    @api.multi
    def view_sale_orders(self):
        self.ensure_one()
        orders = self.mapped('sale_orders')
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = [('id', 'in', orders.ids)]
        return action

    @api.multi
    def view_delivery_orders(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        pickings = self.sale_orders.mapped('picking_ids')
        action['domain'] = [('id', 'in', pickings.ids)]
        return action
