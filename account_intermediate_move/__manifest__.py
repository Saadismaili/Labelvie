# -*- encoding: utf-8 -*-

{
    'name': u'Ecriture comptable intermédiaire',
    'version': '1.0',
    'author': 'Andema',
    'summary': u"Ajout écriture comptable intermédiaire",
    'description': """Ce module permet d'ajouter une écriture comptable intermédiaire dans
                      le cas des paiements standards de Odoo""",
    'website': 'http://www.andemaconsulting.com',
    "depends": [
        'tva_encaissement_maroc'
    ],
    'data': [
        "wizard/inter_move.xml",
        ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
