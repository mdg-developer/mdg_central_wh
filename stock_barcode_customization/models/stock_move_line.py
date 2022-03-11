# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import Counter

from odoo import _, api, fields, tools, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import OrderedSet
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    bigger_uom_qty_done = fields.Float('Bigger UOM Done', default=0.0, digits='Product Unit of Measure', copy=False)
    basic_uom_qty_done = fields.Float('Basic UOM Done', default=0.0, digits='Product Unit of Measure', copy=False)
    # product_purchase_uom_id = fields.Many2one(related='product_id.uom_po_id')

    bigger_uom_id = fields.Many2one('uom.uom', 'Unit of Measure',related='product_id.uom_po_id',domain="[('id', '=', product_purchase_category_id)]")
    bigger_category_id = fields.Many2one(related='product_id.uom_po_id')

    basic_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', related='product_id.uom_id',
                                    domain="[('id', '=', product_purchase_category_id)]")
    basic_category_id = fields.Many2one(related='product_id.uom_id')

    @api.onchange('product_id', 'bigger_uom_qty_done','basic_uom_qty_done','bigger_uom_id')
    def _onchange_product_id_uom(self):
        if self.product_id.uom_id:
            self.basic_uom_id = self.product_id.uom_id.id
        if self.product_id.uom_po_id:
            self.bigger_uom_id = self.product_id.uom_po_id.id
        if self.product_id and self.bigger_uom_id:
            other_uom_qty = 0.0
            if self.bigger_uom_id.uom_type == 'bigger':
                other_uom_qty = self.bigger_uom_qty_done * self.bigger_uom_id.factor_inv
            self.qty_done = other_uom_qty + self.basic_uom_qty_done
        if not self.product_id:
            self.basic_uom_id = False
            self.bigger_uom_qty_done =False
            self.basic_uom_qty_done = False
            self.qty_done = False
            self.bigger_uom_id = False

    @api.onchange('bigger_uom_qty_done')
    def _onchange_bigger_uom_qty_done(self):
        if self.bigger_uom_qty_done < 0:
            self.bigger_uom_qty_done = 0

    @api.onchange('basic_uom_qty_done')
    def _onchange_basic_uom_qty_done(self):
        if self.basic_uom_qty_done < 0:
            self.basic_uom_qty_done = 0

    @api.onchange('qty_done')
    def _onchange_qty_done(self):
        if self.qty_done < 0:
            self.qty_done = 0

