# -*- encoding: utf-8 -*-

{
    'name': u'Formules et rapports de la liasse fiscale Marocaine Excel',
    'version': '1.0',
    'author': 'Osisoftware',
    'website': 'http://www.osisoftware.ma',
    "depends": [
        'report_xlsx', 'account_fiscal_year', 'account','base'
    ],
    'data': [
        "security/odoo_excel_engin.xml",
        "security/ir.model.access.csv",
        "views/report_engin.xml",
        "views/formulas.xml",
        "wizard/print_report.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
