from odoo import _, api, fields, models

class ProductPrincipal(models.Model):
    _name = "product.principal"
    _description = "Product Principal"

    name = fields.Char(String="Name", required=True)
    sequence = fields.Integer(String="Sequence")
