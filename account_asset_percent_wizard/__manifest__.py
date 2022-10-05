# -*- encoding: utf-8 -*-

{
    'name': 'Amortissement en pourcentage par wizard',
    'version': '1.0',
    'author': 'Osisoftware',
    'website': 'http://www.osisoftware.ma',
    "depends": [
        'account','os_account_asset',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/asset_bypercent.xml',
        'views/asset_view.xml',

        ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
