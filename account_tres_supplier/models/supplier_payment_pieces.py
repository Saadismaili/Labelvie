# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import convertion


# Cash
class PaiementCashSupplier(models.Model):
    _name = 'paiement.cash.supplier'
    _description = "Cash Fournisseur"
    _inherit = ['mail.thread']

    def copy(self, default=None):
        if not default:
            default = {}
        default.update({
            'state': 'draft',
            'move_line_ids': [],
            # 'paiement_record_id': False,
        })
        return super(PaiementCashSupplier, self).copy(default)

    def unlink(self):
        for rec in self:
            move_ids = rec.move_line_ids.mapped('move_id')
            print("tototoot", move_ids)
            for move in move_ids:
                move.button_cancel()
            move_ids.unlink()
        return super(PaiementCashSupplier, self).unlink()

    @api.model
    def get_partner_account(self, part):
        account_id = False
        if part:
            account_id = part.property_account_payable_id.id
        return account_id

    def button_done(self):
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']
        for cash in self:
            account_id = self.get_partner_account(cash.partner_id)
            if not account_id:
                raise ValidationError('Le partenaire doit avoir un compte comptable')

            debit_val = {
                'name': cash.name,
                'date': cash.date,
                'ref': cash.note,
                'partner_id': cash.partner_id.id,
                'account_id': account_id,
                'credit': 0.0,
                'debit': cash.amount,
                'cash_supplier_id': cash.id,
                'journal_id': cash.journal_id.id,
                'period_id': cash.period_id.id,
                'analytic_account_id': cash.analytic_account_id and cash.analytic_account_id.id or False,
            }

            credit_val = {
                'name': cash.name,
                'date': cash.date,
                'ref': cash.note,
                'partner_id': cash.partner_id.id,
                'account_id': cash.journal_id.default_credit_account_id.id,
                'credit': cash.amount,
                'debit': 0.0,
                'cash_supplier_id': cash.id,
                'journal_id': cash.journal_id.id,
                'period_id': cash.period_id.id,
                'analytic_account_id': cash.analytic_account_id and cash.analytic_account_id.id or False,
            }
            lines = [(0, 0, debit_val), (0, 0, credit_val)]
            move_id = account_move_obj.create({
                'journal_id': cash.journal_id.id,
                'period_id': cash.period_id.id,
                'date': cash.date,
                'name': cash.name,
                'ref': cash.note,
                'line_ids': lines,
            })
            move_id.post()
            cash.state = 'done'

    def button_cancel(self):
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']
        for cash in self:
            move_ids = []
            for line in cash.move_line_ids:
                move_ids.append(line.move_id)
            move_ids = list(set(move_ids))
            new_ids = []
            for move_id in move_ids:
                new_ids.append(account_move_obj.copy(move_id.id))
            move_objs = account_move_obj.browse(new_ids)
            for move_obj in move_objs:
                for line in move_obj.line_id:
                    credit = line.credit
                    debit = line.debit
                    account_move_line_obj.write(line.id, {'credit': debit, 'debit': credit})
            cash.write({'state': 'cancel'})

    name = fields.Char(string=u'Numéro', required=True, states={'done': [('readonly', True)]})
    date = fields.Date(string=u"Date", required=True, states={'done': [('readonly', True)]})
    amount = fields.Float(string=u'Montant', required=True, states={'done': [('readonly', True)]})
    journal_id = fields.Many2one('account.journal', string=u'Journal', required=True,
                                 states={'done': [('readonly', True)]})
    period_id = fields.Many2one('date.range', string=u'Période', required=True)
    note = fields.Text(string=u"Notes")
    partner_id = fields.Many2one('res.partner', string=u'Fournisseur', required=True,
                                 states={'done': [('readonly', True)]})
    move_line_ids = fields.One2many('account.move.line', 'cash_supplier_id', string=u'Lignes comptables',
                                    states={'done': [('readonly', True)]})
    supplier_payment_id = fields.Many2one('supplier.payment', string=u'Reçu de réglement', ondelete='cascade')
    company_id = fields.Many2one('res.company', string=u'Societé', required=True, states={'done': [('readonly', True)]},
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'paiement.cash.supplier'))
    analytic_account_id = fields.Many2one('account.analytic.account', string=u'Compte Analytique',
                                          states={'done': [('readonly', True)]})
    state = fields.Selection([('draft', 'Brouillon'),
                              ('done', u'Confirmé'),
                              ('cancel', u'Annulé')], string=u'Statut', default='draft', readonly=True, required=True)


