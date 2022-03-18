# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    expiration_date = fields.Date(related='lot_id.expiration_date',readonly=False,string='Expiry Date', help='This is the date on which the goods with this Serial Number may'
                                                                 ' become dangerous and must not be consumed.')

    def write(self, vals):

        res = super(StockMoveLine, self).write(vals)
        if 'expiration_date' in vals and self.lot_id:
            self.lot_id.update({
                'expiration_date':self.expiration_date
            })
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        if self.picking_type_id.sequence_code == 'INT':
            for flag in self.move_line_ids_without_package:
                if flag.expiration_date == False:
                    raise UserError(_("Expiry Date is Required!"))
                    return
        return super(StockPicking, self).button_validate()





