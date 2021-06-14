from odoo import _, api, fields, models
import math

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    def split_operation_lines(self):
        
        for line in self.move_ids_without_package:
            if line.product_id.product_tmpl_id.pallet_quantity > 0:
                divisor =  math.ceil(line.product_uom_qty / line.product_id.product_tmpl_id.pallet_quantity)
                allocated_qty = 0
                for counter in range(0, int(divisor)):     
                    if counter+1 < int(divisor):
                        quantity = line.product_id.product_tmpl_id.pallet_quantity
                    else:
                        quantity = line.product_uom_qty - allocated_qty
                    if counter == 0:
                        existing_move_line = self.env['stock.move.line'].search([('picking_id', '=', self.id)])
                        if existing_move_line:
                            existing_move_line.write({'qty_done': quantity})
                            allocated_qty = allocated_qty + quantity
                    else:
                        values = {
                                    'picking_id': self.id,
                                    'product_id': line.product_id.id,
                                    'qty_done': quantity,
                                    'product_uom_id': line.product_uom.id,
                                    'location_id': line.location_id.id,
                                    'location_dest_id': line.location_dest_id.id,
                                }
                        self.env['stock.move.line'].create(values)
                        allocated_qty = allocated_qty + quantity
                    