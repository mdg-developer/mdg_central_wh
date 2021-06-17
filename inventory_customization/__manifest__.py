{
    'name': 'Inventory Customization',
    "version": "14.0.0.0.0",
    'author': 'VentorTech',
    'website': 'https://www.7thcomputing.com',
    'license': 'LGPL-3',
    'installable': True,
    'summary': 'Inventory Customization',
    'depends': [
        'base',
        'stock',
        'product_expiry'
    ],
    'data': [
             'views/product_template_view.xml',
             'views/stock_move_line_view.xml',
    ],
}