# Chèque
class PaiementChequeSupplier(models.Model):
    _name = 'paiement.cheque.supplier'
    _description = 'Cheque Fournisseur'
    _inherit = ['mail.thread']

    def action_post_fees(self):
        for record in self:
            for fees in record.frais_bancaire_ids:
                if fees.state == 'draft':
                    fees.create_account_lines()

    def unlink(self):
        for rec in self:
            move_ids = rec.move_line_ids.mapped('move_id')
            for move in move_ids:
                move.button_cancel()
            move_ids.unlink()
        return super(PaiementChequeSupplier, self).unlink()

    def copy(self, default=None):
        if not default:
            default = {}
        default.update({
            'state': 'draft',
            'move_line_ids': [],
            # 'paiement_record_id': False,
        })
        return super(PaiementChequeSupplier, self).copy(default)

    @api.model
    def get_partner_account(self, part):
        account_id = False
        if part:
            account_id = part.property_account_payable_id.id
        return account_id

    def button_envoyer(self):
        self.state = 'envoye'

    def button_done(self):
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']

        for cheque in self:
            account_id = self.get_partner_account(cheque.partner_id)
            if not account_id:
                raise ValidationError(u'Le partenaire doit avoir un compte comptable')

            debit_val = {
                'name': cheque.name,
                'date': cheque.date,
                'date_maturity': cheque.due_date,
                'ref': cheque.note,
                'partner_id': cheque.partner_id.id,
                'account_id': account_id,
                'credit': 0.0,
                'debit': cheque.amount,
                'cheque_supplier_id': cheque.id,
                'journal_id': cheque.journal_id.id,
                'period_id': cheque.period_id.id,
                'analytic_account_id': cheque.analytic_account_id and cheque.analytic_account_id.id or False,
            }

            credit_val = {
                'name': cheque.name,
                'date': cheque.date,
                'date_maturity': cheque.due_date,
                'ref': cheque.note,
                'partner_id': cheque.partner_id.id,
                'account_id': cheque.journal_id.default_credit_account_id.id,
                'credit': cheque.amount,
                'debit': 0.0,
                'cheque_supplier_id': cheque.id,
                'journal_id': cheque.journal_id.id,
                'period_id': cheque.period_id.id,
                'analytic_account_id': cheque.analytic_account_id and cheque.analytic_account_id.id or False,
            }
            lines = [(0, 0, debit_val), (0, 0, credit_val)]

            move_id = account_move_obj.create({
                'journal_id': cheque.journal_id.id,
                'period_id': cheque.period_id.id,
                'date': cheque.date,
                'name': cheque.name,
                'ref': cheque.note,
                'line_ids': lines,
            })
            move_id.post()
            cheque.state = 'done'

    def button_rejected(self):
        for cheque in self:
            # move_new_ids = []
            # move_ids = cheque.move_line_ids.mapped('move_id')
            # for move_line in cheque.move_line_ids:
            #     if move_line.reconciled:
            #         move_line.remove_move_reconcile()
            # for move in move_ids:
            #     move_new_ids.append(move.copy())
            # for move_obj in move_new_ids:
            #     for line in move_obj.line_ids:
            #         credit = line.credit
            #         debit = line.debit
            #         line.write({'credit': debit, 'debit': credit})
            #     move_obj.post()
            # lines = cheque.move_line_ids.filtered(lambda x: x.account_id.reconcile == True)
            # lines.reconcile()
            cheque.state = 'rejected'

        return True

    def button_cancel(self):
        self.state = 'cancel'

    def _get_amount_text(self):
        for rec in self:
            rec.amount_text = convertion.trad(rec.amount, 'Dh').upper()

    name = fields.Char(string=u'Numéro', required=True, states={'done': [('readonly', True)]})
    amount = fields.Float(string=u'Montant', required=True, states={'done': [('readonly', True)]})
    amount_text = fields.Char(compute='_get_amount_text', string='Montant en lettre')
    journal_id = fields.Many2one('account.journal', string=u'Journal', states={'done': [('readonly', True)]})
    period_id = fields.Many2one('date.range', string=u'Période', required=True)
    date = fields.Date(string="Date", required=True, states={'done': [('readonly', True)]})
    due_date = fields.Date(string=u"Date d'échéance", states={'done': [('readonly', True)]})
    date_paiement = fields.Date(string=u'Date de paiement', readonly=True)
    note = fields.Text(string="Notes")
    partner_id = fields.Many2one('res.partner', string=u'Fournisseur', required=True,
                                 states={'done': [('readonly', True)]})
    move_line_ids = fields.One2many('account.move.line', 'cheque_supplier_id', string=u'Lignes Comptables',
                                    states={'done': [('readonly', True)]})
    caisse_id = fields.Many2one('paiement.caisse', string=u'Caisse')
    company_id = fields.Many2one('res.company', string=u'Societé', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'paiement.cheque.supplier'))
    frais_bancaire_ids = fields.One2many('frais.bancaire', 'cheque_supplier_id', string=u'Frais Bancaires')
    analytic_account_id = fields.Many2one('account.analytic.account', string=u'Compte Analytique',
                                          states={'done': [('readonly', True)]})
    supplier_payment_id = fields.Many2one('supplier.payment', string=u'Reçu de réglement', ondelete='cascade')
    state = fields.Selection([
        ('draft', u'Brouillon'),
        ('envoye', u'Envoyé'),
        ('done', u'Payé'),
        ('cancel', u'Annule'),
        ('rejected', u'Rejeté')], 'Statut', default='draft', readonly=True, required=True)


