# -*- coding: utf-8 -*-

{
    'name': u'Exercice fiscal',
    'version': '1.0',
    'summary': u"Définition de l'exercice fiscal",
    'category': 'Accounting',
    'author': 'Osisoftware',
    'website': 'http://www.osisoftware.ma',
    'depends': [
        'account',
        'date_range'
    ],
    'data': [
        'data/date_range_type.xml',
        'views/date_range_type.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
