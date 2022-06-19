# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    expiration_date = fields.Date(string='Expiry Date',
                                      help='This is the date on which the goods with this Serial Number may become dangerous and must not be consumed.')
    @api.depends('expiration_date')
    def _compute_product_expiry_alert(self):

        current_date = fields.Date.today()
        for lot in self:
            if lot.expiration_date:
                lot.product_expiry_alert = lot.expiration_date <= current_date
            else:
                lot.product_expiry_alert = False

    def _get_dates(self, product_id=None):
        """Returns dates based on number of days configured in current lot's product."""
        mapped_fields = {
            'expiration_date': 'expiration_time',
            'use_date': 'use_time',
            'removal_date': 'removal_time',
            'alert_date': 'alert_time'
        }
        res = dict.fromkeys(mapped_fields, False)
        product = self.env['product.product'].browse(product_id) or self.product_id
        if product:
            for field in mapped_fields:
                duration = getattr(product, mapped_fields[field])
                if duration:
                    date = datetime.date.today() + datetime.timedelta(days=duration)
                    res[field] = fields.Datetime.to_string(date)
        return res

    def _update_date_values(self, new_date):
        if new_date:
            time_delta = new_date - (self.expiration_date or fields.Date.today())
            vals = self._get_date_values(time_delta, new_date)
            vals['expiration_date'] = new_date
            self.write(vals)


    @api.model
    def _get_fields_stock_barcode(self):
        fields = super()._get_fields_stock_barcode()
        fields.append('expiration_date')
        return fields
