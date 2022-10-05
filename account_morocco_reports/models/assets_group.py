""" init object assets.group """

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr

LOGGER = logging.getLogger(__name__)

TYPES = [('same', 'The same sign'),
         ('reversed', 'The sign is reversed'),
         ('negative', 'The sign is negative'),
         ('positive', 'The sign is positive'), ]

DEFAULT_PYTHON_CODE = """
# Available variables:
#  - env: Odoo Environment on which the action is triggered
# To return an results: results = [(...),(...) ..]
# The Row Data in result: (Name, Value#1, Value#2, Value#3)
results = [('Name#1', 1, 2, 3), ('Name#2', 4, 5, 9), ('Name#3', 7, 8, 15)]
\n\n\n\n"""


class AssetsGroup(models.Model):
    """ init object assets.group """

    _name = 'assets.group'
    _description = 'assets.group'
    _order = 'sequence asc'

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, )
    line_ids = fields.One2many(comodel_name="assets.line",
                               inverse_name="group_id",
                               string="Lignes", required=False, )
    group_type = fields.Selection(default='lines', required=True,
                                  selection=[('lines', 'Lines'),
                                             ('one_line', 'One Line'),
                                             ('sum', 'Sum'), ])
    value_type = fields.Selection(default="same", required=True,
                                  selection=TYPES)
    view_type = fields.Selection(default="same", required=True, selection=TYPES)
    account_source_method = fields.Selection(
        default="accounts", required=True,
        selection=[('accounts', 'Comptes spécifiques'),
                   ('domain', 'Domain'), ]
    )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="assets_group_account_rel",
                                   column1="group_id", column2="account_id",
                                   string="Comptes du Colonne #1", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="assets_group_account_rel_2",
                                    column1="group_id", column2="account_id",
                                    string="Comptes du Colonne #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="assets_group_subtraction_account_rel",
        column1="group_id", column2="account_id",
        string=" Comptes de soustraction Colonne #1",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="assets_group_subtraction_account_rel_2",
        column1="group_id", column2="account_id",
        string=" Comptes de soustraction Colonne #2",
    )
    accounts_domain = fields.Char(string="Domaine des comptes Colonne #1")
    accounts2_domain = fields.Char(string="Domaine des comptes Colonne #2")
    subtraction_accounts_domain = fields.Char(
        string="Domaine des Comptes de soustraction  Colonne #1",
        default='[("id", "=", 0)]',
    )
    subtraction_accounts2_domain = fields.Char(
        string="Domaine des Comptes de soustraction Column #2",
        default='[("id", "=", 0)]',
    )
    summation_domain = fields.Char(default='[("id", "=", 0)]')
    subtraction_domain = fields.Char(default='[("id", "=", 0)]')
    left_char = fields.Char()
    period_fiscal_year = fields.Boolean(
        string="Les périodes commencent à partir de l'exercice?",
    )


class AssetsLine(models.Model):
    """ init object assets.line """

    _name = 'assets.line'
    _description = 'assets.line'
    _order = 'sequence asc'

    def get_accounts(self):
        """
        Get All Accounts
        :return: account_ids, sub_account_ids
        """
        account_ids = sub_account_ids = acc_obj = self.env['account.account']
        account_ids |= self.mapped('account_ids')
        account_ids |= self.mapped('account2_ids')
        sub_account_ids |= self.mapped('subtraction_account_ids')
        sub_account_ids |= self.mapped('subtraction_account2_ids')
        for line in self:
            if line.accounts_domain:
                account_ids |= acc_obj.search(safe_eval(line.accounts_domain))
            if line.accounts2_domain:
                account_ids |= acc_obj.search(safe_eval(line.accounts2_domain))
            if line.subtraction_accounts_domain:
                sub_account_ids |= acc_obj.search(safe_eval(
                    line.subtraction_accounts_domain))
            if line.subtraction_accounts2_domain:
                sub_account_ids |= acc_obj.search(safe_eval(
                    line.subtraction_accounts2_domain))
        return account_ids, sub_account_ids

    @api.constrains('code')
    def _check_python_code(self):
        """
        Check_python_code
        """
        for rec in self.sudo().filtered('code'):
            msg = test_python_expr(expr=rec.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    # pylint: disable=inconsistent-return-statements
    def run_code(self):
        """
        Run Python Code
        :return: eval_context['results'] list of data
        Example: [('Name#1', 1, 2, 3), ('Name#2', 4, 5, 9), ... ]
        """
        self.ensure_one()
        eval_context = {
            'record': self,
            'env': self.env,
            'context': self.env.context.copy()
        }
        safe_eval(self.code.strip(), eval_context, mode="exec",
                  nocopy=True)
        if 'results' in eval_context:
            return eval_context['results']

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, )
    group_id = fields.Many2one(comodel_name="assets.group", string="Group",
                               required=True, )
    value_type = fields.Selection(default="same", required=True,
                                  selection=TYPES)
    view_type = fields.Selection(default="same", required=True, selection=TYPES)
    account_source_method = fields.Selection(
        default="accounts", required=True,
        selection=[('accounts', 'Specific Accounts'),
                   ('domain', 'Domain'),
                   ('code', 'Python Code'), ]
    )
    account_ids = fields.Many2many(comodel_name="account.account",
                                   relation="assets_line_account_rel",
                                   column1="line_id", column2="account_id",
                                   string="Accounts Column #1", )
    account2_ids = fields.Many2many(comodel_name="account.account",
                                    relation="assets_line_account_rel_2",
                                    column1="line_id", column2="account_id",
                                    string="Accounts Column #2", )
    subtraction_account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="assets_line_subtraction_account_rel",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts Column #1",
    )
    subtraction_account2_ids = fields.Many2many(
        comodel_name="account.account",
        relation="assets_line_subtraction_account_rel_2",
        column1="line_id", column2="account_id",
        string="Subtraction Accounts Column #2",
    )
    accounts_domain = fields.Char(string="Accounts Domain Column #1")
    accounts2_domain = fields.Char(string="Accounts Domain Column #2")
    subtraction_accounts_domain = fields.Char(
        string="Subtraction Accounts Domain Column #1",
        default='[("id", "=", 0)]',
    )
    subtraction_accounts2_domain = fields.Char(
        string="Subtraction Accounts Domain Column #2",
        default='[("id", "=", 0)]',
    )
    code = fields.Char(default=DEFAULT_PYTHON_CODE)
    left_char = fields.Char()
    disable_sum_group = fields.Boolean()
    period_fiscal_year = fields.Boolean(
        string="Les périodes commencent à partir de l'exercice ?",
    )
