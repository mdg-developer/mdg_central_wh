from odoo import _, api, fields, models

class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"
    pickface_pcs_route = fields.Boolean("PICKFACE PCS Route")
    pickface_ctn_route = fields.Boolean("PICKFACE CA Route")

class Location(models.Model):
    _inherit = "stock.location"
    
    zone_id = fields.Many2one('zone', string="Zone")
    pick_face = fields.Boolean(
        string='Pick-Face',
        default=False,
    )
    product_id = fields.Many2one('product.product', string="Product")
    principal_id = fields.Many2one('product.principal', string='Product Principal', related='product_id.principal_id', readonly=True)
    categ_id = fields.Many2one('product.category', string='Product Category', related='product_id.categ_id',readonly=True)
    loose = fields.Boolean(
        string='Is a Loose Location?',
        default=False,
    )
    hold = fields.Boolean(
        string='Is a Hold Location?',
        default=False,
    )
    ship_to = fields.Boolean(
        string='Is a Ship to Location?',
        default=False,
    )