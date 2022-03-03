{
    'name': 'Barcode Customization',
    "version": "15.0.0.0.0",
    'author': '',
    'website': '',
    'license': 'LGPL-3',
    'installable': True,
    'summary': 'Barcode Customization',
    'depends': [
        'base',
        'stock',
        'stock_barcode',
        'product_expiry'
    ],
    'data': [
             'views/stock_barcode_view.xml',
             'views/stock_expiration_date.xml',
             'views/stock_view.xml',
            "views/production_lot_view.xml",
    ],

    'assets': {
            'web.assets_backend': [
                'stock_barcode_customization/static/src/components/stock_barcode_main.js',
                'stock_barcode_customization/static/src/components/stock_barcode_dest_main.js',
            ],
            'web.assets_qweb': [
                'stock_barcode_customization/static/src/**/*.xml',
            ],
        }
}