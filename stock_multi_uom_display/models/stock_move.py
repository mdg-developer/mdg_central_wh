from odoo import _, api, fields, models
from collections import defaultdict

class StockMove(models.Model):
    _inherit = "stock.move"
    
    bigger_qty = fields.Float('Bigger Qty', default=0.0, digits='Product Unit of Measure', compute='_bigger_quantity_done_compute', copy=False)
    bigger_uom_id = fields.Many2one(string='Bigger UOM',related='product_id.uom_po_id', store=True, index=True, copy=False)
    
    @api.depends('quantity_done')
    def _bigger_quantity_done_compute(self):
        """ This field represents the sum of the move lines `qty_done`. It allows the user to know
        if there is still work to do.

        We take care of rounding this value at the general decimal precision and not the rounding
        of the move's UOM to make sure this value is really close to the real sum, because this
        field will be used in `_action_done` in order to know if the move will need a backorder or
        an extra move.
        """
        if not any(self._ids):
            # onchange
            for move in self:
                quantity_done = 0
                bigger_qty = 0
                for move_line in move._get_move_lines():
                    quantity_done += move_line.product_uom_id._compute_quantity(
                        move_line.qty_done, move.product_uom, round=False)
                    bigger_qty = move_line.bigger_qty
                move.quantity_done = quantity_done
                move.bigger_qty = bigger_qty
        else:
            # compute
            bigger_qty = 0
            move_lines = self.env['stock.move.line']
            for move in self:
                move_lines |= move._get_move_lines()

            data = self.env['stock.move.line'].read_group(
                [('id', 'in', move_lines.ids)],
                ['move_id', 'product_uom_id', 'bigger_qty'], ['move_id', 'product_uom_id'],
                lazy=False
            )            
            print("data>>>>",data)
            rec = defaultdict(list)
            for d in data:
                rec[d['move_id'][0]] += [(d['product_uom_id'][0], d['bigger_qty'])]

            for move in self:
                uom = move.product_uom
                move.bigger_qty = sum(
                    qty
                    for line_uom_id, qty in rec.get(move.ids[0] if move.ids else move.id, [])
                )
                