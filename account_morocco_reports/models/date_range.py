from odoo import models, fields, api , _ 
from odoo.exceptions import ValidationError


class DateRangeInheritance(models.Model):
    
    _inherit = 'date.range'
    
    is_config  = fields.Boolean(string='Date par défaut ?', default=False,readonly=True)

    @api.constrains("is_config")
    def _check_is_config(self):
        for rec in self:
            ranges = self.env['date.range'].search([('is_config','=',True),('id','!=',rec.id)])
            if rec.is_config:
                if ranges:
                    raise ValidationError(_("La date par défaut a etait deja configuré sur votre systéme"))

class DefaultDate(models.TransientModel):
    _name = 'default.date'

    range_id= fields.Many2one(
        'date.range',
        string = 'Exercice')
    
    def set_function(self):
        for rec in self:
            ranges = self.env['date.range'].search([('id','!=',rec.range_id.id)])
            if ranges:
                for date in ranges:
                    date.is_config = False
                    
            if rec.range_id:
                rec.range_id.is_config = True
                
                
                