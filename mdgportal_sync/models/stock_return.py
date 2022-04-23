from xmlrpc import client
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        result = super(StockPicking, self).button_validate()
        # Check if the stock picking transaction is coming from mdgportal ; assume that coming transaction start with
        # 'SRN' in Source Document
        if self.origin:
            if self.origin.startswith("SRN") and self.state == 'done':
                sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
                common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                srn_id = models.execute_kw(db, sd_uid, password, 'stock.return', 'search', [[['name', '=', self.origin]]],{'limit': 1})
                if srn_id:
                    for line in self.move_ids_without_package:
                        if line.quantity_done != 0:
                            change_sr_line_id = models.execute_kw(db, sd_uid, password, 'stock.return.line', 'search',[[['line_id', '=', srn_id[0]],['product_id.default_code','=',line.product_id.default_code]]],{'limit':1})
                            value ={
                                'actual_return_quantity':line.quantity_done
                            }
                            models.execute_kw(db, sd_uid, password, 'stock.return.line', 'write',[change_sr_line_id, value])

                    models.execute_kw(db, sd_uid, password, 'stock.return', 'received',srn_id)

        return result