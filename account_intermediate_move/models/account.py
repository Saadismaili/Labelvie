# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class account_invoice_tax(models.Model):
    _inherit = "account.move"

    origin_move_line_id = fields.Many2one('account.move', string='Mouvement CL/FR origine', readonly=True)



