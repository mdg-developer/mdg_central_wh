from odoo import _, api, fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    def button_confirm(self):
        result = super(PurchaseOrder, self).button_confirm()
        picking = self.env['stock.picking'].search([('purchase_id', '=', self.id),('name', 'ilike', 'IN')])
        if picking:
            for line in picking.move_line_ids_without_package:
                if not line.lot_name:
                    lot_name = self.env['ir.sequence'].next_by_code('stock.lot.serial')
                    line.write({'lot_name': lot_name})
        return result