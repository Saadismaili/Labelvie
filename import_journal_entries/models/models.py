# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re, html_escape, is_html_empty
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from contextlib import contextmanager
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings


class AccountMoveInheritance(models.Model):
    _inherit = 'account.move'

    is_imported  = fields.Boolean(string='importé',default=False)
    def _check_balanced(self):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        for rec in self:
            if not rec.is_imported:
                moves = self.filtered(lambda move: move.line_ids)
                if not moves:
                    return
                # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
                # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
                # It happens as the ORM makes the create with the 'no_recompute' statement.
                self.env['account.move.line'].flush(self.env['account.move.line']._fields)
                self.env['account.move'].flush(['journal_id'])
                self._cr.execute('''
                    SELECT line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places)
                    FROM account_move_line line
                    JOIN account_move move ON move.id = line.move_id
                    JOIN account_journal journal ON journal.id = move.journal_id
                    JOIN res_company company ON company.id = journal.company_id
                    JOIN res_currency currency ON currency.id = company.currency_id
                    WHERE line.move_id IN %s
                    GROUP BY line.move_id, currency.decimal_places
                    HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
                ''', [tuple(self.ids)])

                query_res = self._cr.fetchall()
                if query_res:
                    ids = [res[0] for res in query_res]
                    sums = [res[1] for res in query_res]
                    raise UserError(_("Cannot create unbalanced journal entry. Ids: %s\nDifferences debit - credit: %s") % (ids, sums))
            else:
                return True