# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Barcode in Mobile for MDG Central WH',
    'category': 'Inventory/Inventory',
    'summary': 'Stock Barcode scan and customized for mdg wh',
    'version': '1.0',
    'description': """ """,
    'depends': ['stock_barcode_mobile'],
    'qweb': ['static/src/xml/stock_mobile_barcode_mdg.xml'],
    'data': ['views/stock_barcode_template.xml'],
    'installable': True,
    'auto_install': True,
}
