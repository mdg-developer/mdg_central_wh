from odoo import api, fields, models, SUPERUSER_ID, _

class QuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Package id must be unique!')
    ]

    name = fields.Char(
        'Package Reference', copy=False, index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('stock.quant.package') or '')

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        res = super(StockQuant,self)._get_inventory_fields_create()
        res += ['inventory_quantity']
        return res