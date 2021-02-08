# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from base64 import b64encode
from reportlab.graphics import barcode

from odoo import api, models
from odoo.exceptions import Warning


class product_barcode_report_template(models.AbstractModel):
    _name = 'report.aces_barcode_label.product_barcode_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'aces_barcode_label.product_barcode_report_template')
        if 'barcode' in [x.name for x in self.env['aces.small.barcode.label.line'].browse(data['form']['field_lines'])] \
                and data['form']['barcode_type']:
            for product in self.env['aces.small.product.label.qty'].browse(data['form']['product_lines']):
                if not product.product_id.barcode:
                    continue
                try:
                    barcode.createBarcodeDrawing(data['form']['barcode_type'], value=product.product_id.barcode,
                                                 format='png', width=2000, height=2000)
                except:
                    raise Warning('Select valid barcode type according product barcode value !')

        return {
            'doc_ids': self.env["aces.small.barcode.label"].browse(data["ids"]),
            'doc_model': report.model,
            'docs': self,
            'get_label_data': self._get_label_data,
            'draw_style': self._draw_style,
            'get_barcode_string': self._get_barcode_string,
            'draw_barcode_style': self._draw_barcode_style,
            'data': data,
            'name' : 'Yogesh'
        }

    def _draw_barcode_style(self, data):
        return "width:%s;height:%s;" % (str(data['disp_width']) + "px", str(data['disp_height']) + "px")

    def _get_barcode_string(self, ean13, data):
        barcode_str = barcode.createBarcodeDrawing(
            data['barcode_type'], value=ean13, format='png', width=2000,
            height=2000, humanReadable=True)
        barcode_str = b64encode(barcode_str.asString('png'))
        return barcode_str

    def _get_label_data(self, form):
        currency_symbol = ''
        if form['currency_id']:
            currency_symbol = self.env['res.currency'].browse(form['currency_id'][0]).symbol
        line_ids = []
        selected_fields = {}
        for line in self.env['aces.small.barcode.label.line'].browse(form['field_lines']):
            selected_fields.update({line.sequence: line.name})
        for product in self.env['aces.small.product.label.qty'].browse(form['product_lines']):
            product_dict = {}
            product_dict.update({'product_id': product.product_id})
            if 'barcode' in selected_fields.values() and not product.product_id.barcode:
                continue
            product_data = product.product_id.read(selected_fields.values())
            for key, value in selected_fields.items():
                if product_data[0].get(value):
                    if value == 'barcode':
                        product_dict.update({key: value})
                    elif value == 'lst_price':
                        if form['currency_position'] == 'before':
                            product_dict.update({key: currency_symbol + ' ' + str(product_data[0].get(value))})
                        else:
                            product_dict.update({key: str(product_data[0].get(value)) + ' ' + currency_symbol})
                    else:
                        product_dict.update({key: product_data[0].get(value)})
            for no in range(0, product.qty):
                line_ids.append(product_dict)
        return line_ids

    def _draw_style(self, data, field):
        style = ''
        selected_fields = {}
        for line in self.env['aces.small.barcode.label.line'].browse(data['field_lines']):
            selected_fields.update({line.name: str(line.font_size) + '-' + (line.font_color or 'black')})
        for product in self.env['aces.small.product.label.qty'].browse(data['product_lines']):
            if product.product_id.name == field:
                style = 'font-size:' + str(
                    selected_fields.get('name').split('-')[0]) + 'px;margin-top:10px;color:' + str(
                    selected_fields.get('name').split('-')[1]) + ';'
            elif product.product_id.default_code == field:
                style = 'font-size:' + str(
                    selected_fields.get('default_code').split('-')[0]) + 'px;margin-top:10px;color:' + str(
                    selected_fields.get('default_code').split('-')[1]) + ';'
            elif str(product.product_id.lst_price) in field:
                style = 'font-size:' + str(
                    selected_fields.get('lst_price').split('-')[0]) + 'px;margin-top:10px;color:' + str(
                    selected_fields.get('lst_price').split('-')[1]) + ';'
        return style

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
