from odoo import models, fields, api, _    


class AccountAssetInherit(models.Model):
    _inherit = 'account.asset.asset'
    _description = 'Asset/Revenue Recognition'
    _inherit = ['mail.thread', 'mail.activity.mixin']