# Copyright 2021 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProductBarcodeMulti(models.Model):
    _name = 'product.barcode.multi'
    _description = 'Product Barcode Multi'
    _barcode_field = 'name'

    name = fields.Char(
        'Barcode',
        required=True,
    )

    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        required=True,
        ondelete="cascade",
    )

    default_code = fields.Char('Internal Reference', related='product_id.default_code')
    tracking = fields.Selection(related='product_id.tracking')
    default_name = fields.Char('Internal Reference', related='product_id.display_name')
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', readonly=True)
    barcode = fields.Char('Barcode', related='product_id.barcode')



    @api.model
    def _get_fields_stock_barcode(self):
        return ['name', 'product_id', 'default_code', 'tracking', 'display_name', 'uom_id','barcode']


# return ['barcode', 'default_code', 'tracking', 'display_name', 'uom_id']