# Effet
class PaiementEffetSupplier(models.Model):
    _name = 'paiement.effet.supplier'
    _description = "Effet Fournisseur"
    _inherit = ['mail.thread', ]

    def action_post_fees(self):
        for record in self:
            for fees in record.frais_bancaire_ids:
                if fees.state == 'draft':
                    fees.create_account_lines()

    def unlink(self):
        for rec in self:
            move_ids = rec.move_line_ids.mapped('move_id')
            for move in move_ids:
                move.button_cancel()
            move_ids.unlink()
        return super(PaiementEffetSupplier, self).unlink()

    def copy(self, default=None):
        if not default:
            default = {}
        default.update({
            'state': 'draft',
            'move_line_ids': [],
            # 'paiement_record_id': False,
        })
        return super(PaiementEffetSupplier, self).copy(default)

    @api.model
    def get_partner_account(self, part):
        account_id = False
        if part:
            account_id = part.property_account_payable_id.id
        return account_id

    def action_post_entries(self):
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']

        for effet in self:
            analytic = False
            move_name = ''
            if effet.state == 'draft':
                move_name = effet.name + '[LIV]'
                account_id = self.get_partner_account(effet.partner_id)
                if not account_id:
                    raise ValidationError(u'Le partenaire doit avoir un compte comptable')
                if effet.analytic_account_id:
                    analytic = effet.analytic_account_id.id
                if not effet.model_id.delivred_account.id:
                    raise ValidationError(u'Il faut définir Le compte comptable crédit')
                cred_account = effet.model_id.delivred_account.id
                deb_account = account_id

            if effet.state == 'delivred':
                move_name = effet.name + '[ENC]'
                cred_account = effet.journal_id.default_credit_account_id.id
                deb_account = effet.model_id.delivred_account.id

            debit_val = {
                # 'name': effet.name,
                'name': move_name,
                'date': effet.date,
                'date_maturity': effet.due_date,
                'ref': move_name,
                'partner_id': effet.partner_id.id,
                'account_id': deb_account,
                'credit': 0.0,
                'debit': effet.amount,
                'effet_supplier_id': effet.id,
                'journal_id': effet.journal_id.id,
                'period_id': effet.period_id.id,
                'analytic_account_id': analytic,
                'currency_id': False
            }

            credit_val = {
                # 'name': effet.name,
                'name': move_name,
                'date': effet.date,
                'date_maturity': effet.due_date,
                'ref': move_name,
                'partner_id': effet.partner_id.id,
                'account_id': cred_account,
                'credit': effet.amount,
                'debit': 0.0,
                'effet_supplier_id': effet.id,
                'journal_id': effet.journal_id.id,
                'period_id': effet.period_id.id,
                'currency_id': False
            }
            lines = [(0, 0, debit_val), (0, 0, credit_val)]
            move_id = account_move_obj.create({
                'journal_id': effet.journal_id.id,
                'period_id': effet.period_id.id,
                'date': effet.date,
                'name': move_name,
                'ref': move_name,
                # 'piece_comptable_id':'paiement.effet.supplier,'+str(effet.id)+'',
                'line_ids': lines,
            })
            move_id.post()

    def button_delivred(self):
        for effet in self:
            if effet.model_id.post:
                self.action_post_entries()
                effet.state = 'delivred'

    def button_payed(self):
        for effet in self:
            if effet.model_id.post:
                self.action_post_entries()
                effet.write({'state': 'payed', 'date_paiement': fields.date.today()})

    def button_cancel(self):
        for effet in self:
            effet.state = 'cancel'

    def button_rejected(self):
        for effet in self:
            move_new_ids = []
            move_ids = effet.move_line_ids.mapped('move_id')
            for move_line in effet.move_line_ids:
                if move_line.reconciled:
                    move_line.remove_move_reconcile()
            for move in move_ids:
                move_new_ids.append(move.copy())
            for move_obj in move_new_ids:
                for line in move_obj.line_ids:
                    credit = line.credit
                    debit = line.debit
                    line.write({'credit': debit, 'debit': credit})
                move_obj.post()
            lines = effet.move_line_ids.filtered(lambda x: x.account_id.user_type_id.type in ('receivable', 'payable'))
            lines.reconcile()
            effet.state = 'rejected'
        return True

    # @api.multi
    # def button_rejected(self):
    #     account_move_obj = self.env['account.move']
    #     account_move_line_obj = self.env['account.move.line']
    #     for effet in self:
    #         move_ids = []
    #         for line in effet.move_line_ids:
    #             move_ids.append(line.move_id)
    #         move_ids = list(set(move_ids))
    #         new_ids = []
    #         for move_id in move_ids:
    #             new_ids.append(account_move_obj.copy(move_id.id))
    #         move_objs = account_move_obj.browse(new_ids)
    #         for move_obj in move_objs:
    #             for line in move_obj.line_id:
    #                 credit = line.credit
    #                 debit = line.debit
    #                 account_move_line_obj.write(line.id, {'credit':debit, 'debit':credit})
    #         effet.state = 'rejected'

    def _get_amount_text(self):
        for rec in self:
            rec.amount_text = convertion.trad(rec.amount, 'Dh').upper()

    name = fields.Char(string=u'Numéro', required=True, states={'payed': [('readonly', True)]})
    amount = fields.Float(string='Montant', required=True, states={'payed': [('readonly', True)]})
    amount_text = fields.Char(compute='_get_amount_text', string='Montant en lettre')
    journal_id = fields.Many2one('account.journal', string=u'journal', states={'payed': [('readonly', True)]})
    model_id = fields.Many2one('paiement.effet.model.supplier', string=u'Model comptable', required=True,
                               states={'payed': [('readonly', True)]})
    date = fields.Date("Date", required=True, states={'payed': [('readonly', True)]})
    due_date = fields.Date("Echéance", required=True, states={'payed': [('readonly', True)]})
    date_paiement = fields.Date('Date paiement', readonly=True)
    note = fields.Text("Notes")
    partner_id = fields.Many2one('res.partner', 'Fournisseurs', required=True, states={'payed': [('readonly', True)]})
    move_line_ids = fields.One2many('account.move.line', 'effet_supplier_id', 'Lignes comptables',
                                    states={'payed': [('readonly', True)]})
    period_id = fields.Many2one('date.range', string=u'Période', required=True)
    caisse_id = fields.Many2one('paiement.caisse', string=u'Caisse')
    company_id = fields.Many2one('res.company', string=u'Societé', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'paiement.effet.supplier'))
    analytic_account_id = fields.Many2one('account.analytic.account', string=u'Compte analytique',
                                          states={'payed': [('readonly', True)]})
    frais_bancaire_ids = fields.One2many('frais.bancaire', 'effet_sup_id', string=u'Frais Bancaires')
    supplier_payment_id = fields.Many2one('supplier.payment', string=u'Reçu de réglement', ondelete='cascade')
    state = fields.Selection([('draft', u'Brouillon'),
                              ('delivred', u'Livré'),
                              ('payed', u'Encaissé'),
                              ('cancel', u'Annulé'),
                              ('rejected', u'Rejeté')], 'Statut', default='draft', readonly=True, required=True)


