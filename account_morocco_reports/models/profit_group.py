""" init object profit.group """

import logging

from odoo import fields, models

LOGGER = logging.getLogger(__name__)


class ProfitGroup(models.Model):
    """ init object profit.group """

    _name = 'profit.group'
    _description = 'profit.group'
    _order = 'sequence asc'
    _inherit = 'assets.group'

    line_ids = fields.One2many(comodel_name="profit.line",
                               inverse_name="group_id",
                               string="Lines", required=False, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="profit_group_account_rel",
                                   column1="group_id", column2="account_id",
                                   string="Accounts Column #1", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="profit_group_account_rel_2",
                                    column1="group_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="profit_group_subtraction_account_rel",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="profit_group_subtraction_account_rel_2",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
    period_fiscal_year = fields.Boolean(
        string="The periods starts from the fiscal year?",
    )

class ProfitLine(models.Model):
    """ init object profit.line """

    _name = 'profit.line'
    _description = 'profit.line'
    _inherit = 'assets.line'
    _order = 'sequence asc'

    group_id = fields.Many2one(comodel_name="profit.group", string="Group",
                               required=True, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="profit_line_account_rel",
                                   column1="line_id", column2="account_id",
                                   string="Accounts Column #1", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="profit_line_account_rel_2",
                                    column1="line_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="profit_line_subtraction_account_rel",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="profit_line_subtraction_account_rel_2",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
