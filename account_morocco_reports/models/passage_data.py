from odoo import models, fields, api, _   


class PassageEnterieur(models.Model):
    _name = 'passage.enterieur'
    
    name  = fields.Char(string='Nom', default = 'Valeur anterieur de tableau passage, partie  Cumulatif')
    date  = fields.Date(string='Date de l\'exercice')
    cumule_amorti  = fields.Float(string='CUMUL DES AMORTISSEMENTS DIFFERES')
    exercice_n_4 = fields.Float(string='Valeur pour Exercice N-4')
    exercice_n_3 = fields.Float(string='Valeur pour Exercice N-3')
    exercice_n_2 = fields.Float(string='Valeur pour Exercice N-2')
    exercice_n_1 = fields.Float(string='Valeur pour Exercice N-1')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('passage.enterieur'))
