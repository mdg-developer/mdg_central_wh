{
    'name': 'Inventory Customizations',
    "version": "14.0.0.0.0",
    'author': 'VentorTech',
    'website': 'https://www.7thcomputing.com',
    'license': 'LGPL-3',
    'installable': True,
    'summary': 'Inventory Customization',
    'depends': [
        'base',
        'stock',
        'product_expiry',
        'sale',
        'product',
        'stock_location_position',
    ],
    'data': [
             'security/ir.model.access.csv', 
             'views/product_template_view.xml',
             'views/stock_move_line_view.xml',
             'views/zone_location_view.xml',
             'views/stock_location_view.xml',
             'views/stock_views.xml',
             'views/sale_order_view.xml',
             'views/stock_picking.xml',
             'views/product_principle_test.xml',
             'views/stock_move.xml',
             'report/report_replenishment.xml',
             'report/stock_report_views.xml',
             'report/report_replenishment_line.xml',
    ],
}