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

{
    'name': 'Stock Mulit UOM display',
    'version': '1.1',
    'author': '7thcomputing',
    'category': 'Stock',
    'description': """
        Module will show with purchase uom on stock move.
    """,
    'website': 'http://www.acespritech.com',
    'price': 55,
    'currency': 'EUR',
    'summary': 'Module allows to change the sequence of fields to display in barcode label report.',
    'depends': ['base', 'stock','stock_barcode','product_expiry'],
    'data': [
       'views/stock_view.xml'
    ],
    
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
