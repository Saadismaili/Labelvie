# -*- coding: utf-8 -*-

{
    'name': u'Période fiscale',
    'version': '1.0',
    'summary': u'Définition de la période fiscale',
    'category': 'Accounting',
    'author': 'Osisoftware',
    'website': 'http://www.osisoftware.ma',
    'depends': [
        'account_fiscal_year',
    ],
    'data': [
        'security/date_range_security.xml',
        'security/ir.model.access.csv',
        'data/date_range_type.xml',
        'views/date_range_type.xml',
        'views/date_range.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
