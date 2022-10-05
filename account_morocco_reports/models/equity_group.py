""" init object equity.group """

import logging

from odoo import fields, models

LOGGER = logging.getLogger(__name__)

DEFAULT_PYTHON_CODE = """
# Available variables:
#  - env: Odoo Environment on which the action is triggered
# To return an results: results = [(...),(...) ..]
# The Row Data in result: (Name, Value)
results = [('Name#1', 1), ('Name#2', 2), ('Name#3', 3)]
\n\n\n\n"""


class EquityGroup(models.Model):
    """ init object equity.group """

    _name = 'equity.group'
    _description = 'equity.group'
    _order = 'sequence asc'
    _inherit = 'assets.group'

    line_ids = fields.One2many(comodel_name="equity.line",
                               inverse_name="group_id",
                               string="Lines", required=False, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="equity_group_account_rel",
                                   column1="group_id", column2="account_id",
                                   string="Accounts", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="equity_group_account_rel_2",
                                    column1="line_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="equity_group_subtraction_account_rel",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="equity_group_subtraction_account_rel_2",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
    period_fiscal_year = fields.Boolean(
        string="The periods starts from the fiscal year?",
    )


class EquityLine(models.Model):
    """ init object equity.line """

    _name = 'equity.line'
    _description = 'equity.line'
    _inherit = 'assets.line'
    _order = 'sequence asc'

    group_id = fields.Many2one(comodel_name="equity.group", string="Group",
                               required=True, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="equity_line_account_rel",
                                   column1="line_id", column2="account_id",
                                   string="Accounts", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="equity_line_account_rel_2",
                                    column1="line_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="equity_line_subtraction_account_rel",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="equity_line_subtraction_account_rel_2",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
    code = fields.Char(default=DEFAULT_PYTHON_CODE)
