# -*- encoding: utf-8 -*-


{
    'name': u'Données de base de la comptabilité Marocaine',
    'version': '1.0',
    'summary': u'Plan comptable, Types de comptes, Taxes',
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": [
        'account',
    ],
    'data': [
        'views/account_account.xml',
        'views/account_move_line.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
