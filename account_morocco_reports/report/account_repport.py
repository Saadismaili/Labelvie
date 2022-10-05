import copy
import json
import io
import logging
import lxml.html
import datetime
import ast
from collections import defaultdict
from math import copysign

from dateutil.relativedelta import relativedelta

from odoo.tools.misc import xlsxwriter
from odoo import models, fields, api, _
from odoo.tools import config, date_utils, get_lang
from odoo.osv import expression
from babel.dates import get_quarter_names
from odoo.tools.misc import formatLang, format_date
from odoo.addons.web.controllers.main import clean_action
from odoo.tools.safe_eval import safe_eval


# pylint: disable=no-member, unused-argument, consider-using-ternary
# pylint: disable=no-self-use, unused-variable, redefined-outer-name
# pylint: disable=too-many-arguments, too-many-locals, protected-access
# pylint: disable=too-many-nested-blocks
class AccountReport(models.AbstractModel):
    """ inherit py report account.report """
    _inherit = "account.report"

    @api.model
    def _get_query_currency_table(self, options):
        ''' Construct the currency table as a mapping company -> rate to convert the amount to the user's company
        currency in a multi-company/multi-currency environment.
        The currency_table is a small postgresql table construct with VALUES.
        :param options: The report options.
        :return:        The query representing the currency table.
        '''

        user_company = self.env.company
        user_currency = user_company.currency_id
        if options.get('multi_company'):
            company_ids = [c['id'] for c in self._get_options_companies(options) if c['id'] != user_company.id and c['selected']]
            company_ids.append(self.env.company.id)
            companies = self.env['res.company'].browse(company_ids)
            conversion_date = options['date']['date_to']
            currency_rates = companies.mapped('currency_id')._get_rates(user_company, conversion_date)
        else:
            companies = user_company
            currency_rates = {user_currency.id: 1.0}

        conversion_rates = []
        for company in companies:
            conversion_rates.append((
                company.id,
                currency_rates[user_company.currency_id.id] / currency_rates[company.currency_id.id],
                user_currency.decimal_places,
            ))

        currency_table = ','.join('(%s, %s, %s)' % args for args in conversion_rates)
        return '(VALUES %s) AS currency_table(company_id, rate, precision)' % currency_table

    @api.model
    def _get_options_companies(self, options):
        if not options.get('multi_company'):
            company = self.env.company
            return [{'id': company.id, 'name': company.name, 'selected': True}]

        all_companies = []
        companies = []
        for company_option in options['multi_company']:
            if company_option['selected']:
                companies.append(company_option)
            all_companies.append(company_option)
        return companies or all_companies