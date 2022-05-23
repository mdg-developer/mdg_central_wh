from odoo import _, api, fields, models

class ProductPrinciple(models.Model):
    _name = "product.principle"
    _description = "Product Principle"

    name = fields.Char(String="Name", required=True)
    sequence = fields.Integer(String="Sequence")
