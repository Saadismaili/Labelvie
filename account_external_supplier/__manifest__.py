# -*- encoding: utf-8 -*-


{
    'name': u'Opérations avec fournisseurs à l\'étranger',
    'version': '1.0',
    'summary': u'Gestion des factures avec fournisseurs étrangers',
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": [
        'account', 'l10n_maroc', 'payement_method'
    ],
    'data': [
        # 'data/external_supplier_settings.xml',
        'views/account_external_supplier.xml',
        'views/external_supplier_settings.xml',
        # 'wizard/payment_wizard.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
