# -*- coding: utf-8 -*-

{
    'name': u"Cloture de l'exercice fiscal",
    'version': '1.0',
    'summary': u"Génération de l'ANV",
    'category': 'Accounting',
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    'depends': [
        'account',
        'account_fiscal_period',
    ],
    'data': [
        "security/ir.model.access.csv",
        'views/account_fiscal_year_close.xml',
        'wizards/account_fiscal_year_close_wizard.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
