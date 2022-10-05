# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ExternalPaymentWizard(models.TransientModel):
    _name = 'external.supplier.payment'

    payment_date = fields.Date('Date de paiement')
    payment_amount = fields.Float('Montant de paiement')
    pay_journal_id = fields.Many2one('account.journal', string='Journal de paiement')
    bank_account_id = fields.Many2one('account.account', string='Compte de la banque')
    ras_account_id = fields.Many2one('account.account', string='Compte de la RAS',
                                     default=lambda self: self.env.ref('l10n_maroc.1_pcg_44570000').id)

    def pay_action(self):
        rec = self.env['account.external.supplier'].search([('id', '=', self._context['active_id'])])
        account_move_obj = self.env['account.move']

        if not self.payment_amount:
            raise ValidationError('Veuiller renseigner un montant de paiement')

        if rec.mt_du < self.payment_amount:
            self.payment_amount = rec.mt_du

        if rec.mt_du == 0:
            rec.write({
                'state': 'paid'
            })

        if rec.mt_du > 0:
            supplier_account_id = self.env.ref('l10n_maroc.1_pcg_44111000')
            lines = [rec.generate_pay_accounting_line(self.payment_amount, supplier_account_id, 'debit', self.pay_journal_id, self.payment_date, True),
                     rec.generate_pay_accounting_line(self.payment_amount, self.bank_account_id, 'credit', self.pay_journal_id, self.payment_date),
                     rec.generate_pay_accounting_line(self.payment_amount * 0.111108333333333, self.ras_account_id,
                                                       'debit', self.pay_journal_id, self.payment_date),
                     rec.generate_pay_accounting_line(self.payment_amount * 0.111108333333333, self.bank_account_id,
                                                       'credit', self.pay_journal_id, self.payment_date)]

            move_id = account_move_obj.create({
                'journal_id': self.pay_journal_id.id,
                'date': self.payment_date,
                'ref': '[PAI]' + rec.name,
                'type': 'entry',
                'line_ids': lines,
            })
            move_id.post()

            rec.mt_du = rec.mt_du - self.payment_amount
            if rec.mt_du == 0:
                rec.write({
                    'state': 'paid'
                })
