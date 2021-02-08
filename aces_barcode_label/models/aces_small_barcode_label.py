# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning

class aces_small_barcode_template(models.Model):
    _name = 'aces.small.barcode.template'

    def close_wizard(self):
        self.write({'active': False})
        return {
            'name': _('Product Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'aces.small.barcode.label',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }

    def go_to_label_wizard(self):
        if not self.name:
            raise Warning(_('Template Design Name is required.'))
        return {
            'name': _('Product Label'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'aces.small.barcode.label',
            'target': 'new',
            'res_id': self._context.get('wiz_id'),
            'context': self.env.context
        }

    @api.model
    def default_get(self, fields_list):
        res = super(aces_small_barcode_template, self).default_get(fields_list)
        if self._context.get('wiz_id') and self._context.get('from_wizard'):
            for wiz in self.env['aces.small.barcode.label'].browse(self._context.get('wiz_id')):
                prod_list = []
                for line in wiz.field_lines:
                    prod_list.append((0, 0, {'font_size': line.font_size,
                                             'font_color': line.font_color,
                                             'sequence': line.sequence,
                                             'name': line.name}))
                res.update({'height': wiz.height,
                            'width': wiz.width,
                            'currency_id': wiz.currency_id.id,
                            'currency_position': wiz.currency_position,
                            'disp_height': wiz.disp_height,
                            'disp_width': wiz.disp_width,
                            'barcode_type': wiz.barcode_type,
                            'field_lines': prod_list
                            })
        return res

    def _get_currency(self):
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    name = fields.Char(string="Design Name")
    active = fields.Boolean(string="Active", default=1)
    height = fields.Float(string="Height", required=True, default=30)
    width = fields.Float(string="Width", required=True, default=43)
    currency_id = fields.Many2one('res.currency', string="Currency", default=_get_currency)
    currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default='after')
    disp_height = fields.Float(string="Display Height (px)", required=True, default=30)
    disp_width = fields.Float(string="Display Width (px)", required=True, default=120)
    barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                     ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                     ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                     ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                     ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                     ('QR', 'QR')],
                                    string='Type', default='EAN13')
    field_lines = fields.One2many('aces.small.barcode.template.line', 'barcode_label_id', string="Fields")


class aces_small_barcode_template_line(models.Model):
    _name = 'aces.small.barcode.template.line'

    font_size = fields.Integer(string="Font Size", default=10)
    font_color = fields.Selection([('black', 'Black'), ('blue', 'Blue'),
                                   ('cyan', 'Cyan'), ('gray', 'Gray'),
                                   ('green', 'Green'), ('lime', 'Lime'),
                                   ('maroon', 'Maroon'), ('pink', 'Pink'),
                                   ('purple', 'Purple'), ('red', 'Red'),
                                   ('yellow', 'Yellow')], string="Font Color", default='black')
    sequence = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], string="Sequence")
    name = fields.Selection([('default_code', 'Internal Reference'),
                             ('name', 'Product Name'),
                             ('lst_price', 'Sale Price'),
                             ('barcode', 'Barcode')], string="Name")
    barcode_label_id = fields.Many2one('aces.small.barcode.template', string="Barcode Label ID")


