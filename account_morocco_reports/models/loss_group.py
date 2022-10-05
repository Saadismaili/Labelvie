""" init object loss.group """

import logging

from odoo import fields, models

LOGGER = logging.getLogger(__name__)


class LossGroup(models.Model):
    """ init object loss.group """

    _name = 'loss.group'
    _description = 'loss.group'
    _order = 'sequence asc'
    _inherit = 'profit.group'

    line_ids = fields.One2many(comodel_name="loss.line",
                               inverse_name="group_id",
                               string="Lines", required=False, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="loss_group_account_rel",
                                   column1="group_id", column2="account_id",
                                   string="Accounts Column #1", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="loss_group_account_rel_2",
                                    column1="group_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="loss_group_subtraction_account_rel",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="loss_group_subtraction_account_rel_2",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
    period_fiscal_year = fields.Boolean(
        string="The periods starts from the fiscal year?",
    )


class LossLine(models.Model):
    """ init object loss.line """

    _name = 'loss.line'
    _description = 'loss.line'
    _inherit = 'profit.line'
    _order = 'sequence asc'

    group_id = fields.Many2one(comodel_name="loss.group", string="Group",
                               required=True, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="loss_line_account_rel",
                                   column1="line_id", column2="account_id",
                                   string="Accounts Column #1", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="loss_line_account_rel_2",
                                    column1="line_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="loss_line_subtraction_account_rel",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="loss_line_subtraction_account_rel_2",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
