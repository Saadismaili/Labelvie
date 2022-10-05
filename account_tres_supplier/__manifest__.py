# -*- coding: utf-8 -*-

{
    'name': 'Gestion avancée des paiements Fournisseurs',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'complexity': 'normal',
    'description': '''
        Gestion avancée des paiements Fournisseurs (Chèques/Effets/Espèces/OV)
    ''',
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    'images': [],
    'depends': ['account',
                'l10n_maroc',
                'account_fiscal_period'],
    'data': [
        'views/supplier_payment_sequence.xml',
        'views/supplier_payment_view.xml',
        'views/supplier_payment_pieces_view.xml',
        'views/supplier_payment_data.xml',
        'security/supplier_payment_security.xml',
        'security/ir.model.access.csv',
        'reports/supplier_payment_report.xml',
        'reports/report_view.xml',

    ],
    'demo': [],
    'test':[],
    'installable': True,
    'auto_install': False,
    'application': False,
}
