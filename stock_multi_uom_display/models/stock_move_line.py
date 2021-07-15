from odoo import _, api, fields, models

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    bigger_qty = fields.Float('Bigger Qty', default=0.0, digits='Product Unit of Measure', compute='_compute_bigger_qty',store=True, copy=False)
    bigger_uom_id = fields.Many2one(string='Bigger UOM',related='product_id.uom_po_id', store=True, index=True, copy=False)
    
    @api.depends('qty_done')
    def _compute_bigger_qty(self):
        for line in self:
            if line.product_uom_id:
                if line.product_uom_id != line.bigger_uom_id and line.qty_done != 0:
                    uom_qty = 1 / line.bigger_uom_id.factor
                    bigger_qty = round(line.qty_done / uom_qty, 2)
                    line.bigger_qty = bigger_qty
                else:
                    line.bigger_qty = line.qty_done
            
#     @api.onchange('qty_done', 'product_uom_id')
#     def _onchange_qty_done(self):
#         """ When the user is encoding a move line for a tracked product, we apply some logic to
#         help him. This onchange will warn him if he set `qty_done` to a non-supported value.
#         """
#         res = {}
#         if self.product_uom_id:
#             if self.product_uom_id != self.bigger_uom_id and self.qty_done != 0:
#                 uom_qty = 1 / self.bigger_uom_id.factor
#                 bigger_qty = round(self.qty_done / uom_qty, 2)
#                 self.bigger_qty = bigger_qty
#             else:
#                 self.bigger_qty = self.qty_done
#                 
#         if self.qty_done and self.product_id.tracking == 'serial':
#             qty_done = self.product_uom_id._compute_quantity(self.qty_done, self.product_id.uom_id)
#             if float_compare(qty_done, 1.0, precision_rounding=self.product_id.uom_id.rounding) != 0:
#                 message = _('You can only process 1.0 %s of products with unique serial number.', self.product_id.uom_id.name)
#                 res['warning'] = {'title': _('Warning'), 'message': message}
#         return res