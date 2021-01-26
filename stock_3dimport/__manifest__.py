# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Import stock 3D Location',
    'version': '14.0.2.0.0',
    'license': 'AGPL-3',
    'summary': """Import Stock 3D Location from csv file using barcode to find location and parent location,
        colums separated by ;
        see example folder""",
    'category': 'Warehouse',
    'description': 'Import stock 3d Location from csv file, colums separated by ;',
    'author': 'Andrea Piovesana, Loris Tissino',
    'support': 'andrea.m.piovesana@gmail.com',
    'website': 'https://openindustry.it',
    'depends': [
        #'stock_3dbase',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/location.xml',
    ],
    'images': [
        'images/stock_3dimport.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 30.00,
    'currency': 'EUR',
}