# OV
class PaiementOvSupplier(models.Model):
    _name = 'paiement.ov.supplier'
    _description = 'OV Fournisseur'
    _inherit = ['mail.thread']

    def action_post_fees(self):
        for record in self:
            for fees in record.frais_bancaire_ids:
                if fees.state == 'draft':
                    fees.create_account_lines()

    def unlink(self):
        for rec in self:
            move_ids = rec.move_line_ids.mapped('move_id')
            for move in move_ids:
                move.button_cancel()
            move_ids.unlink()
            print('testtt')
        return super(PaiementOvSupplier, self).unlink()

    def copy(self, default=None):
        if not default:
            default = {}
        default.update({
            'state': 'draft',
            'move_line_ids': [],
            # 'paiement_record_id': False,
        })
        return super(PaiementOvSupplier, self).copy(default)

    @api.model
    def get_partner_account(self, part):
        account_id = False
        if part:
            account_id = part.property_account_payable_id.id
        return account_id

    def action_post_entries(self):
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']

        for ov in self:
            analytic = False
            account_id = self.get_partner_account(ov.partner_id)
            if not account_id:
                raise ValidationError('Le partenaire doit avoir un compte comptable')
            if ov.analytic_account_id:
                analytic = ov.analytic_account_id.id
            cred_account = ov.journal_id.default_credit_account_id.id
            deb_account = account_id

            debit_val = {
                'name': ov.name,
                'date': ov.date,
                'date_maturity': ov.due_date,
                'ref': ov.note,
                'partner_id': ov.partner_id.id,
                'account_id': deb_account,
                'credit': 0.0,
                'debit': ov.amount,
                'ov_supplier_id': ov.id,
                'journal_id': ov.journal_id.id,
                'period_id': ov.period_id.id,
                'analytic_account_id': analytic,
                'currency_id': False
            }

            credit_val = {
                'name': ov.name,
                'date': ov.date,
                'date_maturity': ov.due_date,
                'ref': ov.note,
                'partner_id': ov.partner_id.id,
                'account_id': cred_account,
                'credit': ov.amount,
                'debit': 0.0,
                'ov_supplier_id': ov.id,
                'journal_id': ov.journal_id.id,
                'period_id': ov.period_id.id,
                'currency_id': False
            }
            lines = [(0, 0, debit_val), (0, 0, credit_val)]
            move_id = account_move_obj.create({
                'journal_id': ov.journal_id.id,
                'period_id': ov.period_id.id,
                'date': ov.date,
                'name': ov.name,
                'ref': ov.note,
                # 'piece_comptable_id':'paiement.ov.supplier,'+str(ov.id)+'',
                'line_ids': lines,
            }, )
            move_id.post()

    def button_done(self):
        for ov in self:
            self.action_post_entries()
            ov.write({'state': 'done', 'date_paiement': fields.date.today()})

    def button_cancel(self):
        for ov in self:
            ov.state = 'cancel'

    def button_rejected(self):
        for ov in self:
            move_new_ids = []
            move_ids = ov.move_line_ids.mapped('move_id')
            for move_line in ov.move_line_ids:
                if move_line.reconciled:
                    move_line.remove_move_reconcile()
            for move in move_ids:
                move_new_ids.append(move.copy())
            for move_obj in move_new_ids:
                for line in move_obj.line_ids:
                    credit = line.credit
                    debit = line.debit
                    line.write({'credit': debit, 'debit': credit})
                move_obj.post()
            lines = ov.move_line_ids.filtered(lambda x: x.account_id.user_type_id.type in ('receivable', 'payable'))
            lines.reconcile()
            ov.state = 'rejected'
        return True

    # @api.multi
    # def button_rejected(self):
    #     account_move_obj = self.env['account.move']
    #     account_move_line_obj = self.env['account.move.line']
    #     for ov in self:
    #         move_ids = []
    #         for line in ov.move_line_ids:
    #             move_ids.append(line.move_id)
    #         move_ids = list(set(move_ids))
    #         new_ids = []
    #         for move_id in move_ids:
    #             new_ids.append(account_move_obj.copy(move_id.id))
    #         move_objs = account_move_obj.browse(new_ids)
    #         for move_obj in move_objs:
    #             for line in move_obj.line_id:
    #                 credit = line.credit
    #                 debit = line.debit
    #                 account_move_line_obj.write(line.id, {'credit':debit, 'debit':credit})
    #         ov.state = 'rejected'

    def _get_amount_text(self):
        for rec in self:
            rec.amount_text = convertion.trad(rec.amount, 'Dh').upper()

    name = fields.Char(string=u'Numéro', readonly=True, states={'done': [('readonly', True)]})
    amount = fields.Float(string='Montant', required=True, states={'done': [('readonly', True)]})
    montant_devise = fields.Float(string='Montant en devise', required=True, states={'done': [('readonly', True)]})
    journal_id = fields.Many2one('account.journal', string='Journal', states={'done': [('readonly', True)]})
    date = fields.Date(string="Date", required=True, states={'done': [('readonly', True)]})
    due_date = fields.Date(string=u"Date d'échéance", states={'done': [('readonly', True)]})
    date_paiement = fields.Date(string=u'Date de paiement', readonly=True)
    note = fields.Text(string=u"Notes")
    partner_id = fields.Many2one('res.partner', string=u'Fournisseur', required=True,
                                 states={'done': [('readonly', True)]})
    move_line_ids = fields.One2many('account.move.line', 'ov_supplier_id', string=u'Lignes Comptables',
                                    states={'done': [('readonly', True)]})
    period_id = fields.Many2one('date.range', string=u'Période', required=True)
    caisse_id = fields.Many2one('paiement.caisse', string=u'Caisse')
    company_id = fields.Many2one('res.company', string=u'Societe', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'paiement.ov.supplier'))
    analytic_account_id = fields.Many2one('account.analytic.account', string=u'Compte Analytique',
                                          states={'done': [('readonly', True)]})
    frais_bancaire_ids = fields.One2many('frais.bancaire', 'ov_supplier_id', string=u'Frais Bancaires')
    type = fields.Selection([('Local', u'Local'), ('Etranger', u'Etranger')], string=u'Type')
    amount_provision = fields.Float(string='Montant de provision')
    date_provision = fields.Date(string=u'Date de provision')
    date_extourne = fields.Date(string=u"Date d'extourne")
    ref_fournisseur = fields.Char(string=u'Réf virement fournisseur', states={'done': [('readonly', True)]})
    supplier_payment_id = fields.Many2one('supplier.payment', string=u'Reçu de réglement', ondelete='cascade')
    state = fields.Selection([
        ('draft', u'Brouillon'),
        ('done', u'Payé'),
        ('cancel', u'Annulé'),
        ('rejected', u'Rejeté')], 'Statut', default='draft', readonly=True, required=True)


