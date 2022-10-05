# -*- encoding: utf-8 -*-

{
    'name': 'Gestion des immobilisations (norme Marocaine)',
    'version': '1.0',
    'author': 'Osisoftware',
    'website': 'https://osisoftware.net',
    "depends": [
        'os_account_asset',
    ],
    'data': [
        'wizard/asset_control_view.xml',
        'security/asset_security.xml',
        'security/ir.model.access.csv',
        "views/asset.xml"
        ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
