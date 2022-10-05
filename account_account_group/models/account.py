# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.move.line'

    group_id = fields.Many2one(related="account_id.group_id", string="Poste", store=True)

