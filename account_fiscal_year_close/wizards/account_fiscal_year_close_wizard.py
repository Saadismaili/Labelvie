# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError, UserError


class AccountFiscalYearClose(models.TransientModel):
    _name = "account.fiscalyear.close"
    _description = "Fiscalyear Close"

    fy_id = fields.Many2one('date.range', u'Exercice à fermer', required=True)
    fy2_id = fields.Many2one('date.range', u'Nouvel exercice', required=True)
    journal_id = fields.Many2one('account.journal', u"Journal d'ouverture", domain="[('type','=','situation')]", required=True)
    report_name = fields.Char('Nom', required=True)

    @api.onchange('fy_id')
    def onchange_fy_id(self):
        self.fy2_id = self.fy_id.next_fiscal_year.id

    # @api.multi
    def data_save(self):
        cr = self._cr
        """
        This function close account fiscalyear and create entries in new fiscalyear
        """

        obj_acc_move = self.env['account.move']
        obj_acc_move_line = self.env['account.move.line']

        name = self.report_name
        new_fyear = self.fy2_id
        old_fyear = self.fy_id
        new_journal = self.journal_id
        company_id = new_journal.company_id.id

        if not new_fyear:
            raise UserError(u"Merci de définir le nouvel exercice")

        if not new_journal.default_credit_account_id or not new_journal.default_debit_account_id:
            raise UserError(u"Merci de définir les comptes débit et crédit dans le journal d'ouverture")

        # delete existing move and move lines if any
        move_ids = obj_acc_move.search([('journal_id', '=', new_journal.id), ('date', '=', new_fyear.date_start)])
        for move in move_ids:
            cr.execute('''
            UPDATE account_move_line
            SET  reconciled = 'f'
            WHERE move_id = %s
            ''',
            (move.id,))
        if move_ids:
            move_line_ids = obj_acc_move_line.search([('move_id', 'in', move_ids.ids)])
            move_line_ids.unlink()
            move_ids.unlink()

        # create the opening move
        vals = {
            'name': '/',
            'ref': self.report_name,
            'date': new_fyear.date_start,
            'journal_id': new_journal.id,
            'company_id': company_id,
        }
        move_id = obj_acc_move.create(vals)
        # 1. report of the accounts with defferal method == 'unreconciled'
        cr.execute('''
            SELECT a.id
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type_id = t.id)
            WHERE
                a.company_id = %s
                AND t.close_method = %s''', (company_id, 'unreconciled',))
        account_ids = map(lambda x: x[0], cr.fetchall())
        if account_ids:
            cr.execute('''
                INSERT INTO account_move_line (
                     name,
                     journal_id,
                     partner_id,
                     credit,
                     debit,
                     balance,
                     account_id,
                     date,
                     date_maturity,
                     move_id,
                     company_id)
                  (SELECT
                          %s,
                          %s,
                          partner_id,
                          CASE
                            WHEN (sum(debit)-sum(credit)<0) THEN sum(credit)-sum(debit)
                            ELSE 0
                          END,
                          CASE
                            WHEN (sum(debit)-sum(credit)>0) THEN sum(debit)-sum(credit)
                            ELSE 0
                          END,
                          sum(debit)-sum(credit),
                          account_id,
                          (%s) AS date,
                          (%s) AS date_maturity,
                          %s,
                          company_id
                    FROM account_move_line
                    WHERE account_id IN %s
                     AND date >= %s
                     AND date <= %s
                    GROUP BY account_id,partner_id,company_id
                     )''',
                       (name, new_journal.id, new_fyear.date_start, new_fyear.date_start, move_id.id, tuple(account_ids), old_fyear.date_start, old_fyear.date_end,))

            self.invalidate_cache()

        # 2. report of the accounts with defferal method == 'balance'
        cr.execute('''
            SELECT a.id
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type_id = t.id)
            WHERE
                a.company_id = %s
                AND t.close_method = %s''', (company_id, 'balance',))
        account_ids = map(lambda x: x[0], cr.fetchall())
        if account_ids:
            cr.execute('''
                INSERT INTO account_move_line (
                     name,journal_id,credit,debit,balance,account_id,date,date_maturity,move_id,company_id)
                  (SELECT
                        %s,
                        %s,
                        CASE
                            WHEN (sum(debit)-sum(credit)<0) THEN sum(credit)-sum(debit)
                            ELSE 0
                        END,
                        CASE
                            WHEN (sum(debit)-sum(credit)>0) THEN sum(debit)-sum(credit)
                            ELSE 0
                        END,
                        sum(debit)-sum(credit),
                        account_id,
                        (%s) AS date,
                        (%s) AS date_maturity,
                        %s,
                        %s
                  FROM account_move_line
                  WHERE account_id IN %s
                     AND date >= %s
                     AND date <= %s
                  GROUP BY account_id)''',
                       (name, new_journal.id, new_fyear.date_start, new_fyear.date_start, move_id.id, company_id,
                        tuple(account_ids), old_fyear.date_start, old_fyear.date_end,))

        # 3. report of the accounts with defferal method == 'none'
        cr.execute('''
            SELECT a.id
            FROM account_account a
            LEFT JOIN account_account_type t ON (a.user_type_id = t.id)
            WHERE
                a.company_id = %s
                AND t.close_method in %s''', (company_id, ('balance', 'unreconciled'),))
        account_ids = map(lambda x: x[0], cr.fetchall())
        if account_ids:
            cr.execute('''
                  SELECT
                        sum(debit) - sum(credit)
                  FROM  account_move_line
                  WHERE account_id IN %s
                        AND date >= %s
                        AND date <= %s
                  ''',
                       (tuple(account_ids), old_fyear.date_start, old_fyear.date_end,))
        solde = 0.0
        query_res = cr.fetchone()
        if query_res != None:
            solde = query_res[0]
        if solde:
            if solde > 0.0:
                debit = 0.0
                credit = abs(solde)
                account_id = new_journal.default_credit_account_id.id
            else:
                debit = abs(solde)
                credit = 0.0
                account_id = new_journal.default_debit_account_id.id
            cr.execute('''
                                INSERT INTO account_move_line (
                                     name,
                                     journal_id,
                                     credit,
                                     debit,
                                     balance,
                                     account_id,
                                     date,
                                     date_maturity,
                                     move_id,
                                     company_id)
                                VALUES(%s,
                                      %s,
                                      %s,
                                      %s,
                                      %s,
                                      %s,
                                      (%s),
                                      (%s),
                                      %s,
                                      %s)
                             ''',
                       (name, new_journal.id, credit, debit, debit - credit, account_id, new_fyear.date_start,
                        new_fyear.date_start, move_id.id, company_id))

        # Delete account move with debit and credit == 0
        cr.execute('''
                          DELETE
                          FROM  account_move_line
                          WHERE move_id = %s AND debit = 0 and credit = 0
                          ''',
                   (move_id.id,))

        cr.execute('''
                     UPDATE account_move_line
                     SET  reconciled = 't'
                     WHERE move_id = %s
                    ''',
                   (move_id.id,))
        return {'type': 'ir.actions.act_window_close'}
