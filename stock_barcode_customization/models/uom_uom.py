# -*- coding: utf-8 -*-

from odoo import models, api


class UoM(models.Model):
    _inherit = 'uom.uom'

    @api.model
    def _get_fields_stock_barcode(self):
        fields = super()._get_fields_stock_barcode()
        fields.append('factor_inv')
        return fields
