""" init object esg.caf.group """

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


class TFRGroup(models.Model):
    """ init object esg.tfr.group """

    _name = 'esg.caf.group'
    _description = 'esg.caf.group'
    _order = 'sequence asc'
    _inherit = 'esg.tfr.group'

    line_ids = fields.One2many(comodel_name="esg.caf.line",
                               inverse_name="group_id",
                               string="Lines", required=False, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="esg_caf_group_account_rel",
                                   column1="group_id", column2="account_id",
                                   string="Accounts", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="esg_caf_group_account_rel_2",
                                    column1="line_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="esg_caf_group_subtraction_account_rel",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="esg_caf_group_subtraction_account_rel_2",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
    period_fiscal_year = fields.Boolean(
        string="The periods starts from the fiscal year?",
    )


class TFRLine(models.Model):
    """ init object esg.caf.line """

    _name = 'esg.caf.line'
    _description = 'esg.caf.line'
    _inherit = 'esg.tfr.line'
    _order = 'sequence asc'

    group_id = fields.Many2one(comodel_name="esg.caf.group", string="Group",
                               required=True, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="esg_caf_line_account_rel",
                                   column1="line_id", column2="account_id",
                                   string="Accounts", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="esg_caf_line_account_rel_2",
                                    column1="line_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="esg_caf_line_subtraction_account_rel",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="esg_caf_line_subtraction_account_rel_2",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
    code = fields.Char(default=DEFAULT_PYTHON_CODE)