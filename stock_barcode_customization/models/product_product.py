# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields

class Product(models.Model):
    _inherit = 'product.product'

    product_name = fields.Char(related='product_tmpl_id.default_code')

    # @api.depends('product_tmpl_id')
    # def _compute_product_name(self):
    #     import pdb
    #     pdb.set_trace()
    #     for record in self:
    #         if record.product_tmpl_id:
    #             record.product_name = record.product_tmpl_id.name

