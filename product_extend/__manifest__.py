# -*- coding: utf-8 -*-

{
    "name": "Product Extend",
    "version": "1.1",
    "depends": ['product'],
    'author': 'Osisoftware',
    'website': 'http://www.osisoftware.ma',
    "category": "",
    "description": "Product Extend",
                        
    "init_xml": [],
    "depends": [
        'stock',
    ],

    'data': [
        'security/security.xml',
        'data/uom_data.xml',
        'security/ir.model.access.csv',
        'views/product_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
