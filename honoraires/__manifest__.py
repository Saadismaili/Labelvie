# -*- coding: utf-8 -*-

{
    'name': u"Gestion de l'état des honoraires",
    'version': '1.0',
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": [
        'account','partner_extend','account_fiscal_period',
        'odoo_excel_engin',
        'payement_method'
    ],
    'data': [
        "views/partner_view.xml",
        "views/honoraires_view.xml",
        "views/res_config_view.xml",
        "security/honoraires.xml",
        "security/ir.model.access.csv",
        ],
    "external_dependencies": {
        'python': ['openpyxl']
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
