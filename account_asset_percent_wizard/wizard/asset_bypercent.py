# -*- encoding: utf-8 -*-
import calendar

from odoo import api, fields, models
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import ValidationError
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta


class AssetsByPercent(models.TransientModel):
    _name = 'asset.bypercent'

    percent = fields.Float('Percent')

    def _compute_board_undone_dotation_nb(self, asset, depreciation_date, total_days):
        undone_dotation_number = self.percent and 100/self.percent or 1
        if asset.method_time == 'end':
            end_date = datetime.strptime(asset.method_end, DF).date()
            undone_dotation_number = 0
            while depreciation_date <= end_date:
                depreciation_date = date(depreciation_date.year, depreciation_date.month,
                                         depreciation_date.day) + relativedelta(months=+asset.method_period)
                undone_dotation_number += 1
        if asset.prorata:
            undone_dotation_number += 1
        return undone_dotation_number

    def _compute_board_amount(self, asset, sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date):
        amount = 0
        number = self.percent and 100/self.percent or 1
        if sequence == undone_dotation_number:
            amount = residual_amount

        else:
            if asset.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if asset.prorata:
                    amount = amount_to_depr / number
                    if sequence == 1:
                        months = 13 - datetime.strptime(asset._get_last_depreciation_date()[asset.id],
                                                      DF).date().month
                        amount = (amount_to_depr / number) / 12 * months

            elif self.method == 'degressive':
                amount = residual_amount * self.method_progress_factor
                if self.prorata:
                    if sequence == 1:
                        months = 13 - depreciation_date.month
                        amount = (residual_amount * self.method_progress_factor) / 12 * months
        return amount



    # @api.multi
    def compute_depreciation_bypercent(self):
        active_id = self.env['account.asset.asset'].browse(self.env.context.get('active_id'))
        active_id.percent = self.percent

        method_number = self.percent and int(100/self.percent or 1)+1
        if active_id.prorata:
            method_number +=1
        active_id.method_number = method_number
        posted_depreciation_line_ids = active_id.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(
            key=lambda l: l.depreciation_date)
        if posted_depreciation_line_ids:
            raise ValidationError(u'Merci de supprimer les lignes de dépreciation comptabilisées')
        unposted_depreciation_line_ids = active_id.depreciation_line_ids.filtered(lambda x: not x.move_check)

        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

        if active_id.value_residual != 0.0 and not active_id.vna_move_id:
            amount_to_depr = residual_amount = active_id.value_residual

            date_dep = datetime.strptime(active_id._get_last_depreciation_date()[active_id.id], DF).date()
            if active_id.prorata:
                depreciation_date = datetime.strptime(active_id._get_last_depreciation_date()[active_id.id][:4] + '-12-31',
                                                      DF).date()
            else:
                # depreciation_date = 1st of January of purchase year
                asset_date = datetime.strptime(active_id.date[:4] + '-12-31', DF).date()
                # if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                    last_depreciation_date = datetime.strptime(posted_depreciation_line_ids[-1].depreciation_date,
                                                               DF).date()
                    depreciation_date = last_depreciation_date + relativedelta(months=+active_id.method_period)
                else:
                    depreciation_date = asset_date

            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb(active_id, depreciation_date, total_days)
            for x in range(len(posted_depreciation_line_ids), int(undone_dotation_number)):
                sequence = x + 1
                amount = self._compute_board_amount(active_id, sequence, residual_amount, amount_to_depr, undone_dotation_number,
                                                    posted_depreciation_line_ids, total_days, depreciation_date)
                amount = active_id.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=active_id.currency_id.rounding):
                    continue
                residual_amount -= amount
                vals = {
                    'amount': amount,
                    'asset_id': active_id.id,
                    'sequence': sequence,
                    'name': (active_id.code or '') + '/' + str(sequence),
                    'remaining_value': residual_amount,
                    'depreciated_value': active_id.value - (active_id.salvage_value + residual_amount),
                    'depreciation_date': depreciation_date.strftime(DF),
                }
                commands.append((0, False, vals))
                # Considering Depr. Period as months
                depreciation_date = date(year, month, day) + relativedelta(months=+active_id.method_period)
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year

        active_id.write({'depreciation_line_ids': commands})
        if round(active_id.depreciation_line_ids[-1].remaining_value,2) != 0:
            values = {
                    'amount': active_id.depreciation_line_ids[-1].remaining_value,
                    'asset_id': active_id.id,
                    'sequence': sequence+1,
                    'name': (active_id.code or '') + '/' + str(sequence+1),
                    'remaining_value': 0,
                    'depreciated_value': active_id.value,
                    'depreciation_date': (date(year, month, day) + relativedelta(months=+active_id.method_period)).strftime(DF),
                }
            active_id.write({'depreciation_line_ids': [(0,False, values)]})

        return True
