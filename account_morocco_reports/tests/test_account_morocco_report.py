"""Integrated Tests for TestAccountMoroccoReports"""

# pylint: disable=import-error
from odoo.addons.account_reports.tests.common import TestAccountReportsCommon

from odoo import fields
from odoo.tests import tagged
from odoo.tools import date_utils


# pylint: disable=too-many-ancestors, too-few-public-methods, invalid-name
# pylint: disable=protected-access
@tagged('post_install', '-at_install')
class TestAccountMoroccoReports(TestAccountReportsCommon):
    """Integrated Tests"""

    def setUp(self):
        """Setup the testing environment."""
        super(TestAccountMoroccoReports, self).setUp()
        accounts = self.env['account.account'].search([])
        python_code = "results = [('Name#1', 1, 2, 3), ('Name#2', 4, 5, 9)," \
                      " ('Name#3', 7, 8, 15)]"
        self.env['assets.group'].create([
            {
                'name': 'Test Asset Group#1',
                'sequence': 1,
                'group_type': 'one_line',
                'value_type': 'reversed',
                'view_type': 'negative',
                'account_ids': [(4, accounts[1].id)],
                'subtraction_account_ids': [(4, accounts[2].id)],
                'account2_ids': [(4, accounts[11].id)],
                'subtraction_account2_ids': [(4, accounts[12].id)],
                'accounts_domain': "[('id','<',15)]",
                'accounts2_domain': "[('id','<',20)]",
                'subtraction_accounts_domain': "[('id','>',15)]",
                'subtraction_accounts2_domain': "[('id','>',20)]",
            },
            {
                'name': 'Test Asset Group#2',
                'sequence': 2,
                'group_type': 'lines',
                'line_ids': [(0, 0, {
                    'sequence': 1,
                    'name': 'Line#1 To Asset Group#2',
                    'value_type': 'reversed',
                    'view_type': 'negative',
                    'account_source_method': 'accounts',
                    'account_ids': [(4, accounts[1].id)],
                    'subtraction_account_ids': [(4, accounts[2].id)],
                    'account2_ids': [(4, accounts[11].id)],
                    'subtraction_account2_ids': [(4, accounts[12].id)],
                }), (0, 0, {
                    'sequence': 1,
                    'name': 'Line#2 To Asset Group#2',
                    'value_type': 'reversed',
                    'view_type': 'negative',
                    'account_source_method': 'domain',
                    'accounts_domain': "[('id','<',15)]",
                    'accounts2_domain': "[('id','<',20)]",
                    'subtraction_accounts_domain': "[('id','>',15)]",
                    'subtraction_accounts2_domain': "[('id','>',20)]",
                }), (0, 0, {
                    'sequence': 2,
                    'name': 'Line#3 To Asset Group#2',
                    'value_type': 'positive',
                    'view_type': 'negative',
                    'account_source_method': 'code',
                    'code': python_code,
                })],
            },
            {
                'name': 'Test SUM Asset Group#3',
                'sequence': 3,
                'group_type': 'sum',
                'summation_domain': '[["name","ilike","Test Asset Group"]]',
                'subtraction_domain': '[["id",">",1]]',
            },
        ])

        self.env['equity.group'].create([
            {
                'name': 'Test Equity Group#1',
                'sequence': 1,
                'group_type': 'one_line',
                'value_type': 'reversed',
                'view_type': 'negative',
                'account_ids': [(4, accounts[0].id)],
                'accounts_domain': "[('id','<',10)]",
                'subtraction_accounts_domain': "[('id','>',15)]",
            },
            {
                'name': 'Test Equity Group#2',
                'sequence': 2,
                'group_type': 'lines',
                'line_ids': [(0, 0, {
                    'sequence': 1,
                    'name': 'Line#1 To Equity Group#2',
                    'value_type': 'reversed',
                    'view_type': 'negative',
                    'account_ids': [(4, accounts[1].id)],
                    'subtraction_account_ids': [(4, accounts[2].id)],
                    'accounts_domain': "[('id','<',10)]",
                    'subtraction_accounts_domain': "[('id','>',15)]"
                })],
            },
            {
                'name': 'Test SUM Equity Group#3',
                'sequence': 3,
                'group_type': 'sum',
                'summation_domain': '[["name","ilike","Test Equity Group"]]',
                'subtraction_domain': '[["id",">",1]]',
            },
        ])

        self.env['profit.group'].create([
            {
                'name': 'Test Profit Group#1',
                'sequence': 1,
                'group_type': 'one_line',
                'account_ids': [(4, accounts[1].id)],
                'subtraction_account_ids': [(4, accounts[2].id)],
                'account2_ids': [(4, accounts[11].id)],
                'subtraction_account2_ids': [(4, accounts[12].id)],
                'accounts_domain': "[('id','<',15)]",
                'accounts2_domain': "[('id','<',20)]",
                'subtraction_accounts_domain': "[('id','>',15)]",
                'subtraction_accounts2_domain': "[('id','>',20)]",
            },
            {
                'name': 'Test Profit Group#2',
                'sequence': 2,
                'group_type': 'lines',
                'line_ids': [(0, 0, {
                    'sequence': 1,
                    'name': 'Line#1 To Profit Group#2',
                    'value_type': 'reversed',
                    'view_type': 'negative',
                    'account_ids': [(4, accounts[1].id)],
                    'subtraction_account_ids': [(4, accounts[2].id)],
                    'account2_ids': [(4, accounts[11].id)],
                    'subtraction_account2_ids': [(4, accounts[12].id)],
                    'accounts_domain': "[('id','<',15)]",
                    'accounts2_domain': "[('id','<',20)]",
                    'subtraction_accounts_domain': "[('id','>',15)]",
                    'subtraction_accounts2_domain': "[('id','>',20)]",
                })],
            },
            {
                'name': 'Test SUM Profit Group#3',
                'sequence': 3,
                'group_type': 'sum',
                'summation_domain': '[["name","ilike","Test Profit Group"]]',
                'subtraction_domain': '[["id",">",1]]',
            },
        ])

        self.env['loss.group'].create([
            {
                'name': 'Test Loss Group#1',
                'sequence': 1,
                'group_type': 'one_line',
                'account_ids': [(4, accounts[1].id)],
                'subtraction_account_ids': [(4, accounts[2].id)],
                'account2_ids': [(4, accounts[11].id)],
                'subtraction_account2_ids': [(4, accounts[12].id)],
                'accounts_domain': "[('id','<',15)]",
                'accounts2_domain': "[('id','<',20)]",
                'subtraction_accounts_domain': "[('id','>',15)]",
                'subtraction_accounts2_domain': "[('id','>',20)]",
            },
            {
                'name': 'Test Loss Group#2',
                'sequence': 2,
                'group_type': 'lines',
                'line_ids': [(0, 0, {
                    'sequence': 1,
                    'name': 'Line#1 To Loss Group#2',
                    'value_type': 'reversed',
                    'view_type': 'negative',
                    'account_ids': [(4, accounts[1].id)],
                    'subtraction_account_ids': [(4, accounts[2].id)],
                    'account2_ids': [(4, accounts[11].id)],
                    'subtraction_account2_ids': [(4, accounts[12].id)],
                    'accounts_domain': "[('id','<',15)]",
                    'accounts2_domain': "[('id','<',20)]",
                    'subtraction_accounts_domain': "[('id','>',15)]",
                    'subtraction_accounts2_domain': "[('id','>',20)]",
                })],
            },
            {
                'name': 'Test SUM Loss Group#3',
                'sequence': 3,
                'group_type': 'sum',
                'summation_domain': '[["name","ilike","Test Loss Group"]]',
                'subtraction_domain': '[["id",">",1]]',
            },
        ])

    def test_00_get_accounts(self):
        """test Scenario: Test Get Accounts. """
        lines = self.env['assets.line'].search([])
        self.assertTrue(lines.get_accounts(), 'lines must be constant accounts')

    def test_00_report_copy_list(self):
        """test Scenario: Test copy list. """
        report = self.env['account.report.assets']
        list1 = [[{'no_format_name': 1}, {'no_format_name': 2}],
                 [{'no_format_name': 3}, {'no_format_name': 4}]]
        new_list = report.copy_list_columns(list1, 'new name', sub=1)
        self.assertTrue(new_list[0].get('no_format_name'),
                        'no_format_name not in new list')
        self.assertEqual(new_list[0].get('no_format_name'), 4,
                         'sum of lists must be equal 4.')
        self.assertTrue(new_list[1].get('no_format_name'),
                        'no_format_name not in new list')
        self.assertEqual(new_list[1].get('no_format_name'), 6,
                         'sum of lists must be equal 6.')

    def test_01_report_assets(self):
        """test Scenario: Test report assets. """
        today = fields.Date.today()
        report = self.env['account.report.assets']
        options = self._init_options(report, *date_utils.get_month(
            self.mar_year_minus_1))
        periods = [{
            'number': 1,
            'name': 'test periods',
            'date_from': fields.Date.to_string(today),
            'date_to': fields.Date.to_string(today),
        }]
        options.update(comparison={'periods': periods})
        templates = report._get_templates()
        columns_name = report._get_columns_name(options)
        super_columns = report._get_super_columns(options)
        options_date_domain = report._get_options_date_domain(options)
        dates_period = report._get_dates_period(options, today, today,
                                                options['date']['mode'])
        lines = report._get_lines(options)
        report.open_group(options)
        report.open_line_journal_items(options)
        self.assertTrue(lines, 'no lines in this report.')
        self.assertTrue(templates, 'no templates in this report.')
        self.assertTrue(columns_name, 'no columns_name in this report.')
        self.assertTrue(super_columns, 'no super_columns in this report.')
        self.assertTrue(options_date_domain,
                        'no options_date_domain in this report.')
        self.assertTrue(dates_period, 'no dates_period in this report.')
        options.update(comparison={'filter': 'previous_period'})
        options = report._get_options(options)
        self.assertTrue(options, 'no options in this report.')
        self.assertTrue(report._get_report_name(), 'no name in this report.')
        get_xlsx = report.get_xlsx(options)
        self.assertTrue(get_xlsx, 'no name in this report.')

    def test_02_report_equity(self):
        """test Scenario: Test report equity. """
        report = self.env['account.report.equity']
        today = fields.Date.today()
        options = self._init_options(report, *date_utils.get_month(
            self.mar_year_minus_1))
        periods = [{
            'number': 1,
            'name': 'test periods',
            'date_from': fields.Date.to_string(today),
            'date_to': fields.Date.to_string(today),
        }]
        options.update(comparison={'periods': periods})
        templates = report._get_templates()
        columns_name = report._get_columns_name(options)
        super_columns = report._get_super_columns(options)
        options_date_domain = report._get_options_date_domain(options)
        dates_period = report._get_dates_period(options, today, today,
                                                options['date']['mode'])
        lines = report._get_lines(options)
        self.assertTrue(lines, 'no lines in this report.')
        self.assertTrue(templates, 'no templates in this report.')
        self.assertTrue(columns_name, 'no columns_name in this report.')
        self.assertTrue(super_columns, 'no super_columns in this report.')
        self.assertTrue(options_date_domain,
                        'no options_date_domain in this report.')
        self.assertTrue(dates_period, 'no dates_period in this report.')
        self.assertTrue(report._get_report_name(), 'no name in this report.')

    def test_03_report_profit(self):
        """test Scenario: Test report profit. """
        report = self.env['account.report.profit']
        today = fields.Date.today()
        options = self._init_options(report, *date_utils.get_month(
            self.mar_year_minus_1))
        periods = [{
            'number': 1,
            'name': 'test periods',
            'date_from': fields.Date.to_string(today),
            'date_to': fields.Date.to_string(today),
        }]
        options.update(comparison={'periods': periods})
        templates = report._get_templates()
        columns_name = report._get_columns_name(options)
        super_columns = report._get_super_columns(options)
        options_date_domain = report._get_options_date_domain(options)
        dates_period = report._get_dates_period(options, today, today,
                                                options['date']['mode'])
        lines = report._get_lines(options)
        self.assertTrue(lines, 'no lines in this report.')
        self.assertTrue(templates, 'no templates in this report.')
        self.assertTrue(columns_name, 'no columns_name in this report.')
        self.assertTrue(super_columns, 'no super_columns in this report.')
        self.assertTrue(options_date_domain,
                        'no options_date_domain in this report.')
        self.assertTrue(dates_period, 'no dates_period in this report.')
        self.assertTrue(report._get_report_name(), 'no name in this report.')

    def test_04_report_loss(self):
        """test Scenario: Test report loss. """
        report = self.env['account.report.loss']
        today = fields.Date.today()
        options = self._init_options(report, *date_utils.get_month(
            self.mar_year_minus_1))
        periods = [{
            'number': 1,
            'name': 'test periods',
            'date_from': fields.Date.to_string(today),
            'date_to': fields.Date.to_string(today),
        }]
        options.update(comparison={'periods': periods})
        templates = report._get_templates()
        columns_name = report._get_columns_name(options)
        super_columns = report._get_super_columns(options)
        options_date_domain = report._get_options_date_domain(options)
        dates_period = report._get_dates_period(options, today, today,
                                                options['date']['mode'])
        lines = report._get_lines(options)
        self.assertTrue(lines, 'no lines in this report.')
        self.assertTrue(templates, 'no templates in this report.')
        self.assertTrue(columns_name, 'no columns_name in this report.')
        self.assertTrue(super_columns, 'no super_columns in this report.')
        self.assertTrue(options_date_domain,
                        'no options_date_domain in this report.')
        self.assertTrue(dates_period, 'no dates_period in this report.')
        self.assertTrue(report._get_report_name(), 'no name in this report.')
