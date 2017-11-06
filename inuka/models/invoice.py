# -*- coding: utf-8 -*-

from odoo import api, fields, models


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
        ], string='Purchase Type', default='it')

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        self.purchase_type = self.purchase_id.purchase_type
        super(AccountInvoice, self).purchase_order_change()
