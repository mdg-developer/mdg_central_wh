# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api

class Location(models.Model):
    _inherit = 'stock.location'

    @api.model
    def _get_fields_stock_barcode(self):
        fields = super()._get_fields_stock_barcode()
        fields.append('hold')
        return fields