# -*- encoding: utf-8 -*-

{
    'name': 'Cumul antérieur des immobilisations',
    'version': '1.0',
    'author': 'Osisoftware',
    'website': 'http://www.andemaconsulting.com',
    "depends": [
        'account','account_asset',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/account_asset_anterieur_views.xml',


        ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
