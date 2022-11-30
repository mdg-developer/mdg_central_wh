# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operator = fields.Many2one('res.partner', string="Operator")
    gin_ref = fields.Char(string="GIN Ref")
    picking_type_sequence_code = fields.Char(related='picking_type_id.sequence_code')

    def _get_fields_stock_barcode(self):
        fields = super()._get_fields_stock_barcode()
        fields.append('picking_type_sequence_code')
        fields.append('operator')
        return fields