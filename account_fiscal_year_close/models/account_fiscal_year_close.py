# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
        ('situation', u'Journal de situation Ouverture/Clôture')
    ], required=True,
        help="Select 'Sale' for customer invoices journals.\n" \
             "Select 'Purchase' for vendor bills journals.\n" \
             "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n" \
             "Select 'General' for miscellaneous operations journals."
             "Select Opening/Closing Situation for entries generated for new fiscal years.")


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    close_method = fields.Selection([('none', 'None'),
                                     ('balance', 'Balance'),
                                     ('unreconciled', 'Unreconciled')],
                                    u'Méthode de report à nouveau', required=True)