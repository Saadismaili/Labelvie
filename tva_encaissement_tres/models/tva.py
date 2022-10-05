# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class TvaDeclaration(models.Model):
    _inherit = "tva.declaration"

    def generate_liquidity_moves(self, move):
        move_pay_ids = super(TvaDeclaration, self).generate_liquidity_moves(move)
        for move_line in move.line_ids:
            # print('move_line.account_id', move_line.account_id.code, move_line.account_id.user_type_id.type)
            if move_line.account_id.user_type_id.type == 'liquidity':
                move_line_partner_id = False
                if move_line.effet_client_id:
                    move_line_partner_id = move_line.effet_client_id.move_line_ids\
                                            .filtered(lambda r: r.account_id.user_type_id.type == 'receivable')
                elif move_line.cheque_client_id:
                    move_line_partner_id = move_line.cheque_client_id.move_line_ids\
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
        return move_pay_ids

    # Get Payment Type
    def get_payment(self, move):
        paiement_type = super(TvaDeclaration, self).get_payment(move)
        payment_methode = self.env['payement.method']
        cheque = payment_methode.search([('name', '=', 'Chèque')], limit=1)
        effet = payment_methode.search([('name', '=', 'Effet')], limit=1)
        ov = payment_methode.search([('name', '=', 'Virement')], limit=1)
        cash = payment_methode.search([('name', '=', 'Espèce')], limit=1)
        move_lines = move.mapped('line_ids')
        if cheque and (move_lines.mapped('cheque_client_id') or move_lines.mapped('cheque_supplier_id')):
            paiement_type = cheque.id
        if effet and (move_lines.mapped('effet_client_id') or move_lines.mapped('effet_supplier_id')):
            paiement_type = effet.id
        if ov and (move_lines.mapped('ov_client_id') or move_lines.mapped('ov_supplier_id')):
            paiement_type = ov.id
        if cash and (move_lines.mapped('cash_client_id') or move_lines.mapped('cash_supplier_id')):
            paiement_type = cash.id
        # print('mmmmmmmm',move, paiement_type)
        return paiement_type