# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from odoo.exceptions import UserError, ValidationError

class DateRangeInherit(models.Model):
    _inherit = 'date.range'
    
    state  = fields.Selection(string='Statue', selection=[('open', 'Ouvert'),('closed', 'Fermé')],default='open')
    
    def change_state(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                moves = self.env['account.move'].search([('date','<=', rec.date_end),('date','>=',rec.date_start),('company_id','=',rec.company_id.id)])
                for move in moves:
                    if move.state == 'draft':
                        raise ValidationError(_('vous ne pouvez pas fermé l\'année fiscal puisque vous avez déjà ce mouvement %s en etat bruillon ' % (move.name)))
                rec.state = 'closed'
    
    def set_to_open(self):
        for rec in self:
            rec.state = 'open'

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    
    
    @api.constrains("date")
    def _check_date(self):
        for rec in self:
            date_range = self.env['date.range'].search([('date_start','<=',rec.date),('type_id.fiscal_year','=',True),('date_end','>=',rec.date),('company_id','=',rec.company_id.id)])
            if date_range.state == 'closed':
                raise ValidationError(_('Vous avez déjà fermé cette année fical'))
        
