# -*- coding: utf-8 -*-
{
    'name': "Generate Me",
    'summary': """
        This model allow us to import general pdf that contains all our fiscal and accountant tables""",
    'author': "Osisoftware",
    'website': "http://www.yourcompany.com",
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','liasse_fiscale_tables','partner_extend'],#

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_company.xml',
        'data/data.xml',
        'wizards/repports_generator.xml',
        'wizards/template.xml',
        'wizards/template_2.xml',
    ],

}
