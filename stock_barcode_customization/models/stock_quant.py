# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.osv import expression
from datetime import timedelta, date


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    expiry_date = fields.Date(related='lot_id.expiration_date', store=True, readonly=False)
    principal_id = fields.Char(related='product_tmpl_id.principal_id.name', string='Principal')
    default_code = fields.Char(related='product_tmpl_id.default_code', string='SKU')
    display_name = fields.Char(related='product_tmpl_id.name', string='Short Code')

    @api.model
    def _get_removal_strategy_order(self, removal_strategy):

        if removal_strategy == 'fifo':
            return 'in_date ASC, id'
        elif removal_strategy == 'lifo':
            return 'in_date DESC, id DESC'
        elif removal_strategy == 'closest':
            return 'location_id ASC, id DESC'
        elif removal_strategy == 'fefo':
            return 'expiry_date, in_date, id'
        raise UserError(_('Removal strategy %s not implemented.') % (removal_strategy,))

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):

        removal_strategy = self._get_removal_strategy(product_id, location_id)
        removal_strategy_order = self._get_removal_strategy_order(removal_strategy)
        shelf_life = 0
        if self.env.context.get('active_model') == 'sale.order':
            sale_order = self.env.context.get('active_id')
            shelf_life = self.env['sale.order'].browse(sale_order).shelf_life


        domain = [('product_id', '=', product_id.id)]
        if not strict:
            if lot_id:
                domain = expression.AND([[('lot_id', '=', lot_id.id)], domain])
            if package_id:
                domain = expression.AND([[('package_id', '=', package_id.id)], domain])
            if owner_id:
                domain = expression.AND([[('owner_id', '=', owner_id.id)], domain])
            if shelf_life:
                tempDate = date.today() + timedelta(days=int(shelf_life))
                domain = expression.AND([[('expiry_date', '>', tempDate)], domain])
            domain = expression.AND([[('location_id', 'child_of', location_id.id)], domain])
        else:
            domain = expression.AND([[('lot_id', '=', lot_id and lot_id.id or False)], domain])
            domain = expression.AND([[('package_id', '=', package_id and package_id.id or False)], domain])
            domain = expression.AND([[('owner_id', '=', owner_id and owner_id.id or False)], domain])
            domain = expression.AND([[('location_id', '=', location_id.id)], domain])

        return self.search(domain, order=removal_strategy_order)

    def int_transfer(self):
        barcode = "CWHB-INTERNAL"

        picking_type = self.env['stock.picking.type'].search([('barcode', '=', barcode),], limit=1)
        if picking_type:
            picking = self.env['stock.picking']._create_new_picking(picking_type)
            picking.update({
                'location_id':self.location_id
            })
            return picking._get_client_action()['action']
