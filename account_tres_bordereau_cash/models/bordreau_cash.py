# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    bordereau_cash_id = fields.Many2one('paiement.bordereau.cash', 'Bordereau cash')


class PaiementCashClient(models.Model):
    _inherit = "paiement.cash.client"

    bordereau_cash_id = fields.Many2one('paiement.bordereau.cash', 'Bordereau cash', copy=False)

    def unlink(self):
        for rec in self:
            if rec.bordereau_cash_id and rec.bordereau_cash_id.state != 'draft':
                raise ValidationError('Vous ne pouvez pas supprimer une pièce ajoutée à un bordereau validé')
            move_ids = rec.move_line_ids.mapped('move_id')
            move_ids.button_cancel()
            move_ids.unlink()
        return super(PaiementCashClient, self).unlink()


class PaiementBordereauCash(models.Model):
    _name = 'paiement.bordereau.cash'
    _description = 'Bordereau'

    @api.depends('cash_lines')
    def _calc_total_amount(self):
        for rec in self:
            rec.total = sum(rec.cash_lines and rec.cash_lines.mapped('amount'))
            rec.total_amount = sum(cash.amount for cash in rec.cash_lines if cash.state in ('caisse', 'done'))
            rec.nb_cash = len(rec.cash_lines)

    name = fields.Char(string=u'Numéro', required=True)
    # period_id = fields.Many2one('account.period', string=u'Période' ,required=True)
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                 default=lambda self: self.env.user.company_id)
    cash_lines = fields.One2many('paiement.cash.client', 'bordereau_cash_id', string=u'Espèces', copy=False)
    date = fields.Date(string=u'Date', required=True)
    courssier_id = fields.Many2one('res.users', string=u'Coursier')
    journal_id = fields.Many2one('account.journal', string=u'Journal Banque', required=True, domain=[('type', '=', 'bank')])
    total_amount = fields.Float(compute='_calc_total_amount', string=u'Montant total encaissé')
    total = fields.Float(compute='_calc_total_amount', string=u'Montant total')

    nb_cash = fields.Integer(compute='_calc_total_amount', string=u'Nombre des espèces')
    date_encaissement = fields.Date(string=u'Date encaissement')
    state = fields.Selection([('draft', 'Brouillon'), ('bordereau', 'Bordereau'), ('done', u'Validé')], string='Etat',
                             default='draft', readonly=True, required=True)
    move_lines = fields.One2many('account.move.line', 'bordereau_cash_id', 'Ecritures Comptables')

    def valider_bordereau(self):
        account_move_obj = self.env['account.move']
        for record in self:
            for ch in record.cash_lines:
                ch.action_caisse_centrale()
                ch.caisse_id = None
                debit_val1 = {
                    'name': ch.name,
                    'date': ch.date,
                    'ref': ch.note,
                    'partner_id': ch.client.id,
                    'account_id': ch.journal_id.default_account_id.id,
                    'credit': ch.amount,
                    'debit': 0.0,
                    'cash_client_id': ch.id,
                    'bordereau_cash_id': record.id,
                    'journal_id': ch.journal_id.id,
                    'analytic_account_id': ch.analytic_account_id and ch.analytic_account_id.id or False,
                    'currency_id': False
                }

                credit_val1 = {
                    'name': ch.name,
                    'date': ch.date,
                    'ref': ch.note,
                    'partner_id': ch.client.id,
                    'account_id': ch.company_id.transfer_account_id.id,
                    'credit': 0.0,
                    'debit': ch.amount,
                    'cash_client_id': ch.id,
                    'bordereau_cash_id': record.id,
                    'journal_id': ch.journal_id.id,
                    'currency_id': False
                }
                lines = [(0, 0, debit_val1), (0, 0, credit_val1)]
                move_id = account_move_obj.create({
                    'journal_id': record.journal_id.id,
                    'date': record.date,
                    'name': record.name,
                    'line_ids': lines,
                })
                ch.write({'journal_id': record.journal_id.id})
            record.write({'state': 'bordereau'})

        return True

    def encaisser_cash(self):
        account_move_obj = self.env['account.move']
        if not self.date_encaissement:
            raise UserError(u"Il faut renseigner la date d'encaissement avant la validation")
        for ch in self.cash_lines:
            ch.action_done()
            ch.caisse_id = None

            debit_val2 = {
                'name': ch.name,
                'date': self.date_encaissement,
                'ref': ch.note,
                'partner_id': ch.client.id,
                'account_id': ch.company_id.transfer_account_id.id,
                'credit': ch.amount,
                'debit': 0.0,
                'cash_client_id': ch.id,
                'bordereau_cash_id': self.id,
                'journal_id': self.journal_id.id,
                'analytic_account_id': ch.analytic_account_id and ch.analytic_account_id.id or False,
                'currency_id': False
            }

            credit_val2 = {
                'name': ch.name,
                'date': self.date_encaissement,
                'ref': ch.note,
                'partner_id': ch.client.id,
                'account_id': self.journal_id.default_account_id.id,
                'credit': 0.0,
                'debit': ch.amount,
                'cash_client_id': ch.id,

                'bordereau_cash_id': self.id,
                'journal_id': self.journal_id.id,
                'currency_id': False
            }
            lines = [(0, 0, debit_val2), (0, 0, credit_val2)]
            move_id = account_move_obj.create({
                'journal_id': self.journal_id.id,
                'date': self.date,
                'name': self.name,
                'line_ids': lines,
            })
            ch.write({'journal_id': self.journal_id.id})
            if move_id:
                move_id.post()
        self.write({'state': 'done'})

    def action_post_fees(self):
        for record in self:
            for fees in record.tres_fees_ids:
                if fees.state == 'draft':
                    fees.create_account_lines()

    def back_to_draft(self):
        cash = self.env['account.journal'].search([('type', '=', 'cash')], limit=1)
        for record in self:
            move_ids = []
            for l in record.cash_lines:
                for mv in l.move_line_ids:
                    mv.remove_move_reconcile()
                    move_ids.append(mv.move_id.id)

                l.move_line_ids.unlink()
                l.write({'state':'draft'})
                if cash:
                    l.journal_id = cash[0].id
                l.action_caisse()
            for line in record.move_lines:
                line.remove_move_reconcile()
                move_ids.append(line.move_id.id)

            record.move_lines.unlink()
            self.env['account.move'].browse(move_ids).unlink()
            record.write({'state': 'draft'})
        return True
