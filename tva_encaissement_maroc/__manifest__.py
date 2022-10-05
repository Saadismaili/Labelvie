# -*- encoding: utf-8 -*-

{
    'name': u'Gestion de la TVA Marocaine(Régime encaissement)',
    'version': '1.0',
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": [
         'partner_extend','account_tres_customer','account_tres_supplier',
       'odoo_excel_engin', 'account_tax_code','account_external_supplier',
    ],
    'data': [
        "views/account_move.xml",
        "views/tva.xml",
        "views/res_config.xml",
        "views/rapport_tva.xml",
        "views/company_views.xml",
        "views/account_tax_views.xml",
        "security/tva_encaissement_maroc.xml",
        "security/ir.model.access.csv",
        # "data/account_tax_repport_data.xml",
        "data/account.tax.repport.csv",
        ],
    "external_dependencies": {
        'python': ['openpyxl']
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
