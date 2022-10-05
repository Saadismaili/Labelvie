from odoo import models, fields,api     


class InheritAccountMove(models.Model):
    _inherit = 'account.move'
    
    declared   = fields.Boolean(string='Déclarer à la tva ?', default = False)