class EffetModelSupplier(models.Model):
    _name = 'paiement.effet.model.supplier'
    _description = 'Modele effet fournisseur'

    name = fields.Char('Nom', required=True)
    company_id = fields.Many2one('res.company', u'Societé',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'paiement.effet.model.supplier'))
    delivred_account = fields.Many2one('account.account', u"Fournisseur effet à payer")
    post = fields.Boolean(u'A Poster', default=True)


class FraisBancaire(models.Model):
    _name = 'frais.bancaire'
    _description = 'Frais Bancaire Fournisseur'

    def unlink(self):
        for fee in self:
            if fee.move_id:
                raise ValidationError(u"L'écriture comptable liée aux frais doit être annulée avant de procéder!")
        return super(FraisBancaire, self).unlink()

    def create_account_lines(self):
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']
        for record in self:
            journal_id = False
            period_id = False
            date = False
            name = False
            ref = False
            partner_id = False

            if record.cheque_supplier_id:
                journal_id = record.cheque_supplier_id.journal_id
                period_id = record.cheque_supplier_id.period_id.id
                date = record.cheque_supplier_id.date
                name = record.cheque_supplier_id.name
                ref = record.cheque_supplier_id.note
                partner_id = record.cheque_supplier_id.partner_id.id

            if record.ov_supplier_id:
                journal_id = record.ov_supplier_id.journal_id
                period_id = record.ov_supplier_id.period_id.id
                date = record.ov_supplier_id.date
                name = record.ov_supplier_id.name
                ref = record.ov_supplier_id.note
                partner_id = record.ov_supplier_id.partner_id.id

            if record.effet_sup_id:
                journal_id = record.effet_sup_id.journal_id
                period_id = record.effet_sup_id.period_id.id
                date = record.effet_sup_id.date
                name = record.effet_sup_id.name
                ref = record.effet_sup_id.note
                partner_id = record.effet_sup_id.partner_id.id

            debit_val = {
                'name': name,
                'date': date,
                'partner_id': partner_id,
                'account_id': record.account_id.id,
                'credit': 0.0,
                'debit': record.amount,
                'journal_id': journal_id.id,
                'period_id': period_id,
            }
            credit_val = {
                'name': name,
                'date': date,
                'partner_id': partner_id,
                'account_id': journal_id.default_credit_account_id.id,
                'credit': record.amount,
                'debit': 0.0,
                'journal_id': journal_id.id,
                'period_id': period_id,
            }
            lines = [(0, 0, debit_val), (0, 0, credit_val)]
            move_id = account_move_obj.create({
                'journal_id': journal_id.id,
                'period_id': period_id,
                'date': date,
                'name': name,
                'ref': ref,
                'line_ids': lines,
            })
            move_id.post()
            record.write({'state': 'done', 'move_id': move_id.id})

    name = fields.Char(string=u'Réference')
    move_id = fields.Many2one('account.move', string=u'Ecriture comptable', readonly=True)
    amount = fields.Float(string=u'Montant', required=True)
    account_id = fields.Many2one('account.account', u'Compte de charge', required=True)
    cheque_supplier_id = fields.Many2one('paiement.cheque.supplier', u'Chèque Fournisseur')
    ov_supplier_id = fields.Many2one('paiement.ov.supplier', string=u'OV Fournisseur')
    effet_sup_id = fields.Many2one('paiement.effet.supplier', string=u'Effet Fournisseur')
    state = fields.Selection([
        ('draft', u'Brouillon'),
        ('done', u'Validé'), ], 'Statut', default='draft', readonly=True, required=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cash_supplier_id = fields.Many2one('paiement.cash.supplier', u'Cash fournisseur')
    cheque_supplier_id = fields.Many2one('paiement.cheque.supplier', u'Chèque fournisseur')
    ov_supplier_id = fields.Many2one('paiement.ov.supplier', u'OV fournisseur')
    effet_supplier_id = fields.Many2one('paiement.effet.supplier', u'Effet fournisseur')
    period_id = fields.Many2one('date.range', string=u'Période', required=False)


class AccountMove(models.Model):
    _inherit = 'account.move'

    period_id = fields.Many2one('date.range', string=u'Période', required=False)
