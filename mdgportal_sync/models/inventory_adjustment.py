# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import UserError
from xmlrpc import client


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _apply_inventory(self):

        # result = super(StockQuant, self)._apply_inventory()
        location = self.location_id
        product = self.product_id
        product_uom = self.product_uom_id
        counted_quantity = self.inventory_quantity

        sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        cwh_location = models.execute_kw(db, sd_uid, password, 'stock.location', 'search',[[['name', '=', location.name],['is_cwh_location', '=', True]]], {'limit': 1})
        product_id_portal = models.execute_kw(db, sd_uid, password, 'product.product', 'search',[[['default_code', '=', product.default_code]]], {'limit': 1})
        if cwh_location and product_id_portal:
            today = fields.Date.today()
            inventory_adjustment_name = str(today)+":"+str(product.name)
            stock_inventory_value = {
                'name': inventory_adjustment_name,
                'location_id':cwh_location[0],
                'filter':'partial',
            }
            stock_inventory_id = models.execute_kw(db, sd_uid, password, 'stock.inventory', 'create', [stock_inventory_value])
            models.execute_kw(db, sd_uid, password, 'stock.inventory', 'prepare_inventory', [stock_inventory_id])




            stock_inventory_lines = {
                'inventory_id':stock_inventory_id,
                'product_id':product_id_portal[0],
                # 'product_uom_id':uom_id,
                'location_id':cwh_location[0],
                'product_qty':counted_quantity,
            }

            models.execute_kw(db, sd_uid, password, 'stock.inventory.line', 'create', [stock_inventory_lines])
            return super(StockQuant, self)._apply_inventory()



