from xmlrpc import client
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        result = super(StockPicking, self).button_validate()
        backorder = self.env['stock.picking'].search([('sale_id', '=', self.sale_id.id),('backorder_id', '=', self.id )])
        if self.picking_type_id.code == "outgoing" and self.state == 'done':
            if not self.backorder_id and not backorder and not self.gin_ref:
                sale_order_id = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
                if sale_order_id.origin:
                    if sale_order_id.origin.startswith("BRFI"):
                        sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
                        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                        brfi_name = sale_order_id.origin


                        bgin_id = models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'search',
                                                   [[['request_id.name', '=', brfi_name],['state', '=', 'approve']]], {'limit': 1})
                        if bgin_id:
                            # models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'approve', [bgin_id])
                            for line in sale_order_id.order_line:
                                flag_qty_delivered = 0
                                # BGIN Issue Syncing
                                same_prod = self.env['sale.order.line'].search([('product_id', '=', line.product_id.id), ('order_id', '=', sale_order_id.id),
                                     ('loose', '=', line.loose)])
                                for flag in same_prod:
                                    flag_qty_delivered += flag.qty_delivered

                                # BGIN Issue Syncing
                                change_bgin_line_id = models.execute_kw(db, sd_uid, password, 'branch.good.issue.note.line','search', [[['line_id', '=', bgin_id[0]],['product_id.default_code', '=',line.product_id.default_code],['product_uom.name','=',line.product_uom.name]]],{'limit' :1})
                                if flag_qty_delivered != 0:
                                    value = {
                                        'issue_quantity': flag_qty_delivered
                                    }
                                else:
                                    value = {
                                        'issue_quantity': line.qty_delivered
                                    }
                                models.execute_kw(db, sd_uid, password, 'branch.good.issue.note.line', 'write',[change_bgin_line_id, value])
                            models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'issue', [bgin_id])

            elif backorder and not self.backorder_id and not self.gin_ref:
                sale_order_id = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
                if sale_order_id.origin:
                    if sale_order_id.origin.startswith("BRFI"):
                        sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
                        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                        brfi_name = sale_order_id.origin

                        brfi_id = models.execute_kw(db, sd_uid, password, 'branch.stock.requisition', 'search',
                                                    [[['name', '=', brfi_name]]], {'limit': 1})
                        bgin_id = models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'search',
                                                    [[['request_id.name', '=', brfi_name],['state', '=', 'approve']]], {'limit': 1})
                        if bgin_id:
                            # models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'set_issue_qty_zero', [bgin_id])
                            for line in sale_order_id.order_line:
                                flag_qty_delivered = 0
                                # BGIN Issue Syncing
                                same_prod = self.env['sale.order.line'].search([('product_id', '=', line.product_id.id), ('order_id', '=', sale_order_id.id),
                                     ('loose', '=', line.loose)])
                                for flag in same_prod:
                                    flag_qty_delivered += flag.qty_delivered

                                # BGIN Issue Syncing
                                change_bgin_line_id = models.execute_kw(db, sd_uid, password, 'branch.good.issue.note.line','search', [[['line_id', '=', bgin_id[0]],['product_id.default_code', '=',line.product_id.default_code],['product_uom.name','=',line.product_uom.name]]],{'limit' :1})
                                if flag_qty_delivered != 0:
                                    value = {
                                        'issue_quantity': flag_qty_delivered
                                    }
                                else:
                                    value = {
                                        'issue_quantity': line.qty_delivered
                                    }
                                models.execute_kw(db, sd_uid, password, 'branch.good.issue.note.line', 'write',[change_bgin_line_id, value])
                            models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'issue', [bgin_id])
                            gin_id = models.execute_kw(db, sd_uid, password, 'branch.stock.requisition', 'create_gin', [brfi_id])
                            backorder.write({'gin_ref': gin_id})

            elif backorder and self.gin_ref:
                sale_order_id = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
                if sale_order_id.origin:
                    if sale_order_id.origin.startswith("BRFI"):
                        sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
                        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                        brfi_name = sale_order_id.origin

                        brfi_id = models.execute_kw(db, sd_uid, password, 'branch.stock.requisition', 'search',
                                                    [[['name', '=', brfi_name]]], {'limit': 1})
                        bgin_id = models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'search',
                                                    [[['request_id.name', '=', brfi_name],['state', '=', 'approve']]], {'limit': 1})
                        if bgin_id:
                            # models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'set_issue_qty_zero',
                            #                   [bgin_id])
                            for line in sale_order_id.order_line:
                                flag_qty_delivered = 0
                                # BGIN Issue Syncing
                                same_prod = self.env['sale.order.line'].search([('product_id', '=', line.product_id.id), ('order_id', '=', sale_order_id.id),
                                     ('loose', '=', line.loose)])
                                for flag in same_prod:
                                    flag_qty_delivered += flag.qty_delivered

                                # BGIN Issue Syncing
                                change_bgin_line_id = models.execute_kw(db, sd_uid, password, 'branch.good.issue.note.line','search', [[['line_id', '=', bgin_id[0]],['product_id.default_code', '=',line.product_id.default_code],['product_uom.name','=',line.product_uom.name]]],{'limit' :1})
                                if flag_qty_delivered != 0:
                                    value = {
                                        'issue_quantity': flag_qty_delivered
                                    }
                                else:
                                    value = {
                                        'issue_quantity': line.qty_delivered
                                    }
                                models.execute_kw(db, sd_uid, password, 'branch.good.issue.note.line', 'write',[change_bgin_line_id, value])
                            models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'issue', [bgin_id])
                            gin_id = models.execute_kw(db, sd_uid, password, 'branch.stock.requisition', 'create_gin', [brfi_id])
                            backorder.write({'gin_ref': gin_id})

            elif not backorder and self.gin_ref:
                sale_order_id = self.env['sale.order'].search([('name', '=', self.origin)], limit=1)
                if sale_order_id.origin:
                    if sale_order_id.origin.startswith("BRFI"):
                        sd_uid, url, db, password = self.env['cwh.connection'].get_connection_data()
                        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                        brfi_name = sale_order_id.origin

                        brfi_id = models.execute_kw(db, sd_uid, password, 'branch.stock.requisition', 'search',
                                                    [[['name', '=', brfi_name]]], {'limit': 1})
                        bgin_id = models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'search',
                                                    [[['request_id.name', '=', brfi_name],['state', '=', 'approve']]], {'limit': 1})
                        if bgin_id:
                            # models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'set_issue_qty_zero',
                            #                   [bgin_id])
                            for line in sale_order_id.order_line:
                                flag_qty_delivered = 0
                                # BGIN Issue Syncing
                                same_prod = self.env['sale.order.line'].search([('product_id', '=', line.product_id.id), ('order_id', '=', sale_order_id.id),
                                     ('loose', '=', line.loose)])
                                for flag in same_prod:
                                    flag_qty_delivered += flag.qty_delivered

                                # BGIN Issue Syncing
                                change_bgin_line_id = models.execute_kw(db, sd_uid, password, 'branch.good.issue.note.line','search', [[['line_id', '=', bgin_id[0]],['product_id.default_code', '=',line.product_id.default_code],['product_uom.name','=',line.product_uom.name]]],{'limit' :1})
                                if flag_qty_delivered != 0:
                                    value = {
                                        'issue_quantity': flag_qty_delivered
                                    }
                                else:
                                    value = {
                                        'issue_quantity': line.qty_delivered
                                    }
                                models.execute_kw(db, sd_uid, password, 'branch.good.issue.note.line', 'write',[change_bgin_line_id, value])
                            models.execute_kw(db, sd_uid, password, 'branch.good.issue.note', 'issue', [bgin_id])

            else:
                return result





        return result
