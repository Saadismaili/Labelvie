# -*- encoding: utf-8 -*-

{
    'name': u'États financiers: Balance, Grand livre',
    'version': '1.0',
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": [
        'account',
        'date_range',
        'account_fiscal_year',
        'account_fiscal_year_close',
        'report_xlsx',
    ],
    'data': [
        "security/ir.model.access.csv",
        'views/report_views.xml',
        "wizard/financial_report.xml",
        "wizard/financial_report_menu.xml",

        ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
