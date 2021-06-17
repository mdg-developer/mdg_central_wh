from odoo import api, fields, models, tools, _

class ProductPackaging(models.Model):
    _inherit = "product.packaging"
    
    pallet_quantity = fields.Float(string='Pallet Quantity')