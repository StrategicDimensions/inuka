# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

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
        ], string='Purchase Type', default='it', states=READONLY_STATES)
