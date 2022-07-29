# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _

class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"


    to_replenish = fields.Char(compute='_compute_to_replenish',store=True)

    @api.depends('qty_on_hand','product_min_qty','product_id')
    def _compute_to_replenish(self):
        for record in self:
            on_hand = record.qty_on_hand
            min_qty = record.product_min_qty
            if on_hand <= min_qty:
                record.to_replenish = 'True'
            else:
                record.to_replenish = 'False'


    def stock_check(self):

        return {
            'name': _('Stock Check'),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban',
            'res_model': 'stock.quant',
            'target': 'new',
            'domain': [('product_id', '=', self.product_id.id)],
            'context': dict(
                search_default_internal_loc=1,
            ),

        }

