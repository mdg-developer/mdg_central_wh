from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    pallet_quantity = fields.Float(string='Pallet Quantity')
    ti_x_hi = fields.Char(string='TI x HI')
    ti = fields.Integer(string='TI')
    hi = fields.Integer(string='HI')
    viss = fields.Float(string='Viss',default=0.0000)
    cbm = fields.Float(string='CBM',default=0.0000)
    principal_id = fields.Many2one(
        'product.principal', 'Product Principal',help="Select principal for the current product")



class Picking(models.Model):
    _inherit = "stock.picking"

    container = fields.Char(string="Container Number")

    def button_validate(self):

        internal = self.env['stock.picking'].search([('picking_type_code', '=', 'internal'), ('origin', '=', self.origin)],limit=1)
        if self.container and internal:

            if internal:
                internal.update({
                    'container':self.container
                })
        return super(Picking, self).button_validate()

class SaleOrder(models.Model):
    _inherit = "sale.order"

    ship_to_code = fields.Char(string="Ship To Code")
    shelf_life = fields.Float(String="Shelf Life")




