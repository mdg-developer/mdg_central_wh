# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import UserError
from xmlrpc import client


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _apply_inventory(self):
        location = self.location_id
        product = self.product_id
        product_uom = self.product_uom_id.name
        counted_quantity = self.inventory_quantity
        diff_quantity = self.inventory_diff_quantity

        sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        cwh_location = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',[[['name', '=', 'MDGCWH2-Sellable'],['is_cwh_location', '=', True]]], {'limit': 1})
        inv_loss_location = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',[[['name', '=', 'Inventory loss']]], {'limit': 1})
        product_id_portal = models.execute_kw(db, sd_uid, password, 'product.product', 'search',[[['default_code', '=', product.default_code]]], {'limit': 1})
        product_uom_portal = models.execute_kw(db, sd_uid, password, 'product.uom', 'search', [[['name', '=', product_uom]]],{'limit':1})
        if cwh_location and product_id_portal:
            today = fields.Date.today()
            inventory_adjustment_name = str(today) + ":" + str(product.name)
            if (diff_quantity <0 ):
                stock_move_value = {
                    'name': product.name,
                    'product_id': product_id_portal[0],
                    'location_dest_id':inv_loss_location[0],
                    'location_id':cwh_location[0],
                    'product_uom_qty':abs(diff_quantity),
                    'product_uom':product_uom_portal[0],
                    'origin': inventory_adjustment_name,

                }
            else:
                stock_move_value = {
                    'name': product.name,
                    'product_id': product_id_portal[0],
                    'location_dest_id':cwh_location[0],
                    'location_id':inv_loss_location[0],
                    'product_uom_qty':abs(diff_quantity),
                    'product_uom':product_uom_portal[0],
                    'origin':inventory_adjustment_name,
                }
            stock_inventory_id = models.execute_kw(db, sd_uid, password, 'stock.move', 'create', [stock_move_value])
            return super(StockQuant, self)._apply_inventory()



