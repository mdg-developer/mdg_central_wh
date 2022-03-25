{
    'name': 'Account Customizations',
    "version": "15.0.0.0.0",
    'author': 'MDG',
    'website': '',
    'license': 'LGPL-3',
    'installable': True,
    'summary': 'Account Customization',
    'depends': [
        'account_reports',

    ],
    'data': [
             'views/search_template_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_report_customization/static/src/js/account_report.js',
        ],

    }
}