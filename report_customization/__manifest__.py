{
    'name': 'Report Customization',
    "version": "14.0.0.0.0",
    'author': '7thcomputing',
    'website': 'https://www.7thcomputing.com',
    'license': 'LGPL-3',
    'installable': True,
    'summary': 'Report Customization',
    'depends': [
        'base',
        'stock',
        'stock_barcode',
    ],
    'data': [
             'reports/report_stockpicking_operations.xml',
    ],
    "assets": {
            'web.assets_backend': [
                'report_customization/static/src/js/barcode_model.js',
            ],
        },

}