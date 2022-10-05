# -*- coding: utf-8 -*-

{
    'name': 'Génération de la Taxe Professionnelle',
    'version': '1.0',
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": [
        'account','partner_extend','account_fiscal_period','account_asset',
        'odoo_excel_engin',
        'payement_method'
    ],
    'data': [
        "views/asset_view.xml",
        "views/taxe_professionnelle_view.xml",
        "views/res_config_view.xml",
        "security/taxe_professionnelle.xml",
        "security/ir.model.access.csv",
        ],
    "external_dependencies": {
        'python': ['openpyxl']
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
