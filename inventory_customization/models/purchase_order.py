from odoo import _, api, fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    def button_confirm(self):
        result = super(PurchaseOrder, self).button_confirm()
        picking = self.env['stock.picking'].search([('purchase_id', '=', self.id)])
        if picking:
            picking.split_operation_lines()
        return result
        