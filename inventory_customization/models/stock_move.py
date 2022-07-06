from odoo import _, api, fields, models



class StockMove(models.Model):
    _inherit = "stock.move"

    demand_bigger_qty = fields.Float('Demand Case', default=0.0, digits='Product Unit of Measure',
                              compute='_bigger_quantity_done_compute', store=True)
    bigger_uom_id = fields.Many2one(string='Bigger UOM', related='product_id.uom_po_id', store=True, index=True,
                                    copy=False)

    @api.depends('product_id')
    def _bigger_quantity_done_compute(self):

        for record in self:
            record.demand_bigger_qty = record.product_uom_qty / record.bigger_uom_id.factor_inv