""" init object loss.group """

import logging

from odoo import fields, models

LOGGER = logging.getLogger(__name__)


class PassageGroup(models.Model):
    """ init object passage.group """

    _name = 'passage.group'
    _description = 'passage.group'
    _order = 'sequence asc'
    _inherit = 'profit.group'

    line_ids = fields.One2many(comodel_name="passage.line",
                               inverse_name="group_id",
                               string="Lines", required=False, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="passage_group_account_rel",
                                   column1="group_id", column2="account_id",
                                   string="Accounts Column #1", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="passage_group_account_rel_2",
                                    column1="group_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="passage_group_subtraction_account_rel",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="passage_group_subtraction_account_rel_2",
        column1="group_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
    period_fiscal_year = fields.Char(
        string="Corresponding disallowed code",
    )
    
    period_fiscal_year_year  = fields.Boolean(
        string="The periods starts from the fiscal year?",
    )
    
    previous_fiscal_year  = fields.Boolean(
        string="The periods starts from the previous fiscal year?",
    )
    
    


class PassageLine(models.Model):
    """ init object passage.line """

    _name = 'passage.line'
    _description = 'passage.line'
    _inherit = 'profit.line'
    _order = 'sequence asc'

    group_id = fields.Many2one(comodel_name="passage.group", string="Group",
                               required=True, )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="passage_line_account_rel",
                                   column1="line_id", column2="account_id",
                                   string="Accounts Column #1", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="passage_line_account_rel_2",
                                    column1="line_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="passage_line_subtraction_account_rel",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="passage_line_subtraction_account_rel_2",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
    
    period_fiscal_year = fields.Char(
        string="Corresponding disallowed code",
    )
    
    period_fiscal_year_year  = fields.Boolean(
        string="The periods starts from the fiscal year?",
    )
    
    specific_line_type = fields.Selection(string='Specific Line type', selection=[('perte', 'Perte'),('benifice', 'Bénifice'),('perte_brut', 'Perte Brut'),('benifice_brut', 'Bénifice Brut'),('perte_net', 'Perte Net'),('benifice_net', 'Bénifice Net')])
    
    specific_year  = fields.Selection(string='Specific Year', selection=[('1', 'N-1'),('2', 'N-2'),('3', 'N-3'),('4', 'N-4')])
    rapport_specific_year  = fields.Selection(string='Specific Rapport Year', selection=[('1', 'N-1'),('2', 'N-2'),('3', 'N-3'),('4', 'N-4')])
