# -*- encoding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class AccountAssetAnterieur(models.TransientModel):
    _name = 'account.asset.anterieur'

    def default_date(self):
        return fields.Date.from_string(fields.Date.context_today(self)).replace(month=1, day=1)

    date = fields.Date(default=default_date)

    def check_old_depreciation(self):
        asset_ids = self.env.context.get('active_ids', False)
        assets = self.env['account.asset.asset'].browse(asset_ids)
        if any(asset.state != 'open' for asset in assets):
            raise ValidationError("Vous devez d'abord confirmer ces immobilisations")
        if asset_ids:
            if len(asset_ids) == 1:
                self.env.cr.execute(
                    """update account_asset_depreciation_line set move_check=True where asset_id = %s and depreciation_date < %s""",
                    (asset_ids[0], self.date))
            else:
                self.env.cr.execute(
                    """update account_asset_depreciation_line set move_check=True where asset_id in %s and depreciation_date < %s""",
                    (tuple(asset_ids), self.date))
        return True