from odoo import _, api, fields, models
import math

class StockPicking(models.Model):
    _inherit = "stock.picking"

    # @api.model
    # def create(self, vals):
    #     res = super(StockPicking, self).create(vals)
    #     print(res)
    #     return res

    def split_operation_lines(self):
        for line in self.move_ids_without_package:
            if line.product_id.product_tmpl_id.pallet_quantity > 0:
                putaway_location = None
                existing_locations=[]
                divisor =  math.ceil(line.product_uom_qty / line.product_id.product_tmpl_id.pallet_quantity)
                allocated_qty = 0
                for counter in range(0, int(divisor)):     
                    if counter+1 < int(divisor):
                        quantity = line.product_id.product_tmpl_id.pallet_quantity
                    else:
                        quantity = line.product_uom_qty - allocated_qty
                    if counter == 0:
                        existing_move_line = self.env['stock.move.line'].search([('picking_id', '=', self.id),('product_id', '=', line.product_id.id)])
                        if existing_move_line:                            
                            lot_name = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                            existing_move_line.write({
                                                        'qty_done': quantity,
                                                        'lot_name': lot_name,
                                                    })                            
                            allocated_qty = allocated_qty + quantity
                            location_dest_id = existing_move_line.location_dest_id.id
                            existing_locations.append(location_dest_id)
                    else:
                        putaway_rules = line.location_dest_id.putaway_rule_ids.filtered(lambda x: x.product_id == line.product_id)
                        if putaway_rules:
                            putaway_location = putaway_rules[0].location_out_id
                            for rule in putaway_rules:
                                records = self.env['stock.quant'].search([('location_id','=',rule.location_out_id.id),('product_id','=',line.product_id.id)])
                                existed  = rule.location_out_id.exist_location(rule.location_out_id,existing_locations)
                                if  existed == False and len(records) == 0:                        
                                    putaway_location = rule.location_out_id
                                    existing_locations.append(putaway_location)
                                    break
                                else:
                                    continue
                        lot_value = {                                        
                                        'product_id': line.product_id.id,
                                        'company_id': line.company_id.id,
                                    }
                        product_lot = self.env['stock.production.lot'].create(lot_value)
                        values = {
                                    'picking_id': self.id,
                                    'product_id': line.product_id.id,
                                    'qty_done': quantity,
                                    'product_uom_id': line.product_uom.id,
                                    'location_id': line.location_id.id,
                                    'location_dest_id': putaway_location.id if putaway_location else None,
                                    'lot_id': product_lot.id,                                    
                                }
                        self.env['stock.move.line'].create(values)
                        allocated_qty = allocated_qty + quantity
                        
    def button_validate(self):
        
        result = super(StockPicking, self).button_validate()
        if self.picking_type_id.sequence_code == 'IN': 
            picking = self.env['stock.picking'].search([('origin', '=', self.origin),('name', 'ilike', 'INT')])
            if picking:
                picking.split_operation_lines()
        return result
        
                    