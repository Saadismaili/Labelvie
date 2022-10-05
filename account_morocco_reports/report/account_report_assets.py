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
class AccountReportAssets(models.AbstractModel):
    """ init py report account.report.assets """
    _name = "account.report.assets"
    _description = "account.report.assets"
    _inherit = "account.report"
    _group_model = 'assets.group'
    _number_of_columns = 2

    filter_date = {'mode': 'range', 'filter': 'this_year',
                   'date_from': '1900-1-1'}
    filter_comparison = {'date_from': '', 'date_to': '',
                         'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_journals = False
    filter_analytic = False
    filter_unfold_all = False
    filter_cash_basis = None
    filter_hierarchy = False
    MAX_LINES = None

    def _get_from_fiscal_year(self, date_to, res_date=False):
        """
        Get Date From Fiscal Year
        :param date_to:
        :return:
        """
        date_dt = datetime.now()
        if isinstance(date_to, str):
            date_dt = fields.Date.from_string(date_to)
        elif isinstance(date_to, datetime):
            date_dt = date_to
        fiscalyear_dates = self.env.company.compute_fiscalyear_dates(date_dt)
        date_from = fiscalyear_dates['date_from']
        date_to = fiscalyear_dates['date_to']
        if res_date:
            return date_from, date_to
        date_from_str = date_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
        date_to_str = date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)
        return date_from_str, date_to_str

    # pylint: disable=invalid-name, too-many-branches, too-many-statements
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
                    net = balance - balance2 # i modify here 
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
                        x_compare = x_balance - x_balance2 # i modify here +/-
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
                net = balance - balance2 # i modify here 
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
    def format_value(self, amount, currency=False, blank_if_zero=False):
        """
        Override to return the same amount
        :param amount:
        :param currency:
        :param blank_if_zero:
        :return: amount with format
        """
        return '{:20,.2f}'.format(amount)

    @api.model
    def _get_templates(self):
        """
        Override function _get_templates
        """
        templates = super(AccountReportAssets, self)._get_templates()
        templates['main_template'] = 'account_morocco_reports.' \
                                     'morocco_main_template'
        templates['main_table_header_template'] = 'account_morocco_reports.' \
                                                  'template_assets_table_header'
        templates['search_template'] = 'account_morocco_reports.' \
                                       'search_template_assets'
        templates['line_template'] = 'account_morocco_reports.' \
                                     'line_template_assets'
        return templates

    @api.model
    def _get_columns_name(self, options):
        """
        Override function _get_columns_name
        """
        columns = [
            {'name': '', 'style': 'width:2%'},
            {'name': '', 'style': 'width:80%'},
            {'name': _('Gross'), 'class': 'number'},
            {'name': _('Amortization and Provisions'), 'class': 'number'},
            {'name': _('Net'), 'class': 'number '},
        ]
        count_opt = len(options['comparison']['periods'])
        if options.get('comparison') and options['comparison'].get('periods'):
            columns += [{'name': _('Net'), 'class': 'number '}] * count_opt
        return columns

    @api.model
    def _get_super_columns(self, options):
        """
        Override _get_super_columns
        """
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = []
        columns += date_cols
        return {'columns': columns, 'x_offset': 3, 'merge': 1}

    @api.model
    def _get_options_date_domain(self, options):
        """
        Override _get_options_date_domain
        """

        def create_date_domain(options_date):
            """
            create_date_domain
            """
            date_field = options_date.get('date_field', 'date')
            domain = [(date_field, '<=', options_date['date_to'])]
            if options_date['mode'] == 'range':
                strict_range = options_date.get('strict_range')
                if not strict_range:
                    domain += [
                        '|',
                        (date_field, '>=', '1900-01-01'),
                        ('account_id.user_type_id.include_initial_balance', '=',
                         True)
                    ]
                else:
                    domain += [(date_field, '>=', options_date['date_from'])]
            return domain

        if not options.get('date'):
            return []
        return create_date_domain(options['date'])
    
    @api.model
    def _get_dates_period(self, options, date_from, date_to, mode,
                          period_type=None, strict_range=False):
        """
        Override _get_dates_period
        """
        res = super(AccountReportAssets, self)._get_dates_period(
            options, date_from, date_to, mode, period_type=period_type,
            strict_range=strict_range
        )
        date_range = self.env['date.range'].search([('is_config','=',True)])
        if date_range:
            res['date_from'] = str(date_range.date_start)
            dt_to_str = format_date(self.env, str(date_range.date_end))
            string = _('As %s') % dt_to_str
            return {
                'string': string,
                'period_type': 'year',
                'mode': res['mode'],
                'strict_range': strict_range, # This Line Has Been Added 
                'date_from': res['date_from'],
                'date_to': str(date_range.date_end),
            }
        else:
            dt_to_str = format_date(self.env, fields.Date.to_string(date_to))
            string = _('As %s') % dt_to_str
            return {
                'string': string,
                'period_type': 'year',
                'mode': res['mode'],
                'strict_range': strict_range, # This Line Has Been Added 
                'date_from': res['date_from'],
                'date_to': fields.Date.to_string(date_to),
            }

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
            elif account.code[0] == '1' or account.code[0] == '4' or str(account.code[0] + account.code[1]) == '55'  or str(account.code[0] + account.code[1]) == '28' or str(account.code[0] + account.code[1]) == '29' or str(account.code[0] + account.code[1]) == '39' or str(account.code[0] + account.code[1]) == '59' :
                balance += data['credit'] - data['debit']
            elif str(account.code[0] + account.code[1]+ account.code[2]+account.code[3]) == '6119' or str(account.code[0] + account.code[1]+ account.code[2]+account.code[3]) == '6129' :
                balance += data['credit'] - data['debit']
            elif account.code[0] == '7' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '7119' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '7129':
                balance += data['credit'] - data['debit']
            elif str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) == '7119' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) == '7129':
                balance +=data['debit'] - data['credit'] 
            elif account.code[0] == '6' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '6119' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '6129':
                balance += data['debit'] - data['credit']
            
        return debit, credit, balance
    
    def find_index(self,array):
        for element in array:
            if isinstance(element, str) and ('-' in element):
                return array.index(element)

    @api.model
    def _get_account_values(self, options, account_ids,
                            period_fiscal_year=None):
        """
        Compute the balance
        """
        # print('options' ,options)
        domain = [('account_id', 'in', account_ids)]
        tables, where_clause, where_params = self._query_get(
            options, domain=domain)
        date = options.get('date')
        if date:
            date_to = date.get('date_to')
            if period_fiscal_year:
                date_from, date_to = self._get_from_fiscal_year(date_to)
                domain += [('date', '>=', date_from), ('date', '<=', date_to)]
                import logging
                _logger = logging.getLogger(__name__)
                _logger.info("where_params general asset equal = %s" % where_params) 
                where_params[self.find_index(where_params)] = date_to
                where_params[self.find_index(where_params) + 1] = date_from
        ct_query = self.env['res.currency']._get_query_currency_table(options)
        debit, credit, balance = self._get_data(
            ct_query, where_clause, where_params)
        return balance

    def copy_list_columns(self, list_columns, col_name, sub=0):
        """ copy list columns"""
        extra_class = 'text-danger'
        if sub == 1:
            extra_class = 'text-success'

        def copy_columns(columns1, columns2):
            """ copy columns"""

            def mearge_column(col1, col2):
                """ mearge_column """
                if 'no_format_name' in col1 and 'no_format_name' in col2:
                    value = col1['no_format_name'] + col2['no_format_name']
                    return {'name': self.format_value(value),
                            'class': 'number %s' % extra_class,
                            'title': col_name,
                            'no_format_name': value}
                return col1

            res = []
            if columns1 and columns2:
                count = len(columns1)
                for index in range(0, count):
                    res.append(mearge_column(columns1[index], columns2[index]))
            return res

        res_columns = []
        for columns in list_columns:
            if not res_columns:
                res_columns = columns
            else:
                res_columns = copy_columns(res_columns, columns)
        return res_columns

    def action_sign_columns(self, list_columns, value_type='same',
                            view_type='same'):
        """
        Action sign of list columns
        :param list_columns:
        :param value_type:reversed/positive/positive
        :param view_type:reversed/positive/positive
        :return: subtraction_list_columns
        """
        res = []
        for col in list_columns:
            new_col_1 = col.copy()
            value_1 = new_col_1.get('no_format_name', 0)
            new_value_1 = value_1
            name_1 = new_col_1.get('name', '')
            new_name_1 = name_1

            if 'no_format_name' in new_col_1:
                
                if value_type == 'reversed':
                    new_value_1 = value_1 * -1
                elif value_type == 'positive':
                    new_value_1 = abs(value_1)
                elif value_type == 'negative':
                    new_value_1 = abs(value_1) * -1
                if view_type == 'reversed':
                    new_name_1 = value_1 * -1
                elif view_type == 'positive':
                    new_name_1 = abs(value_1)
                elif view_type == 'negative':
                    new_name_1 = abs(value_1) * -1
            if new_value_1 != value_1:
                new_col_1.update(no_format_name=new_value_1)
            if new_name_1 != name_1:
                new_col_1.update(name=self.format_value(new_name_1))
            res.append(new_col_1)
        return res

    def open_group(self, options, params=None):
        """
        open_group
        """
        if not params:
            params = {}
        name_obj = params.get('caret_options', False)
        if name_obj:
            table_name = name_obj.replace('.', '_')
            action_xml_id = \
                "account_morocco_reports.view_%s_action" % table_name
            action_red = self.env.ref(action_xml_id).read()
            if action_red:
                action = action_red[0]
                action.update(res_id=params.get('id', 0))
                return action
        return {}

    def _get_date_from(self, options, period_fiscal_year=None):
        """
        Get Date From
        :return:
        """
        if options and options.get('date'):
            if period_fiscal_year:
                date_to = options.get('date').get('date_to')
                return self._get_from_fiscal_year(date_to)[1]
        return '1900-01-01'

    def open_line_journal_items(self, options, params=None):
        """
        open_line_journal_items
        """
        if not params:
            params = {}

        name_obj = params.get('caret_options', False)
        if name_obj:
            line = self.env[name_obj].browse(params.get('id', 0))
            ctx = self.env.context.copy()
            ctx.update(search_default_posted=1)
            action = self.env.ref('account.action_move_line_select').read()[0]
            if 'domain' in action and not action['domain']:
                action['domain']='[]'
            domain = expression.normalize_domain(ast.literal_eval(action.get('domain', '[]')))
            account_ids, sub_account_ids = line.get_accounts()
            period_fiscal_year = line.period_fiscal_year
            all_acc_ids = account_ids | sub_account_ids
            if all_acc_ids:
                domain = expression.AND(
                    [domain, [('account_id', 'in', all_acc_ids.ids),
                              ('parent_state', '!=', 'cancel')]])
            if options:
                if options.get('date'):
                    opt_date = options['date']
                    if opt_date.get('date_from'):
                        date_from = self._get_date_from(
                            options, period_fiscal_year=period_fiscal_year)
                        domain = expression.AND(
                            [domain, [('date', '>=', date_from)]])
                    if opt_date.get('date_to'):
                        domain = expression.AND(
                            [domain, [('date', '<=', opt_date['date_to'])]])
                    if not opt_date.keys() & {'date_from', 'date_to'} \
                            and opt_date.get('date'):
                        domain = expression.AND(
                            [domain, [('date', '<=', opt_date['date'])]])
                if options.get('all_entries'):
                    ctx.update(search_default_unposted=1)
                action['domain'] = domain
            action['context'] = ctx
            return action
        return {}

    def _set_context(self, options):
        """
        _set_context
        """
        ctx = super(AccountReportAssets, self)._set_context(options)
        ctx['date_from'] = '1900-01-01'
        return ctx

    @api.model
    def _get_options(self, previous_options=None):
        """
        Override _get_options
        """
        res = super(AccountReportAssets, self)._get_options(
            previous_options=previous_options)
        dateto_datetime = datetime.strptime(res['date']['date_to'], "%Y-%m-%d")
        count_opt = res['comparison']['number_period']
        comparison_filter = res['comparison']['filter']
        if comparison_filter == 'previous_period':
            periods = []
            for x in range(1, count_opt + 1):
                x_dateto = dateto_datetime - relativedelta(years=x)
                dt_to_str = format_date(self.env, x_dateto)
                string = _('As %s') % dt_to_str
                periods.append({
                    'string': string,
                    'period_type': 'year',
                    'mode': 'range',
                    'date_from': res['date']['date_from'],
                    'date_to': fields.Date.to_string(x_dateto),
                })
            res['comparison']['periods'] = periods
        return res

    @api.model
    def _get_report_name(self):
        """
        Override  _get_report_name
        """
        return _("Morocco Report Assets")

    def get_xlsx(self, options, response=None):
        """
        Override Generate Excel file
        :param options:
        :param response:
        :return:
        """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self._get_report_name()[:31])

        date_default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666',
             'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666',
             'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666',
             'indent': 2})
        default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        left_style = workbook.add_format({'font_name': 'Arial',
                                          'font_size': 13, 'num_format': '@',
                                          'font_color': '#666666',
                                          'align': 'center'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True,
                                           'bottom': 2, 'align': 'center'})
        super_col_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'align': 'center'})
        level_0_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6,
             'font_color': '#666666'})
        level_1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1,
             'font_color': '#666666'})
        level_2_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12,
             'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12,
             'font_color': '#666666'})
        level_2_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12,
             'font_color': '#666666'})
        level_3_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666',
             'indent': 2})
        level_3_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12,
             'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        sheet.set_column(0, 0, 2)
        sheet.set_column(1, 1, 50)
        sheet.set_column(2, 5, 20)
        super_columns = self._get_super_columns(options)
        y_offset = bool(super_columns.get('columns')) and 1 or 0
        sheet.write(y_offset, 0, '', title_style)
        x = super_columns.get('x_offset', 0)
        for super_col in super_columns.get('columns', []):
            cell_content = super_col.get('string', '').replace(
                '<br/>', ' ').replace('&nbsp;', ' ')
            x_merge = super_columns.get('merge')
            if x_merge and x_merge > 1:
                sheet.merge_range(0, x, 0, x + (x_merge - 1), cell_content,
                                  super_col_style)
                x += x_merge
            else:
                sheet.write(0, x + 1, cell_content, super_col_style)
                x += 1
        for row in self.get_header(options):
            x = 0
            for column in row:
                colspan = column.get('colspan', 1)
                header_label = column.get('name', '').replace(
                    '<br/>', ' ').replace('&nbsp;', ' ')
                if colspan == 1:
                    sheet.write(y_offset, x, header_label, title_style)
                else:
                    sheet.merge_range(y_offset, x, y_offset, x + colspan - 1,
                                      header_label, title_style)
                x += colspan
            y_offset += 1
        ctx = self._set_context(options)
        ctx.update(
            {'no_format': True, 'print_mode': True, 'prefetch_fields': False})
        # deactivating the prefetching saves ~35% on get_lines running time
        lines = self.with_context(ctx)._get_lines(options)
        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)
        # write all data rows
        # pylint: disable=consider-using-enumerate
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style
            # write the first column, Left Char
            sheet.write(y + y_offset, 0, lines[y].get('left_col') or '',
                        left_style)
            # write the second column, with a specific style to manage the
            # indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(y + y_offset, 1, cell_value,
                                     date_default_col1_style)
            else:
                sheet.write(y + y_offset, 1, cell_value, col1_style)

            # write all the remaining cells
            for x in range(1, len(lines[y]['columns']) + 1):
                cell_type, cell_value = self._get_cell_type_value(
                    lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset,
                                         x + lines[y].get('colspan', 1),
                                         cell_value, date_default_style)
                else:
                    sheet.write(y + y_offset,
                                x + lines[y].get('colspan', 1), cell_value,
                                style)
        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()
        return generated_file
