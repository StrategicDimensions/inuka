# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    purchase_type = fields.Selection([
        ('it', 'IT'),
        ('​stationery', '​Stationery'),
        ('warehouse​', 'Warehouse​ supplies (stock)'),
        ('furniture', 'Furniture'),
        ('repairs', 'Repairs'),
        ('services​', 'Services​ (Training​ etc)'),
        ('rental​', 'Rental​ (Car​ park​ etc)'),
        ('stock', 'Stock'),
        ('marketing​', 'Marketing​ ​ Material')
        ], string='Purchase Type', default='it', readonly=True, states={'draft': [('readonly', False)]})
    total_pv = fields.Float(compute='_compute_tot_pv', store=True)
    payment_reference = fields.Char("Payment Reference", states={'draft': [('readonly', False)]})

    @api.depends('invoice_line_ids','invoice_line_ids.pv')
    def _compute_tot_pv(self):
        for invoice in self:
            tot_pvs = 0.0
            for line in invoice.invoice_line_ids:
                tot_pvs += line.pv
            invoice.total_pv = tot_pvs

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        self.purchase_type = self.purchase_id.purchase_type
        self.payment_reference = self.purchase_id.payment_reference
        super(AccountInvoice, self).purchase_order_change()

    @api.multi
    def action_invoice_open(self):
        context = dict(self.env.context or {})
        for invoice in self:
            purchase_ids = invoice.invoice_line_ids.mapped('purchase_id')
            total = sum(purchase_ids.mapped('amount_total'))
            if purchase_ids and invoice.amount_total != total:
                context['active_id'] = invoice.id
                return {
                    'name': _('Warning'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice.validate',
                    'type': 'ir.actions.act_window',
                    'context': context,
                    'target': 'new'
                }
        return super(AccountInvoice, self).action_invoice_open()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    pv = fields.Float("PV's")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(AccountInvoiceLine, self)._onchange_product_id()
        self.pv = self.product_id.categ_id.category_pv * self.quantity

    @api.onchange('quantity')
    def _onchange_quantity(self):
        self.pv = self.product_id.categ_id.category_pv * self.quantity

    def _set_additional_fields(self, invoice):
        self.pv = self.product_id.categ_id.category_pv * self.quantity
        super(AccountInvoiceLine, self)._set_additional_fields(invoice)
