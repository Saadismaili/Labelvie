# -*- coding: utf-8 -*-

from odoo import models, api,fields , _
from odoo.exceptions import ValidationError


class inter_move(models.TransientModel):

    _name = "account.inter.move"
    _description = "Account inter move"

    journal_id = fields.Many2one('account.journal', 'Journal',
                                 domain=[('type', 'in', ('cash', 'bank'))],
                                 required=True)
    date = fields.Date("Date d'eancaissement", required=True, default=fields.Date.context_today)

    def create_move(self):
        move_obj = self.env['account.move']
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        move_ids = move_obj.browse(active_ids)
        for move in move_ids:
            origin_move_line_id = False
            if move.origin_move_line_id:
                origin_move_line_id = move.origin_move_line_id
            else:
                origin_move_line_id = move
            reversed_move = move.copy(default={'date': self.date,
                                               'journal_id': self.journal_id.id,
                                               'ref': move.ref,
                                               'origin_move_line_id': origin_move_line_id.id})
            for acm_line in reversed_move.line_ids:
                account_id = acm_line.account_id
                deb_acc = move.journal_id.default_debit_account_id
                cred_acc = move.journal_id.default_account_id

                if acm_line.account_id == deb_acc:
                    account_id = self.journal_id.default_account_id
                elif acm_line.account_id == cred_acc:
                    account_id = self.journal_id.default_account_id
                else:
                    if not deb_acc or not cred_acc:
                        raise ValidationError(
                            u'Merci de définir des comptes de débit et de crédit par défaut'
                            u' du journal de la pièce comptable')
                    if acm_line.debit > 0:
                        account_id = deb_acc
                    if acm_line.credit > 0:
                        account_id = cred_acc
                acm_line.with_context(check_move_validity=False).write({
                        'account_id': account_id.id,
                        'name': move.ref or move.name
                })
            move_obj |= reversed_move
            if move_obj:
                move_obj._post_validate()
                move_obj.post()
