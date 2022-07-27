from xmlrpc import client
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        result = super(StockPicking, self).button_validate()
        if self.picking_type_id.code == "outgoing" and self.state == 'done' and self.origin.startswith("GIN"):
            gin_id_wms = self.env['good.issue.note'].search([('name', '=', self.origin)], limit=1)
            if gin_id_wms:
                sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
                models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                user = self.env['res.users'].browse(self.env.uid)
                gin_name = gin_id_wms.gin_ref

                gin_id = models.execute_kw(db, sd_uid, password, 'good.issue.note', 'search',
                                            [[['name', '=', gin_name]]], {'limit': 1})
                if gin_id:
                    uid_value = {
                        'issue_by': user.name,
                        'receiver': user.name,
                    }
                    models.execute_kw(db, sd_uid, password, 'good.issue.note', 'write',
                                      [gin_id, uid_value])
                    for line in self.move_ids_without_package:
                        change_gin_line_id = models.execute_kw(db, sd_uid, password, 'good.issue.note.line','search', [[['line_id', '=', gin_id[0]],['product_id.default_code', '=',line.product_id.default_code],['product_uom.name', '=',line.product_uom.name]]], {'limit': 1})

                        value = {
                            'issue_quantity': line.quantity_done
                        }
                        models.execute_kw(db, sd_uid, password, 'good.issue.note.line', 'write',
                                          [change_gin_line_id, value])
                        # gin_line_obj = self.env['good.issue.note.line'].search(
                        #     [('gin_id', '=', gin_id_wms.id), ('product_id', '=', line.product_id.id),
                        #      ('total_req_qty', '=', line.product_uom_qty)])

                        gin_line_obj = self.env['good.issue.note.line'].search(
                            [('gin_id', '=', gin_id_wms.id), ('product_id', '=', line.product_id.id)])


                        if gin_line_obj:
                            if gin_line_obj.product_uom_id.name == line.product_uom.name:
                                gin_line_obj.update({
                                    'qty': line.quantity_done
                                })
                            else:
                                factor = gin_line_obj.product_uom_id.factor_inv
                                gin_line_obj.update({
                                    'qty': (line.quantity_done / factor)
                                })
                        # gin_line_obj.update({
                        #         'qty':line.quantity_done
                        # })
                    models.execute_kw(db, sd_uid, password, 'good.issue.note', 'issue', [gin_id])
                    gin_id_wms.action_issue()

