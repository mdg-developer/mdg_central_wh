# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import http, _
from odoo.http import request
from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController



class StockBarcodeProductBarcodeMultipleController(StockBarcodeController):

    def _try_open_product_location(self, barcode):

        """ If barcode represent a product, open a list/kanban view to show all
        the locations of this product.
        """
        product_barcode = request.env['product.product'].search_read([('barcode', '=', barcode),], ['id', 'display_name'], limit=1)
        if product_barcode:
            tree_view_id = request.env.ref('stock.view_stock_quant_tree').id
            kanban_view_id = request.env.ref('stock_barcode.stock_quant_barcode_kanban_2').id
            return {
                'action': {
                    'name': product_barcode[0]['display_name'],
                    'res_model': 'stock.quant',
                    'views': [(tree_view_id, 'list'), (kanban_view_id, 'kanban')],
                    'type': 'ir.actions.act_window',
                    'domain': [('product_id', '=', product_barcode[0]['id'])],
                    'context': {
                        'search_default_internal_loc': True,
                    },
                }
            }
        product_barcode_multi = request.env['product.barcode.multi'].search([('name', '=', barcode)],limit=1)
        if product_barcode_multi:
            product_id = product_barcode_multi.product_id.id
            result = request.env['product.product'].search_read([('id', '=', product_id),], ['id', 'display_name'], limit=1)
            tree_view_id = request.env.ref('stock.view_stock_quant_tree').id
            kanban_view_id = request.env.ref('stock_barcode.stock_quant_barcode_kanban_2').id
            return {
                'action': {
                    'name': result[0]['display_name'],
                    'res_model': 'stock.quant',
                    'views': [(tree_view_id, 'list'), (kanban_view_id, 'kanban')],
                    'type': 'ir.actions.act_window',
                    'domain': [('product_id', '=', result[0]['id'])],
                    'context': {
                        'search_default_internal_loc': True,
                    },
                }
            }
