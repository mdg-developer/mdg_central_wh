# Copyright 2020 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock 3D View',
    'version': '14.0.7.0.0',
    'license': 'AGPL-3',
    'summary': """
        Stock 3D View enable to view pan and zoom multi warehouse locations in a 3d space
    """,
    'description': """
        Stock 3D View Multi Warehouse
    """,
    'author': 'Andrea Piovesana, Loris Tissino, Davide Corio, Matteo Boscolo',
    'support': 'andrea.m.piovesana@gmail.com',
    'website': 'https://openindustry.it',
    'category': 'Warehouse',
    'depends': [
        'stock_3dbase',
    ],
    'data': [
        'views/stock_view.xml',
    ],
    'qweb': [
        'static/src/xml/templates.xml',
    ],
    'images': [
        'images/stock_3dview.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 150.00,
    'currency': 'EUR',

    "assets": {
        'web.assets_common': [
            'stock_3dview/static/src/css/style.css" rel="stylesheet',
        ],
        'web.assets_backend': [
            'stock_3dview/static/src/js/libs/three.min.js',
            'stock_3dview/static/src/js/libs/stats.min.js',
            'stock_3dview/static/src/js/libs/dat.gui.min.js',
            'stock_3dview/static/src/js/libs/OrbitControls.js',
            'stock_3dview/static/src/js/libs/Detector.js',
            'stock_3dview/static/src/js/renderer.js',
            'stock_3dview/static/src/js/model.js',
            'stock_3dview/static/src/js/threedview.js',

        ],
    },
}
