# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    expiration_date = fields.Date(string='Expiration Date', help='This is the date on which the goods with this Serial Number may'
                                                                 ' become dangerous and must not be consumed.')


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        if self.picking_type_id.sequence_code == 'INT':
            for flag in self.move_line_ids_without_package:
                if flag.expiration_date == False:
                    raise UserError(_("Expiration Date is Required!"))
                    return
        return super(StockPicking, self).button_validate()
        # if self.picking_type_id.sequence_code == 'IN':
        #     picking = self.env['stock.picking'].search([('origin', '=', self.origin), ('name', 'ilike', 'INT')])
        #     if picking:
        #         for flag in picking.move_line_ids_without_package:
        #             existing_picking_line = self.move_line_ids_without_package.filtered(lambda r : r.product_id.id ==flag.product_id.id);
        #             if existing_picking_line and existing_picking_line.expiration_date:
        #                 flag.expiration_date = existing_picking_line.expiration_date
        # return result



