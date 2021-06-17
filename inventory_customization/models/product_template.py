from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    pallet_quantity = fields.Float(string='Pallet Quantity')
    ti_x_hi = fields.Char(string='TI x HI')
    