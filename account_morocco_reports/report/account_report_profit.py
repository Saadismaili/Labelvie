""" init py report account.report.profit """
""" init py report account.report.assets """

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
class AccountReportProfit(models.AbstractModel):
    """ init py report account.report.profit """
    _name = "account.report.profit"
    _description = "account.report.profit"
    _inherit = "account.report.assets"
    _group_model = 'profit.group'

    filter_date = {'mode': 'range', 'filter': 'this_year',
                   'date_from': fields.Date.to_string(
                       datetime.now().replace(month=1, day=1))}

    def _get_date_from(self, options, period_fiscal_year=None):
        """
        Get Date From
        :return:
        """
        if options and options.get('date'):
            if period_fiscal_year:
                date_to = options.get('date').get('date_to')
                return self._get_from_fiscal_year(date_to)[1]
            return options and options.get('date').get('date_from')
        return '1900-01-01'

    @api.model
    def _get_templates(self):
        """
        Override function _get_templates
        """
        templates = super(AccountReportProfit, self)._get_templates()
        templates['main_template'] = 'account_morocco_reports.' \
                                     'morocco_main_template'
        templates['search_template'] = 'account_morocco_reports.' \
                                       'search_template_profit'
        return templates

    @api.model
    def _get_columns_name(self, options):
        """
        Override function _get_columns_name
        """
        columns = [{'name': '', 'style': 'width:2%'},
                   {'name': '', 'style': 'width:80%'},
                   {'name': _('Current Year'), 'class': 'number'},
                   {'name': _('Previous Year'), 'class': 'number'},
                   {'name': _('Net'), 'class': 'number '}, ]
        count_opt = len(options['comparison']['periods'])
        if options.get('comparison') and options['comparison'].get('periods'):
            columns += [{'name': _('Net'), 'class': 'number '}] * count_opt
        return columns

    @api.model
    def _get_dates_period(self, options, date_from, date_to, mode,
                          period_type=None, strict_range=False):
        """
        Override _get_dates_period
        """
        super(AccountReportProfit, self)._get_dates_period(
            options, date_from, date_to, mode, period_type=period_type,
            strict_range=strict_range
        )
        date_range = self.env['date.range'].search([('is_config','=',True)])
        if date_range:
            dt_from_str = format_date(self.env, str(date_range.date_start))
            dt_to_str = format_date(self.env, str(date_range.date_end))
            string = _('Form %s To %s') % (dt_from_str, dt_to_str)
            return {
                'string': string,
                'period_type': 'year',
                'mode': 'range',
                'strict_range': strict_range,# i add this line
                'date_from': str(date_range.date_start),
                'date_to': str(date_range.date_end),
            }
        else:
            dt_from_str = format_date(self.env, fields.Date.to_string(date_from))
            dt_to_str = format_date(self.env, fields.Date.to_string(date_to))
            string = _('Form %s To %s') % (dt_from_str, dt_to_str)
            return {
                'string': string,
                'period_type': 'year',
                'mode': 'range',
                'strict_range': strict_range,# i add this line
                'date_from': fields.Date.to_string(date_from),
                'date_to': fields.Date.to_string(date_to),
            }
    @api.model
    def _get_options(self, previous_options=None):
        """
        Override _get_options
        """
        res = super(AccountReportProfit, self)._get_options(
            previous_options=previous_options)
        dateto_datetime = datetime.strptime(res['date']['date_to'], "%Y-%m-%d")
        count_opt = res['comparison']['number_period']
        comparison_filter = res['comparison']['filter']
        if comparison_filter == 'previous_period':
            periods = []
            for index in range(1, count_opt + 1):
                x_dateto = dateto_datetime - relativedelta(years=index)
                x_datefrom = x_dateto.replace(day=1, month=1)
                dt_to_str = format_date(self.env, x_dateto)
                dt_from_str = format_date(self.env, x_datefrom)
                string = _('From %s To %s ') % (dt_from_str, dt_to_str)
                periods.append({
                    'string': string,
                    'period_type': 'year',
                    'mode': 'range',
                    'date_from': res['date']['date_from'],
                    'date_to': fields.Date.to_string(x_dateto),
                })
            res['comparison']['periods'] = periods
        return res

    def _set_context(self, options):
        """
        _set_context
        """
        ctx = super(AccountReportProfit, self)._set_context(options)
        ctx['date_from'] = options['date']['date_from']
        ctx['date_to'] = options['date']['date_to']
        return ctx

    @api.model
    def _get_report_name(self):
        """
        Override  _get_report_name
        """
        return _("Profit and Loss Part 1")

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