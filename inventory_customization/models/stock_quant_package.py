from odoo import api, fields, models, SUPERUSER_ID, _

class QuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Package id must be unique!')
    ]

    name = fields.Char(
        'Package Reference', copy=False, index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('stock.quant.package') or '')
