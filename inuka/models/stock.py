# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Picking(models.Model):
    _inherit = 'stock.picking'

    bulk_master_id = fields.Many2one("bulk.master", string="Bulk")