class aces_small_barcode_label(models.TransientModel):
    _name = 'aces.small.barcode.label'

    @api.onchange('design_id')
    def on_change_design_id(self):
        if self.design_id:
            prod_list = []
            for line in self.design_id.field_lines:
                prod_list.append((0, 0, {'font_size': line.font_size,
                                         'font_color': line.font_color,
                                         'sequence': line.sequence,
                                         'name': line.name}))
            self.height = self.design_id.height
            self.width = self.design_id.width
            self.currency_id = self.design_id.currency_id and self.design_id.currency_id.id or False
            self.currency_position = self.design_id.currency_position
            self.disp_height = self.design_id.disp_height
            self.disp_width = self.design_id.disp_width
            self.barcode_type = self.design_id.barcode_type
            self.field_lines = prod_list

    @api.model
    def default_get(self, fields_list):
        prod_list = []
        res = super(aces_small_barcode_label, self).default_get(fields_list)
        if self._context.get('active_ids'):
            for product in self._context.get('active_ids'):
                if self._context.get('type'):
                    product_id = self.env['product.product'].browse(product)
                    prod_list.append((0, 0, {'product_id': product_id.product_tmpl_id.id, 'qty': 1}))
                else:
                    prod_list.append((0, 0, {'product_id': product, 'qty': 1}))
        res['product_lines'] = prod_list
        return res

    def _get_currency(self):
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    @api.model
    def _get_report_paperformat_id(self):
        xml_id = self.env['ir.actions.report'].search([('report_name', '=',
                                                        'aces_barcode_label.product_barcode_report_template')])
        if not xml_id or not xml_id.paperformat_id:
            raise Warning('Someone has deleted the reference paperformat of report.Please Update the module!')
        return xml_id.paperformat_id.id

    design_id = fields.Many2one('aces.small.barcode.template', string="Design")
    paper_format_id = fields.Many2one('report.paperformat', string="Paper Format")
    height = fields.Float(string="Height", required=True, default=30)
    width = fields.Float(string="Width", required=True, default=43)
    currency_id = fields.Many2one('res.currency', string="Currency", default=_get_currency)
    currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default='after')
    disp_height = fields.Float(string="Display Height (px)", required=True, default=30)
    disp_width = fields.Float(string="Display Width (px)", required=True, default=120)
    barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                     ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                     ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                     ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                     ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                     ('QR', 'QR')],
                                    string='Type', default='EAN13')
    field_lines = fields.One2many('aces.small.barcode.label.line', 'barcode_label_id', string="Fields")
    product_lines = fields.One2many('aces.small.product.label.qty', 'barcode_label_id', string="Product List")
    make_update_existing = fields.Boolean(string="Update Existing Design")

    def action_call_report(self):
        line_seq = []
        line_name = []
        if self.height <= 0.0 or self.width <= 0.0:
            raise Warning(_("Label height and width should be greater than zero(0)."))
        if not self.field_lines:
            raise Warning(_("Please select any one field to print in label."))
        for line in self.field_lines:
            if line.name == 'barcode' and (not self.barcode_type or self.disp_height <= 0.0 or self.disp_width <= 0.0):
                raise Warning(
                    _("To print barcode enter appropriate data in barcode type, display height and width fields."))
            if not line.sequence or not line.name:
                raise Warning(_("Sequence and fields name can not be empty."))
            if line.sequence in line_seq or line.name in line_name:
                raise Warning(_("Sequence and field name cannot repeated."))
            line_seq.append(line.sequence)
            line_name.append(line.name)
        if 'lst_price' in line_name and self.currency_id and not self.currency_position:
            raise Warning(_("Please, select currency position to display currency symbol."))
        if 'barcode' in line_name:
            if not [product.product_id.barcode for product in self.product_lines if product.product_id.barcode]:
                raise Warning(_("You have selected barcode to print, but none of product(s) contain(s) barcode."))
        if sum([p.qty for p in self.product_lines]) <= 0:
            raise Warning(_("Please, enter product quantity to print no. of labels."))
        self.paper_format_id.sudo().write({
            'page_width': self.width,
            'page_height': self.height
        })
        data = self.read()[0]
        datas = {
            'ids': self._ids,
            'model': 'aces.small.barcode.label',
            'form': data
        }
        return self.env.ref('aces_barcode_label.aces_small_barcode_label_report').report_action(self, data=datas)

    def save_design_template(self):
        if not self.make_update_existing:
            view_id = self.env['ir.model.data'].get_object_reference('aces_barcode_label',
                                                                     'wizard_aces_small_barcode_template_form_view')[1]
            ctx = dict(self.env.context)
            ctx.update({'wiz_id': self.id})
            return {
                'name': _('Product Label Template'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'aces.small.barcode.template',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'view_id': view_id,
                'context': ctx,
                'nodestroy': True
            }
        else:
            prod_list = []
            if self.design_id:
                for line in self.field_lines:
                    prod_list.append((0, 0, {'font_size': line.font_size,
                                             'font_color': line.font_color,
                                             'sequence': line.sequence,
                                             'name': line.name}))
                self.design_id.field_lines = False
                self.design_id.write({
                    'height': self.height,
                    'width': self.width,
                    'currency_id': self.currency_id.id,
                    'currency_position': self.currency_position,
                    'disp_height': self.disp_height,
                    'disp_width': self.disp_width,
                    'barcode_type': self.barcode_type,
                    'field_lines': prod_list
                })
                return {
                    'name': _('Product Page Label'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'aces.small.barcode.label',
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context
                }
            else:
                raise Warning(_("Please, select design template first !"))


class aces_small_barcode_label_line(models.TransientModel):
    _name = 'aces.small.barcode.label.line'

    font_size = fields.Integer(string="Font Size", default=10)
    font_color = fields.Selection([('black', 'Black'), ('blue', 'Blue'),
                                   ('cyan', 'Cyan'), ('gray', 'Gray'),
                                   ('green', 'Green'), ('lime', 'Lime'),
                                   ('maroon', 'Maroon'), ('pink', 'Pink'),
                                   ('purple', 'Purple'), ('red', 'Red'),
                                   ('yellow', 'Yellow')], string="Font Color", default='black')
    sequence = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], string="Sequence")
    name = fields.Selection([('default_code', 'Internal Reference'),
                             ('name', 'Product Name'),
                             ('lst_price', 'Sale Price'),
                             ('barcode', 'Barcode')], string="Name")
    barcode_label_id = fields.Many2one('aces.small.barcode.label', string="Barcode Label ID")


class aces_small_barcode_label_line(models.TransientModel):
    _name = 'aces.small.product.label.qty'

    product_id = fields.Many2one('product.template', string="Product(s)", required=True)
    qty = fields.Integer(string="Quantity", default=1)
    barcode_label_id = fields.Many2one('aces.small.barcode.label', string="Barcode Label ID")

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
