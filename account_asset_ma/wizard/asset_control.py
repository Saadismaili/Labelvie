# -*- coding: utf-8 -*-


import datetime

from odoo import models, fields, api


class AssetControl(models.Model):
    _name = 'asset.control'

    fiscal_year = fields.Many2one('date.range', 'Exercice fiscal', required=True)
    control_ids = fields.One2many('asset.control.line', 'asset_control_id',
                                 string='Asset Control', readonly=True,)
    control_accounting_ids = fields.One2many('asset.control.accounting', 'asset_control_id',
                                 string='Asset Control Accounting', readonly=True,)
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('asset.control'))

    # generate the control
    def calculate_values(self):
        for rec  in self :
            controls = self.env['asset.control.line'].search([('asset_control_id','=',self.id),('company_id','=',self.env.company.id)])
            if len(controls)>0:
                for control in controls:
                    depreciation_value = 0
                    asset_value = 0
                    line_value = 0
                    for asset in control.asset_ids:
                        for depreciation in asset.depreciation_line_ids:
                            if depreciation.depreciation_date.year <= rec.fiscal_year.date_end.year:
                                depreciation_value += depreciation.amount
                    for asset in control.asset_ids:
                        asset_value += asset.value
                    for move in control.move_ids:
                        for line in move.line_ids:
                            if control.account_id.id == line.account_id.id :
                                line_value += line.debit - line.credit if str(line.account_id.code[0]+line.account_id.code[1]) !='28' else line.credit - line.debit 
                    control.write({
                        'balance_asset': depreciation_value if str(control.account_id.code[0]+control.account_id.code[1]) == '28' else asset_value,
                        'balance_account': line_value,
                        'diff_amount': depreciation_value - abs(( line_value)) if str(control.account_id.code[0]+control.account_id.code[1]) == '28' else asset_value - abs(( line_value)),
                    })

    def asset_control(self):
        for rec in self :
            self.env['asset.control.line'].search([('id','!=',False),('company_id','=',self.env.company.id)]).unlink()
            self.control_accounting_ids = False     
            # Control Accounting
            depreciation_ids = self.env['account.asset.depreciation.line'].search([('depreciation_date', '>=', self.fiscal_year.date_start),
                                                                                ('depreciation_date', '<=',self.fiscal_year.date_end),
                                                                                ('move_check', '=', False),
                                                                                ('company_id','=',self.env.company.id)

                                                                                ])
            for dep in depreciation_ids:
                self.env['asset.control.accounting'].create({'asset_control_id': self.ids[0],
                                                    'depreciation_date': dep.depreciation_date,
                                                    'asset_id': dep.asset_id.id,
                                                    'amount': dep.amount,
                                                    'account_id': dep.asset_id.category_id.account_asset_id.id,
                                                    })
            # Control Immobilisation
            assets = self.env['account.asset.asset'].search([('name','!=',False),('company_id','=',self.env.company.id)])
            
            for asset in assets:
                moves_lines  = self.env['account.move.line'].search([('company_id','=',self.env.company.id),('account_id','in',[asset.category_id.account_immo_id.id,asset.category_id.account_asset_id.id])])
                for line in moves_lines:
                    # if line.move_id.asset_id.id == asset.id:
                    if str(line.account_id.code[0]+line.account_id.code[1]) in ['21','22','23','28']:
                        controls = self.env['asset.control.line'].search([('company_id','=',self.env.company.id),('account_id','=',line.account_id.id),('asset_control_id','=',self.id)])
                        if  asset.date.year >= self.fiscal_year.date_end.year and not asset.date_cession :
                            if len(controls)>0:
                                line_value = 0
                                asset_value = 0
                                for control in controls:
                                    asset_value += asset.value
                                    line_value += line.debit - line.credit if str(line.account_id.code[0]+line.account_id.code[1]) !='28' else line.credit - line.debit 
                                    control.write({
                                        'asset_control_id': self.id,
                                        'balance_asset': asset_value,
                                        'balance_account': line_value,
                                        'diff_amount': asset_value - abs(( line_value)),
                                        'move_ids':[(4,line.move_id.id)],
                                        'asset_ids':[(4,asset.id)],
                                    })
                            else:
                                self.env['asset.control.line'].create({
                                            'asset_control_id': rec.id,
                                            'account_id': line.account_id.id,
                                            'balance_asset':asset.value,
                                            'balance_account':line.debit - line.credit if str(line.account_id.code[0]+line.account_id.code[1]) !='28' else line.credit - line.debit,
                                            'diff_amount': asset.value - abs((line.debit - line.credit)) if str(line.account_id.code[0]+line.account_id.code[1]) !='28' else  asset.value - abs((line.credit - line.debit)) ,
                                            'move_ids':[(4,line.move_id.id)],
                                            'asset_ids':[(4,asset.id)],
                                        })
        return rec.calculate_values()

class AssetControlLine(models.Model):
    _name = "asset.control.line"
    
    
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('asset.control.line'))

    account_id = fields.Many2one('account.account', 'Compte')
    balance_asset = fields.Float(string='Solde Immobilisation')
    balance_account = fields.Float(string='Solde Ecritures Comptables')
    diff_amount = fields.Float(string='Difference')
    is_reconciled = fields.Boolean(u'Reconcilie', default=True)
    unreconciled_ids = fields.One2many('asset.unreconciled', 'asset_control_line_id',
                                       string='Asset Unreconciled', readonly=True,)
    asset_control_id = fields.Many2one('asset.control', 'Asset Control')

    asset_ids = fields.Many2many('account.asset.asset',string = 'Les immobilisations')
    move_ids = fields.Many2many('account.move', string = 'Les Mouvements')


class AssetControlAccounting(models.Model):
    _name = "asset.control.accounting"

    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('asset.control.accounting'))
    asset_id = fields.Many2one('account.asset.asset', string='Asset', required=True, ondelete='cascade')
    account_id = fields.Many2one('account.account', 'Compte')
    amount = fields.Float(string=u'Amortissement', digits=0, required=True)
    depreciation_date = fields.Date('Depreciation Date')
    asset_control_id = fields.Many2one('asset.control', 'Asset Control')

class AssetInherit(models.Model):
    _inherit = "account.asset.asset"

    control_id = fields.Many2one('asset.control.line', string='Control', required=False,)


class MoveInherit(models.Model):
    _inherit= "account.move"

    control_id = fields.Many2one('asset.control.line', string='Control', required=False,)

class AssetUnreconciled(models.Model):
    _name = "asset.unreconciled"

    account_id = fields.Many2one('account.account', 'Compte')
    move_id = fields.Many2one('account.move', 'Piece Comptable')
    date = fields.Date(string='Date Ecriture')
    journal_id = fields.Many2one('account.journal', 'Journal')
    debit = fields.Float(string='Debit')
    credit = fields.Float(string='Credit')
    asset_control_line_id = fields.Many2one('asset.control.line', 'Asset Control Line')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('asset.unreconciled'))
