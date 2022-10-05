from odoo import models, fields, api   

class FullReconcileInherit(models.Model):
    _inherit = 'account.full.reconcile'
    
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('account.full.reconcile'))
    
    	