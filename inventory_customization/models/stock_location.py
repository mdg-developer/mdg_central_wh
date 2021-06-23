from odoo import _, api, fields, models

class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"
    pickface_pcs_route = fields.Boolean("PICKFACE PCS Route")

class Location(models.Model):
    _inherit = "stock.location"
    
    zone_id = fields.Many2one('zone', string="Zone")
    pick_face = fields.Boolean(
        string='Pick-Face',
        default=False,
    )
    product_id = fields.Many2one('product.product', string="Product")
    loose = fields.Boolean(
        string='Is a Loose Location?',
        default=False,
    )