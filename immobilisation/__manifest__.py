# -*- coding: utf-8 -*-
{
    'name': "Imobilisation Tables",
    'author': "Osisoftware",
    'website': "https://www.osisoftware.ma",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['base','os_account_asset','report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_category.xml',
        'views/table_4.xml',
        'views/table_8.xml',
        'views/table_16.xml',
        'views/table_10.xml',
        'views/cession_wizard.xml',
    ],
}
