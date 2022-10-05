# -*- encoding: utf-8 -*-
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    by_percent = fields.Boolean('En pourcentage')
    percent = fields.Float('Pourcentage')

    # @api.multi
    def write(self, vals):
        res = super(AccountAssetAsset, self).write(vals)
        if 'depreciation_line_ids' not in vals and 'state' not in vals :
            for rec in self:
                if not rec.by_percent:
                    rec.compute_depreciation_board()
        return res

    @api.model
    def create(self, vals):
        asset = super(AccountAssetAsset, self.with_context(mail_create_nolog=True)).create(vals)
        if not asset.by_percent:
            asset.compute_depreciation_board()
        return asset

    # @api.multi
    def compute_depreciation_board(self):
        if not self.by_percent:
            return super(AccountAssetAsset, self).compute_depreciation_board()



