# -*- coding: utf-8 -*-
{
    'name': "import journal entries",

    'summary': """
        This Module allow us to import journal entries from excel file to odoo""",

    'author': 'Osisoftware',
    'website': 'http://www.osisoftware.net',

    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_asset_ma'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'wizards/journal_entries.xml',
    ],
}
