# -*- encoding: utf-8 -*-


{
    'name': u'Ajout d\'un code TVA pour chaque type de taxe (81, 140...) selon le cahier de charge de la DGI',
    'version': '1.0',
    'author': 'Osisoftware',
    'website': 'http://www.osisoftware.ma',
    "depends": [
        'account',
    ],
    'data': [
        'views/account_tax_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
