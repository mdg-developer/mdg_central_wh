from odoo import _, api, Command, fields, models

class StockMove(models.Model):
    _inherit = "stock.move"

    product_name = fields.Char('Product SKU',related="product_id.product_tmpl_id.name")
    default_code = fields.Char('Product Code',related="product_id.product_tmpl_id.default_code")


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    product_name = fields.Char('Product SKU', related="product_id.product_tmpl_id.name")
    default_code = fields.Char('Product Code', related="product_id.product_tmpl_id.default_code")

