# -*- coding: utf-8 -*-
{
    'name': "Import Assets",

    'summary': """
        This Module allow us to import assets from excel file to odoo""",

    'author': 'Osisoftware',
    'website': 'http://www.osisoftware.net',

    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','os_account_asset'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/asset_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
