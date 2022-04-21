# Copyright 2021 VentorTech OU
# Part of Ventor modules. See LICENSE file for full copyright and licensing details.

{
    'name': 'MDGPortal Sync',
    "version": "15.0.1",
    'author': 'MDG',
    'website': '',
    'license': 'LGPL-3',
    'installable': True,

    'summary': 'Connect with MDG Portal',
    'depends': [
        'base','stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_connection.xml',
    ],
}
