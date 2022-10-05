# -*- coding: utf-8 -*-

{
    'name': 'Gestion des bordereau especes',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'complexity': 'normal',
    'description': '''
        Gestion des bordereau especes
    ''',
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    'images': [],
    'depends': ['account','mail','account_tres_customer'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/bordereau.xml',
        'report/report_bordereau.xml',
        'report/template_bordereau.xml'
    ],
    'demo': [],
    'test':[],
    'installable': True,
    'auto_install': False,
    'application': False,
}
