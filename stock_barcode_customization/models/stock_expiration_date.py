# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    expiration_date = fields.Date(related='lot_id.expiration_date',store=True,readonly=False,string='Expiry Date', help='This is the date on which the goods with this Serial Number may'
                                                                 ' become dangerous and must not be consumed.')

    validated_by = fields.Many2one('res.partner', string="Validated By",store=True, readonly=True)


    def write(self, vals):
        res = super(StockMoveLine, self).write(vals)
        if 'expiration_date' in vals and self.lot_id:
            self.lot_id.update({
                'expiration_date':self.expiration_date
            })
        return res

    def _create_and_assign_production_lot(self):
        """ Creates and assign new production lots for move lines."""
        lot_vals = [{
            'company_id': ml.move_id.company_id.id,
            'name': ml.lot_name,
            'product_id': ml.product_id.id,
            'expiration_date':ml.expiration_date,
        } for ml in self]
        lots = self.env['stock.production.lot'].create(lot_vals)
        for ml, lot in zip(self, lots):
            ml._assign_production_lot(lot)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        if self.picking_type_id.sequence_code == 'INT':
            for flag in self.move_line_ids_without_package:
                if flag.expiration_date == False:
                    raise UserError(_("Expiry Date is Required!"))
                    return

                if ('Pick-Face-CA' in flag.location_dest_id.complete_name and flag.result_package_id):
                    flag.update({
                        'result_package_id': False,
                    })

        return super(StockPicking, self).button_validate()





