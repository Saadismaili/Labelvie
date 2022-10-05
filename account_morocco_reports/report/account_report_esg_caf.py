""" init py report account.report.esg.caf """

import ast
import json

import io
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import format_date
from odoo.tools.misc import xlsxwriter
from odoo.tools.safe_eval import safe_eval


# pylint: disable=no-member, unused-argument, consider-using-ternary
# pylint: disable=no-self-use, unused-variable, redefined-outer-name
# pylint: disable=too-many-arguments, too-many-locals, protected-access
# pylint: disable=too-many-nested-blocks
class AccountReportEGSCAF(models.AbstractModel):
    """ init py report account.report.esg.caf """
    _name = "account.report.esg.caf"
    _description = "account.report.esg.caf"
    _inherit = "account.report.esg.tfr"
    _group_model = 'esg.caf.group'

    @api.model
    def _get_report_name(self):
        """
        Override  _get_report_name
        """
        return _("ESG CAF")

    @api.model
    def _get_lines(self, options, line_id=None):
        """
        Override function _get_lines
        """
        # Create new options with 'unfold_all' to compute the initial balances.
        # Then, the '_do_query' will compute
        # all sums/unaffected earnings/initial balances for all comparisons.
        lines = []
        ctx = self.env.context.copy()
        number_of_columns = self._number_of_columns or 2
        min_python_value_numbers = 4
        if number_of_columns == 1:
            min_python_value_numbers = 2
        group_model = self._group_model
        count_opt = len(options['comparison']['periods'])
        date_from = options['date']['date_from']
        date_to = options['date']['date_to']
        dateto_datetime = datetime.strptime(date_to, "%Y-%m-%d")
        ctx.update(date_from=date_from, date_to=date_to,
                   year=dateto_datetime.year)
        gorup_ids = self.env[group_model].search([], order='sequence asc')
        list_groups = {}
        acc_obj = self.env['account.account']
        for group in gorup_ids:
            if group.group_type == 'lines':
                group_lines = []
                group_columns = []
                for line in group.line_ids:
                    account_ids = line.account_ids
                    subtraction_account_ids = line.subtraction_account_ids
                    account2_ids = line.account2_ids
                    subtraction_account2_ids = line.subtraction_account2_ids
                    if line.account_source_method == 'code':
                        account_ids = subtraction_account_ids = acc_obj
                        account2_ids = subtraction_account2_ids = acc_obj
                        results = line.with_context(ctx).run_code()
                        counts = 0
                        for one_row in results:
                            counts += 1
                            if len(one_row) < min_python_value_numbers:
                                raise UserError(
                                    _('Error Python Value In Group/Line: %s/%s.'
                                      '') % (group.name, line.name)
                                )
                            name = one_row[0]
                            value1 = one_row[1]
                            columns = [{'name': self.format_value(value1),
                                        'class': 'number',
                                        'no_format_name': value1,
                                        'title': 'Python Code'}]
                            if min_python_value_numbers > 2:
                                value2 = one_row[2]
                                value3 = one_row[3]
                                columns.append({
                                    'name': self.format_value(value2),
                                    'class': 'number',
                                    'no_format_name': value2,
                                    'title': 'Python Code'
                                })
                                columns.append({
                                    'name': self.format_value(value3),
                                    'class': 'number',
                                    'no_format_name': value3,
                                    'title': 'Python Code',
                                })
                            for year in range(1, count_opt + 1):
                                columns.append({
                                    'name': self.format_value(
                                        0),
                                    'class': 'number',
                                    'no_format_name': 0,
                                    'title': 'Compare %s' % year
                                })
                            group_lines.append({
                                'id': "line_%d_code_%d" % (line.id, counts),
                                'name': name,
                                'title_hover': name,
                                'columns': self.action_sign_columns(
                                    columns, value_type=line.value_type,
                                    view_type=line.view_type),
                                'unfoldable': False,
                                'left_col': line.left_char,
                                'caret_options': '',
                            })
                        continue
                    elif line.account_source_method == 'domain':
                        if line.accounts_domain:
                            account_ids = acc_obj.search(
                                safe_eval(line.accounts_domain))
                        if line.accounts2_domain:
                            account2_ids = acc_obj.search(
                                safe_eval(line.accounts2_domain))
                        if line.subtraction_accounts_domain:
                            subtraction_account_ids = acc_obj.search(safe_eval(
                                line.subtraction_accounts_domain))
                        if line.subtraction_accounts2_domain:
                            subtraction_account2_ids = acc_obj.search(safe_eval(
                                line.subtraction_accounts2_domain))

                    balance = balance2 = 0
                    if account_ids:
                        balance = self._get_account_values(
                            options, account_ids.ids,
                            period_fiscal_year=line.period_fiscal_year)
                    if subtraction_account_ids:
                        balance -= self._get_account_values(
                            options, subtraction_account_ids.ids,
                            period_fiscal_year=line.period_fiscal_year)
                    if account2_ids:
                        balance2 = self._get_account_values(
                            options, account2_ids.ids,
                            period_fiscal_year=line.period_fiscal_year)
                    if subtraction_account2_ids:
                        balance2 -= self._get_account_values(
                            options, subtraction_account2_ids.ids,
                            period_fiscal_year=line.period_fiscal_year)
                    net = balance + balance2 # i modify here 
                    if number_of_columns == 1:
                        columns = [
                            {
                                'name': self.format_value(balance),
                                'class': 'number', 'no_format_name': balance,
                                'title': 'balance'
                            }
                        ]
                    else:
                        columns = [
                            {
                                'name': self.format_value(balance),
                                'class': 'number', 'no_format_name': balance,
                                'title': 'balance'
                            },
                            {
                                'name': self.format_value(balance2),
                                'class': 'number', 'no_format_name': balance2,
                                'title': 'dep balance'
                            },
                            {
                                'name': self.format_value(net),
                                'class': 'number', 'no_format_name': net,
                                'title': 'Net'
                            }
                        ]
                    for x in range(1, count_opt + 1):
                        x_dateto = dateto_datetime - relativedelta(years=x)
                        dateto_str = x_dateto.strftime('%Y-%m-%d')
                        x_balance = x_balance2 = 0
                        new_options = options.copy()
                        new_options['date'] = new_options['date'].copy()
                        new_options['date']['date_from'] = '1900-01-01'
                        new_options['date']['date_to'] = dateto_str
                        if account_ids:
                            x_balance = self._get_account_values(
                                new_options, account_ids.ids,
                                period_fiscal_year=line.period_fiscal_year)
                        if account2_ids:
                            x_balance2 = self._get_account_values(
                                new_options, account2_ids.ids,
                                period_fiscal_year=line.period_fiscal_year)
                        if subtraction_account_ids:
                            x_balance -= self._get_account_values(
                                new_options, subtraction_account_ids.ids,
                                period_fiscal_year=line.period_fiscal_year)
                        if subtraction_account2_ids:
                            x_balance2 -= self._get_account_values(
                                new_options, subtraction_account2_ids.ids,
                                period_fiscal_year=line.period_fiscal_year)
                        x_compare = x_balance + x_balance2 # i modify here +/-
                        columns.append({
                            'name': self.format_value(x_compare),
                            'class': 'number', 'no_format_name': x_compare,
                            'title': 'Compare %s' % x
                        })
                    group_lines.append({
                        'id': line.id,
                        'name': line.name,
                        'title_hover': line.name,
                        'columns': self.action_sign_columns(
                            columns, value_type=line.value_type,
                            view_type=line.view_type),
                        'unfoldable': False,
                        'left_col': line.left_char,
                        'caret_options': line._name,
                    })
                    if not line.disable_sum_group:
                        group_columns.append(columns)
                sum_group_columns = self.copy_list_columns(
                    group_columns, group.name)
                lines.append({
                    'id': group.id,
                    'name': group.name,
                    'title_hover': group.name,
                    'class': 'total',
                    'columns': self.action_sign_columns(
                        sum_group_columns, value_type=group.value_type,
                        view_type=group.view_type),
                    'unfoldable': False,
                    'left_col': group.left_char,
                    'caret_options': group._name,
                })
                if sum_group_columns:
                    list_groups[group.id] = sum_group_columns
                for g_line in group_lines:
                    lines.append(g_line)
            elif group.group_type == 'one_line':
                account_ids = group.account_ids
                subtraction_account_ids = group.subtraction_account_ids
                account2_ids = group.account2_ids
                subtraction_account2_ids = group.subtraction_account2_ids
                if group.account_source_method == 'domain':
                    if group.accounts_domain:
                        account_ids = acc_obj.search(
                            safe_eval(group.accounts_domain))
                    if group.accounts2_domain:
                        account2_ids = acc_obj.search(
                            safe_eval(group.accounts2_domain))
                    if group.subtraction_accounts_domain:
                        subtraction_account_ids = acc_obj.search(
                            safe_eval(group.subtraction_accounts_domain))
                    if group.subtraction_accounts2_domain:
                        subtraction_account2_ids = acc_obj.search(
                            safe_eval(group.subtraction_accounts2_domain))
                balance = balance2 = 0
                if account_ids:
                    balance = self._get_account_values(
                        options, account_ids.ids,period_fiscal_year=group.period_fiscal_year)
                if account2_ids:
                    balance2 = self._get_account_values(
                        options, account2_ids.ids,period_fiscal_year=group.period_fiscal_year)
                if subtraction_account_ids:
                    balance -= self._get_account_values(
                        options, subtraction_account_ids.ids,period_fiscal_year=group.period_fiscal_year)
                if subtraction_account2_ids:
                    balance2 -= self._get_account_values(
                        options, subtraction_account2_ids.ids,period_fiscal_year=group.period_fiscal_year)
                net = balance + balance2 # i modify here 
                if number_of_columns == 1:
                    columns = [
                        {
                            'name': self.format_value(balance),
                            'class': 'number', 'no_format_name': balance,
                            'title': 'balance'
                        }
                    ]
                else:
                    columns = [
                        {
                            'name': self.format_value(balance),
                            'class': 'number', 'no_format_name': balance,
                            'title': 'balance'
                        },
                        {
                            'name': self.format_value(balance2),
                            'class': 'number', 'no_format_name': balance2,
                            'title': 'dep balance'
                        },
                        {
                            'name': self.format_value(net),
                            'class': 'number', 'no_format_name': net,
                            'title': 'Net'
                        }
                    ]

                for x in range(1, count_opt + 1):
                    x_dateto = dateto_datetime - relativedelta(years=x)
                    dateto_str = x_dateto.strftime('%Y-%m-%d')
                    x_balance = x_balance2 = 0
                    new_options = options.copy()
                    new_options['date'] = new_options['date'].copy()
                    new_options['date']['date_from'] = '1900-01-01'
                    new_options['date']['date_to'] = dateto_str
                    if account_ids:
                        x_balance = self._get_account_values(
                            new_options, account_ids.ids,period_fiscal_year=group.period_fiscal_year)
                    if account2_ids:
                        x_balance2 = self._get_account_values(
                            new_options, account2_ids.ids,period_fiscal_year=group.period_fiscal_year)
                    if subtraction_account_ids:
                        x_balance -= self._get_account_values(
                            new_options, subtraction_account_ids.ids,period_fiscal_year=group.period_fiscal_year)
                    if subtraction_account2_ids:
                        x_balance2 -= self._get_account_values(
                            new_options, subtraction_account2_ids.ids,period_fiscal_year=group.period_fiscal_year)
                    x_compare = x_balance + x_balance2
                    columns.append({
                        'name': self.format_value(x_compare),
                        'class': 'number', 'no_format_name': x_compare,
                        'title': 'Compare %s' % x
                    })
                if columns:
                    list_groups[group.id] = columns
                lines.append({
                    'id': group.id,
                    'name': group.name,
                    'title_hover': group.name,
                    'class': 'total',
                    'columns': self.action_sign_columns(
                        columns, value_type=group.value_type,
                        view_type=group.view_type),
                    'unfoldable': False,
                    'left_col': group.left_char,
                    'caret_options': group._name,
                })
            elif group.group_type == 'sum':
                group_columns = []
                sum_g_columns = []
                sum_g_ids = sub_g_ids = self.env[group_model]
                if group.summation_domain:
                    sum_g_ids = self.env[group_model].search(
                        safe_eval(group.summation_domain)).ids
                if group.subtraction_domain:
                    sub_g_ids = self.env[group_model].search(
                        safe_eval(group.subtraction_domain)).ids
                for sum_g_id in sum_g_ids:
                    if sum_g_id in list_groups:
                        if list_groups[sum_g_id]:
                            group_columns.append(list_groups[sum_g_id])
                for sub_g_id in sub_g_ids:
                    if sub_g_id in list_groups:
                        if list_groups[sub_g_id]:
                            group_columns.append(
                                self.action_sign_columns(list_groups[sub_g_id],
                                                         value_type='reversed',
                                                         view_type='reversed'),
                            )
                if group_columns:
                    sum_g_columns = self.copy_list_columns(
                        group_columns, group.name, sub=1)
                if sum_g_columns:
                    list_groups[group.id] = sum_g_columns
                lines.append({
                    'id': group.id,
                    'name': group.name,
                    'title_hover': group.name,
                    'class': 'total',
                    'columns': self.action_sign_columns(
                        sum_g_columns, value_type=group.value_type,
                        view_type=group.view_type),
                    'unfoldable': False,
                    'left_col': group.left_char,
                    'caret_options': group._name,
                })
        return lines
    
    @api.model
    def _get_lines(self, options, line_id=None):
        """
        Override function _get_lines
        """
        # Create new options with 'unfold_all' to compute the initial balances.
        # Then, the '_do_query' will compute
        # all sums/unaffected earnings/initial balances for all comparisons.
        lines = []
        ctx = self.env.context.copy()
        number_of_columns = self._number_of_columns or 2
        min_python_value_numbers = 4
        if number_of_columns == 1:
            min_python_value_numbers = 2
        group_model = self._group_model
        count_opt = len(options['comparison']['periods'])
        date_from = options['date']['date_from']
        date_to = options['date']['date_to']
        dateto_datetime = datetime.strptime(date_to, "%Y-%m-%d")
        ctx.update(date_from=date_from, date_to=date_to,
                   year=dateto_datetime.year)
        gorup_ids = self.env[group_model].search([], order='sequence asc')
        list_groups = {}
        acc_obj = self.env['account.account']
        for group in gorup_ids:
            if group.group_type == 'lines':
                group_lines = []
                group_columns = []
                for line in group.line_ids:
                    account_ids = line.account_ids
                    subtraction_account_ids = line.subtraction_account_ids
                    account2_ids = line.account2_ids
                    subtraction_account2_ids = line.subtraction_account2_ids
                    if line.account_source_method == 'code':
                        account_ids = subtraction_account_ids = acc_obj
                        account2_ids = subtraction_account2_ids = acc_obj
                        results = line.with_context(ctx).run_code()
                        counts = 0
                        for one_row in results:
                            counts += 1
                            if len(one_row) < min_python_value_numbers:
                                raise UserError(
                                    _('Error Python Value In Group/Line: %s/%s.'
                                      '') % (group.name, line.name)
                                )
                            name = one_row[0]
                            value1 = one_row[1]
                            columns = [{'name': self.format_value(value1),
                                        'class': 'number',
                                        'no_format_name': value1,
                                        'title': 'Python Code'}]
                            if min_python_value_numbers > 2:
                                value2 = one_row[2]
                                value3 = one_row[3]
                                columns.append({
                                    'name': self.format_value(value2),
                                    'class': 'number',
                                    'no_format_name': value2,
                                    'title': 'Python Code'
                                })
                                columns.append({
                                    'name': self.format_value(value3),
                                    'class': 'number',
                                    'no_format_name': value3,
                                    'title': 'Python Code',
                                })
                            for year in range(1, count_opt + 1):
                                columns.append({
                                    'name': self.format_value(
                                        0),
                                    'class': 'number',
                                    'no_format_name': 0,
                                    'title': 'Compare %s' % year
                                })
                            group_lines.append({
                                'id': "line_%d_code_%d" % (line.id, counts),
                                'name': name,
                                'title_hover': name,
                                'columns': self.action_sign_columns(
                                    columns, value_type=line.value_type,
                                    view_type=line.view_type),
                                'unfoldable': False,
                                'left_col': line.left_char,
                                'caret_options': '',
                            })
                        continue
                    elif line.account_source_method == 'domain':
                        if line.accounts_domain:
                            account_ids = acc_obj.search(
                                safe_eval(line.accounts_domain))
                        if line.accounts2_domain:
                            account2_ids = acc_obj.search(
                                safe_eval(line.accounts2_domain))
                        if line.subtraction_accounts_domain:
                            subtraction_account_ids = acc_obj.search(safe_eval(
                                line.subtraction_accounts_domain))
                        if line.subtraction_accounts2_domain:
                            subtraction_account2_ids = acc_obj.search(safe_eval(
                                line.subtraction_accounts2_domain))

                    balance = balance2 = 0
                    if account_ids:
                        balance = self._get_account_values(
                            options, account_ids.ids,
                            period_fiscal_year=line.period_fiscal_year)
                    if subtraction_account_ids:
                        balance -= self._get_account_values(
                            options, subtraction_account_ids.ids,
                            period_fiscal_year=line.period_fiscal_year)
                    if account2_ids:
                        balance2 = self._get_account_values(
                            options, account2_ids.ids,
                            period_fiscal_year=line.period_fiscal_year)
                    if subtraction_account2_ids:
                        balance2 -= self._get_account_values(
                            options, subtraction_account2_ids.ids,
                            period_fiscal_year=line.period_fiscal_year)
                    net = balance + balance2 # i modify here
                    if line.name == 'Bénéfice +':
                        if balance >  0:
                            balance = balance 
                        else:
                            balance = 0
                    if line.name == 'Perte -':
                        if balance <  0 :
                            balance = balance
                        else:
                            balance = 0
                    if number_of_columns == 1:
                        columns = [
                            {
                                'name': self.format_value(balance),
                                'class': 'number', 'no_format_name': balance,
                                'title': 'balance'
                            }
                        ]
                    else:
                        columns = [
                            {
                                'name': self.format_value(balance),
                                'class': 'number', 'no_format_name': balance,
                                'title': 'balance'
                            },
                            {
                                'name': self.format_value(balance2),
                                'class': 'number', 'no_format_name': balance2,
                                'title': 'dep balance'
                            },
                            {
                                'name': self.format_value(net),
                                'class': 'number', 'no_format_name': net,
                                'title': 'Net'
                            }
                        ]
                    for x in range(1, count_opt + 1):
                        x_dateto = dateto_datetime - relativedelta(years=x)
                        dateto_str = x_dateto.strftime('%Y-%m-%d')
                        x_balance = x_balance2 = 0
                        new_options = options.copy()
                        new_options['date'] = new_options['date'].copy()
                        new_options['date']['date_from'] = '1900-01-01'
                        new_options['date']['date_to'] = dateto_str
                        
                        if account_ids:
                            x_balance = self._get_account_values(
                                new_options, account_ids.ids,
                                period_fiscal_year=line.period_fiscal_year)
                        if account2_ids:
                            x_balance2 = self._get_account_values(
                                new_options, account2_ids.ids,
                                period_fiscal_year=line.period_fiscal_year)
                        if subtraction_account_ids:
                            x_balance -= self._get_account_values(
                                new_options, subtraction_account_ids.ids,
                                period_fiscal_year=line.period_fiscal_year)
                        if subtraction_account2_ids:
                            x_balance2 -= self._get_account_values(
                                new_options, subtraction_account2_ids.ids,
                                period_fiscal_year=line.period_fiscal_year)
                        if line.name == 'Bénéfice +':
                            if x_balance >  0:
                                x_balance = x_balance 
                            else:
                                x_balance = 0
                        if line.name == 'Perte -':
                            if x_balance <  0 :
                                x_balance = x_balance
                            else:
                                x_balance = 0
                        x_compare = x_balance + x_balance2 # i modify here +/-
                        columns.append({
                            'name': self.format_value(x_compare),
                            'class': 'number', 'no_format_name': x_compare,
                            'title': 'Compare %s' % x
                        })
                    group_lines.append({
                        'id': line.id,
                        'name': line.name,
                        'title_hover': line.name,
                        'columns': self.action_sign_columns(
                            columns, value_type=line.value_type,
                            view_type=line.view_type),
                        'unfoldable': False,
                        'left_col': line.left_char,
                        'caret_options': line._name,
                    })
                    if not line.disable_sum_group:
                        group_columns.append(columns)
                sum_group_columns = self.copy_list_columns(
                    group_columns, group.name)
                lines.append({
                    'id': group.id,
                    'name': group.name,
                    'title_hover': group.name,
                    'class': 'total',
                    'columns': self.action_sign_columns(
                        sum_group_columns, value_type=group.value_type,
                        view_type=group.view_type),
                    'unfoldable': False,
                    'left_col': group.left_char,
                    'caret_options': group._name,
                })
                if sum_group_columns:
                    list_groups[group.id] = sum_group_columns
                for g_line in group_lines:
                    lines.append(g_line)
            elif group.group_type == 'one_line':
                account_ids = group.account_ids
                subtraction_account_ids = group.subtraction_account_ids
                account2_ids = group.account2_ids
                subtraction_account2_ids = group.subtraction_account2_ids
                if group.account_source_method == 'domain':
                    if group.accounts_domain:
                        account_ids = acc_obj.search(
                            safe_eval(group.accounts_domain))
                    if group.accounts2_domain:
                        account2_ids = acc_obj.search(
                            safe_eval(group.accounts2_domain))
                    if group.subtraction_accounts_domain:
                        subtraction_account_ids = acc_obj.search(
                            safe_eval(group.subtraction_accounts_domain))
                    if group.subtraction_accounts2_domain:
                        subtraction_account2_ids = acc_obj.search(
                            safe_eval(group.subtraction_accounts2_domain))
                balance = balance2 = 0
                if account_ids:
                    balance = self._get_account_values(
                        options, account_ids.ids,period_fiscal_year=group.period_fiscal_year)
                if account2_ids:
                    balance2 = self._get_account_values(
                        options, account2_ids.ids,period_fiscal_year=group.period_fiscal_year)
                if subtraction_account_ids:
                    balance -= self._get_account_values(
                        options, subtraction_account_ids.ids,period_fiscal_year=group.period_fiscal_year)
                if subtraction_account2_ids:
                    balance2 -= self._get_account_values(
                        options, subtraction_account2_ids.ids,period_fiscal_year=group.period_fiscal_year)
                net = balance + balance2 # i modify here 
                if number_of_columns == 1:
                    columns = [
                        {
                            'name': self.format_value(balance),
                            'class': 'number', 'no_format_name': balance,
                            'title': 'balance'
                        }
                    ]
                else:
                    columns = [
                        {
                            'name': self.format_value(balance),
                            'class': 'number', 'no_format_name': balance,
                            'title': 'balance'
                        },
                        {
                            'name': self.format_value(balance2),
                            'class': 'number', 'no_format_name': balance2,
                            'title': 'dep balance'
                        },
                        {
                            'name': self.format_value(net),
                            'class': 'number', 'no_format_name': net,
                            'title': 'Net'
                        }
                    ]

                for x in range(1, count_opt + 1):
                    x_dateto = dateto_datetime - relativedelta(years=x)
                    dateto_str = x_dateto.strftime('%Y-%m-%d')
                    x_balance = x_balance2 = 0
                    new_options = options.copy()
                    new_options['date'] = new_options['date'].copy()
                    new_options['date']['date_from'] = '1900-01-01'
                    new_options['date']['date_to'] = dateto_str
                    if account_ids:
                        x_balance = self._get_account_values(
                            new_options, account_ids.ids,period_fiscal_year=group.period_fiscal_year)
                    if account2_ids:
                        x_balance2 = self._get_account_values(
                            new_options, account2_ids.ids,period_fiscal_year=group.period_fiscal_year)
                    if subtraction_account_ids:
                        x_balance -= self._get_account_values(
                            new_options, subtraction_account_ids.ids,period_fiscal_year=group.period_fiscal_year)
                    if subtraction_account2_ids:
                        x_balance2 -= self._get_account_values(
                            new_options, subtraction_account2_ids.ids,period_fiscal_year=group.period_fiscal_year)
                    x_compare = x_balance + x_balance2
                    columns.append({
                        'name': self.format_value(x_compare),
                        'class': 'number', 'no_format_name': x_compare,
                        'title': 'Compare %s' % x
                    })
                if columns:
                    list_groups[group.id] = columns
                lines.append({
                    'id': group.id,
                    'name': group.name,
                    'title_hover': group.name,
                    'class': 'total',
                    'columns': self.action_sign_columns(
                        columns, value_type=group.value_type,
                        view_type=group.view_type),
                    'unfoldable': False,
                    'left_col': group.left_char,
                    'caret_options': group._name,
                })
            elif group.group_type == 'sum':
                group_columns = []
                sum_g_columns = []
                sum_g_ids = sub_g_ids = self.env[group_model]
                if group.summation_domain:
                    sum_g_ids = self.env[group_model].search(
                        safe_eval(group.summation_domain)).ids
                if group.subtraction_domain:
                    sub_g_ids = self.env[group_model].search(
                        safe_eval(group.subtraction_domain)).ids
                for sum_g_id in sum_g_ids:
                    if sum_g_id in list_groups:
                        if list_groups[sum_g_id]:
                            group_columns.append(list_groups[sum_g_id])
                for sub_g_id in sub_g_ids:
                    if sub_g_id in list_groups:
                        if list_groups[sub_g_id]:
                            group_columns.append(
                                self.action_sign_columns(list_groups[sub_g_id],
                                                         value_type='reversed',
                                                         view_type='reversed'),
                            )
                if group_columns:
                    sum_g_columns = self.copy_list_columns(
                        group_columns, group.name, sub=1)
                if sum_g_columns:
                    list_groups[group.id] = sum_g_columns
                lines.append({
                    'id': group.id,
                    'name': group.name,
                    'title_hover': group.name,
                    'class': 'total',
                    'columns': self.action_sign_columns(
                        sum_g_columns, value_type=group.value_type,
                        view_type=group.view_type),
                    'unfoldable': False,
                    'left_col': group.left_char,
                    'caret_options': group._name,
                })
        return lines
    
    @api.model
    def _get_data(self, ct_query, where_clause, where_params):
        """
        Get Data
        :param ct_query:
        :param where_clause:
        :param where_params:
        :return:
        """
        debit = credit = balance = 0
        query = '''
SELECT
account_move_line.id,
account_move_line.date,
account_move_line.date_maturity,
account_move_line.name,
account_move_line.ref,
account_move_line.company_id,
account_move_line.account_id,
account_move_line.payment_id,
account_move_line.currency_id,
account_move_line.amount_currency,
ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)
AS debit,
ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)
AS credit,
ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)
AS balance,
account_move_line__move_id.name         AS move_name,
company.currency_id                     AS company_currency_id,
partner.name                            AS partner_name,

account.code                            AS account_code,
account.name                            AS account_name,
journal.code                            AS journal_code,
journal.name                            AS journal_name,
full_rec.name                           AS full_rec_name
FROM account_move_line
LEFT JOIN account_move account_move_line__move_id
ON account_move_line__move_id.id = account_move_line.move_id
LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
LEFT JOIN res_company company ON company.id = account_move_line.company_id
LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
LEFT JOIN account_account account ON account.id = account_move_line.account_id
LEFT JOIN account_journal journal ON journal.id = account_move_line.journal_id
LEFT JOIN account_full_reconcile full_rec
ON full_rec.id = account_move_line.full_reconcile_id
WHERE %s
ORDER BY account_move_line.date, account_move_line.id

                        ''' % (ct_query, where_clause) # i removed line 545 : account_move_line__move_id.type         AS move_type,
        # ORDER BY account_move_line.date, account_move_line.id
        # pylint: disable=sql-injection
        self._cr.execute(query, where_params)
        
        for data in self._cr.dictfetchall():
            credit += data['credit']
            debit += data['debit']
            account = self.env['account.account'].search([('id','=',data['account_id'])])
            if str(account.code[0] + account.code[1]) == '51':
                balance += data['debit'] - data['credit']
            elif account.code[0] == '2' and  str(account.code[0] + account.code[1]) != '28' and  str(account.code[0] + account.code[1]) != '29':
                balance += data['debit'] - data['credit']
            elif account.code[0] == '3' and  str(account.code[0] + account.code[1]) != '39':
                balance += data['debit'] - data['credit']
            elif account.code[0] == '1'  or str(account.code[0] + account.code[1]) == '55'  or str(account.code[0] + account.code[1]) == '28' or str(account.code[0] + account.code[1]) == '29' or str(account.code[0] + account.code[1]) == '39' or str(account.code[0] + account.code[1]) == '59' :
                balance += data['credit'] - data['debit']
            elif str(account.code[0] + account.code[1]+ account.code[2]+account.code[3]) == '6119' or str(account.code[0] + account.code[1]+ account.code[2]+account.code[3]) == '6129' :
                balance += data['credit'] - data['debit']
            elif account.code[0] == '7' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '7119' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '7129':
                balance += data['credit'] - data['debit']
            elif str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) == '7119' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) == '7129':
                balance +=data['debit'] - data['credit'] 
            elif account.code[0] == '6' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '6119' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '6129':
                balance += data['debit'] - data['credit']
            elif  account.code[0] == '4' and str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '4465' :
                balance += data['credit'] - data['debit']
            elif  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) == '4465' :
                balance +=  data['credit']
            
        return debit, credit, balance
