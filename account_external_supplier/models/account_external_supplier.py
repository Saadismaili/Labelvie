# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountExternalSupplier(models.Model):
    _name = 'account.external.supplier'
    _rec_name = 'name'

    name = fields.Char('Référence')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('posted', 'Comptabilisé'),
        ('paid', 'Payé'),
    ], 'Status', default='draft', readonly=True)

    type = fields.Selection([
        ('net', 'Montant Net'),
        ('ttc', 'Service TVA comprise et RAS comprise'),
    ], 'Type de facture', default='net')

    supplier_id = fields.Many2one('res.partner', string="Fournisseur")
    date = fields.Date('Date')
    journal_id = fields.Many2one('account.journal', string='Journal')

    due_date = fields.Date(u'Date d\'échéance')

    mt_ttc = fields.Float('Montant TTC', compute='compute_amounts', store=True)
    mt_global = fields.Float('Montant Global', compute='compute_amounts', store=True)
    mt_ht = fields.Float('Montant Hors taxe', compute='compute_amounts', store=True)
    mt_tva = fields.Float('Montant TVA', compute='compute_amounts', store=True)
    mt_ras = fields.Float('RAS', compute='compute_amounts', store=True)
    mt_net = fields.Float(u'Net à payer', compute='compute_amounts', store=True)

    mt_du = fields.Float(u'Montant du', compute='compute_mt_du', store=True)

    move_line_ids = fields.One2many('account.move.line', 'external_supplier_id')
    payment_line_ids = fields.One2many('account.payment', 'external_supplier_pay_id', string=u"Écritures comptables")

    payement_method_id = fields.Many2one(comodel_name='payement.method',
                                         string=u'Méthode de paiement')

    @api.depends('mt_ttc', 'mt_net')
    def compute_amounts(self):
        if self.type == 'ttc':
            self.mt_ht = self.mt_ttc / 1.2
            self.mt_ras = self.mt_ht * 0.1
            self.mt_tva = self.mt_ht * 0.2
            self.mt_net = self.mt_ttc - self.mt_ras - self.mt_tva
            self.mt_global = self.mt_ttc
        if self.type == 'net':
            self.mt_ras = self.mt_net * 0.111108333333333
            self.mt_tva = self.mt_net * 0.222216666666667
            self.mt_global = self.mt_net * 1.3333
            self.mt_ht = self.mt_global / 1.2
            self.mt_ttc = self.mt_ht + self.mt_tva

        self.mt_du = self.mt_net

    def action_pay(self):
        total_paye = sum(
            payment.amount for payment in self.payment_line_ids.filtered(lambda rec: rec.state == 'posted'))
        if self.mt_net - total_paye > 0:
            self.mt_du = self.mt_net - total_paye
        elif self.mt_net - total_paye == 0:
            self.mt_du = 0
            lines_pay = self.payment_line_ids.move_line_ids.filtered(lambda x: x.account_id.user_type_id.type in ('receivable', 'payable'))
            lines = self.move_line_ids.filtered(lambda x: x.account_id.user_type_id.type in ('receivable', 'payable'))\
                .filtered(lambda x: x.credit > 0)
            lines = lines + lines_pay
            lines.reconcile()
            self.write({
                'state': 'paid'
            })
        else:
            raise ValidationError('Vous allez payer plus que le montant Dû')

    def action_send(self):
        self.move_line_ids.unlink()
        account_move_obj = self.env['account.move']
        account_settings_obj = self.env['external.supplier.settings'].search([])
        lines = []

        for account in account_settings_obj:
            amount = self[account.name]
            if account.type == 'debiteur':
                debit_val = {
                    'name': self.name,
                    'date': self.date,
                    'date_maturity': self.due_date,
                    'ref': self.name,
                    'partner_id': self.supplier_id.id,
                    'account_id': account.account_id.id,
                    'credit': 0.0,
                    'debit': amount,
                    'external_supplier_id': self.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': False,
                    # 'tax_ids': [(4, purchase_tax_id.id)] if account.name == 'mt_ht' else False
                }
                lines.append((0, 0, debit_val))
            elif account.type == 'crediteur':
                credit_val = {
                    'name': self.name,
                    'date': self.date,
                    'date_maturity': self.due_date,
                    'ref': self.name,
                    'partner_id': self.supplier_id.id,
                    'account_id': account.account_id.id,
                    'credit': amount,
                    'debit': 0.0,
                    'external_supplier_id': self.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': False
                }
                lines.append((0, 0, credit_val))
        move_id = account_move_obj.create({
            'journal_id': self.journal_id.id,
            'date': self.date,
            'ref': self.name,
            'line_ids': lines,
            'partner_id': self.supplier_id.id,
            # 'type': 'in_invoice'
        })
        move_id.post()
        self.write({
            'state': 'posted'
        })

    def generate_pay_accounting_line(self, amount, account, account_type, journal, date, tax=False):
        if account_type == 'debit':
            debit_val = {
                'name': 'PAI ' + self.name,
                'date': date,
                'date_maturity': self.due_date,
                'ref': '[PAI]' + self.name,
                'partner_id': self.supplier_id.id,
                'account_id': account.id,
                'credit': 0.0,
                'debit': amount,
                'external_supplier_pay_id': self.id,
                'journal_id': journal.id,
                'currency_id': False
            }
            return (0, 0, debit_val)
        elif account_type == 'credit':
            credit_val = {
                'name': 'PAI ' + self.name,
                'date': date,
                'date_maturity': self.due_date,
                'ref': '[PAI]' + self.name,
                'partner_id': self.supplier_id.id,
                'account_id': account.id,
                'credit': amount,
                'debit': 0.0,
                'external_supplier_pay_id': self.id,
                'journal_id': journal.id,
                'currency_id': False,
            }
            return (0, 0, credit_val)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    external_supplier_id = fields.Many2one('account.external.supplier')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    external_supplier_pay_id = fields.Many2one('account.external.supplier')


class ExternalSupplierAccounts(models.Model):
    _name = 'external.supplier.settings'

    name = fields.Char('Description')
    type = fields.Selection([('crediteur', 'Créditeur'), ('debiteur', 'Débiteur')], default='crediteur',
                            string="type de compte")
    account_id = fields.Many2one('account.account')
    actif = fields.Boolean('Actif')
