from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.tools import html2plaintext, is_html_empty


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_stock_barcode_data(self):
        data = super(StockPicking, self)._get_stock_barcode_data()
        move_lines = self.move_line_ids
        products = move_lines.product_id
        product_barcode_multi = products.barcode_ids

        data['records'].update({
            "product.barcode.multi": product_barcode_multi.read(product_barcode_multi._get_fields_stock_barcode(), load=False),
        })
        return data