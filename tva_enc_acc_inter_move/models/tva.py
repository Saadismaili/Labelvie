# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class TvaDeclaration(models.Model):
    _inherit = "tva.declaration"

    def generate_liquidity_moves(self, move):
        move_pay_ids = super(TvaDeclaration, self).generate_liquidity_moves(move)
        for move_line in move.line_ids:
            move_line_partner_id = False
            if move_line.effet_client_id:
                move_line_partner_id = move_line.effet_client_id.move_line_ids \
                    .filtered(lambda r: r.account_id.user_type_id.type == 'receivable')
            elif move_line.cheque_client_id:
                move_line_partner_id = move_line.cheque_client_id.move_line_ids \
                    .filtered(lambda r: r.account_id.user_type_id.type == 'receivable')
            if move_line_partner_id:
                move_line_partner_id = move_line_partner_id[0]
                if move_line_partner_id.debit > 0:
                    reconcial_ids = self.env['account.partial.reconcile'].search(
                        [('debit_move_id', '=', move_line_partner_id.id)])
                    if reconcial_ids:
                        for rec in reconcial_ids:
                            move_pay_ids.append([rec.credit_move_id, rec.amount])
                if move_line_partner_id.credit > 0:
                    reconcial_ids = self.env['account.partial.reconcile'].search(
                        [('credit_move_id', '=', move_line_partner_id.id)])
                    if reconcial_ids:
                        for rec in reconcial_ids:
                            move_pay_ids.append([rec.debit_move_id, rec.amount])
        if move.origin_move_line_id:
            for line in move.origin_move_line_id.line_ids:
                if line.debit > 0:
                    reconcial_ids = self.env['account.partial.reconcile'].search(
                        [('debit_move_id', '=', line.id)])
                    if reconcial_ids:
                        for rec in reconcial_ids:
                            move_pay_ids.append([rec.credit_move_id, rec.amount])
                if line.credit > 0:
                    reconcial_ids = self.env['account.partial.reconcile'].search(
                        [('credit_move_id', '=', line.id)])
                    if reconcial_ids:
                        for rec in reconcial_ids:
                            move_pay_ids.append([rec.debit_move_id, rec.amount])
        return move_pay_ids


