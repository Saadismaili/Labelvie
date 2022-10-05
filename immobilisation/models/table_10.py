# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from lxml import etree
import base64
import zipfile
from odoo.exceptions import UserError, ValidationError
import os
import openpyxl
import xlrd
import io
import csv
import pandas
directory = os.path.dirname(__file__)

class TableTen(models.Model):
    _name = 'immo.immobilisation'
    _description = 'Immobilisation'

    name = fields.Char(string=u"Nom",default="Immobilisation",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='immo.immobilisation.line',inverse_name='immo_id' )
    
    # Code edi 
    edi_date_in = fields.Integer(string='Date de cession', readonly=True,default=1929)
    edi_code = fields.Integer(string=u"Compte principal", required=False, readonly=True,default=1930)
    edi_montant_brut = fields.Integer(string=u"Montant brut",  required=False, readonly=True,default=1931)
    edi_amortissement_cumul = fields.Integer(string=u"Amortissements Cumulés",  required=False,readonly=True,default=1932 )
    edi_amortissement_net = fields.Integer(string=u"Valeur nette d\'amortissements",  required=False, readonly=True,default=1933)
    edi_cession = fields.Integer(string=u"Produit de cession",required=True,readonly=True,default=1934)
    edi_plus_value = fields.Integer(string=u"Plus value",  required=False, readonly=True,default=1935)   
    edi_minece_value = fields.Integer(string=u"Moins value",  required=False, readonly=True,default=1936)   
    
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('immo.immobilisation'))
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    check_line = fields.Boolean(string="check", default = False, readonly=True,compute='check_lines',store=True)
    
    # action function to open wizard that allows us to import tab cession
    def action_open_import(self):
        for rec in self:
            return {
            'name': 'Importer',
            'type': 'ir.actions.act_window',
            'res_model': 'immo.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {'default_immobilisation_id': rec.id}
            }
    @api.depends('line_ids')
    def check_lines(self):
        for rec in self: 
            if rec.line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
                
    def get_lines(self):
        """This Function calculates Table 10 sub-Lines with its affectations"""
        for rec in self:
            rec.line_ids = [(5,0,0)]
            assets = self.env['account.asset.asset'].search([('id','!=',False),('company_id','=',self.env.company.id),])
            sum_initial = sum_start = diff_days = 0
            for asset in assets:
                if asset.date_cession: 
                    if asset.date_cession.year == rec.fy_n_id.date_end.year :
                        if asset.state in ['close','open']:
                            if asset.depreciation_line_ids:
                                sum_initial = sum_start = plus = moins = diff_days = value_day = 0
                                for depreciation in asset.depreciation_line_ids:
                                    if depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                        sum_start += depreciation.amount
                                    elif depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                        diff_days = datetime.strptime(str(depreciation.depreciation_date), "%Y-%m-%d") - datetime.strptime(str(asset.date_cession), "%Y-%m-%d")
                                        value_day = depreciation.amount / 366
                                        sum_start += (366 - diff_days.days) * value_day
                                if (asset.cession_price_ht - asset.value + sum_start) > 0 :
                                    plus = asset.cession_price_ht - asset.value + sum_start
                                else:
                                    moins = abs(asset.cession_price_ht - asset.value + sum_start)
                                move_lines = self.env['account.move.line'].search([('account_id','=',asset.category_id.account_revenue_id.id),('move_id.asset_id','=',asset.id),('move_id.company_id','=',self.env.company.id)])
                                cession = 0
                                if move_lines.exists():
                                    for line in move_lines:
                                        cession += abs(line.debit - line.credit)                  
                                self.env['immo.immobilisation.line'].create({
                                    
                                    'date_in':asset.date_cession,
                                    'code':asset.category_id.account_immo_id.code + ' ' + asset.category_id.account_immo_id.name,
                                    'montant_brut':asset.value,
                                    'amortissement_cumul': sum_start,
                                    'amortissement_net': asset.value - sum_start ,
                                    'cession':cession,
                                    'plus_value':plus,
                                    'minece_value':moins,
                                    'immo_id': rec.id 
                                })
            if rec.line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(38)
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                i = 0
                val_1 = val_2 = val_3 = val_4 = val_5 = val_6 = 0 
                for line in rec.line_ids:
                    date_in = ''
                    i += 1
                    val_1 += line.montant_brut
                    val_2 += line.amortissement_cumul
                    val_3 += line.amortissement_net
                    val_4 += line.cession
                    val_5 += line.plus_value
                    val_6 += line.minece_value
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_date_in)
                    date_in = str(line.date_in)
                    date_in = date_in.split(' ')
                    etree.SubElement(valeur_cellule, "valeur").text = str(date_in[0])
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_code)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.code)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_montant_brut)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_brut)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_amortissement_cumul)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.amortissement_cumul)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_amortissement_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.amortissement_net)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_cession)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.cession)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_plus_value)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.plus_value)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_minece_value)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.minece_value)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2038)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_1)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2039)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_2)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2040)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_3)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2041)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_4)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2042)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_5)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2043)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_6)
                    
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(72)
                etree.SubElement(extra_field_valeur,"valeur").text = str(rec.fy_n_id.date_end)
            else:
                pass
                    
class TableTenLines(models.Model):
    _name = 'immo.immobilisation.line'
    _description = 'immobilisation Lines'

    cession = fields.Float(string=u"Produit de cession",required=True,readonly=True)
    date_in = fields.Datetime(string='Date de cession', readonly=True)
    code = fields.Char(string=u"Compte principal", required=False, readonly=True)
    montant_brut = fields.Float(string=u"Montant brut",  required=False, readonly=True)
    amortissement_cumul = fields.Float(string=u"Amortissements Cumulés",  required=False,readonly=True )
    amortissement_net = fields.Float(string=u"Valeur nette d\'amortissements",  required=False, readonly=True)
    plus_value = fields.Float(string=u"Plus value",  required=False, readonly=True)   
    minece_value = fields.Float(string=u"Moins value",  required=False, readonly=True)   
    # relational fields
    immo_id = fields.Many2one(comodel_name="immo.immobilisation", string="Immobilisation", required=False,readonly=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('immo.immobilisation.line'))


class ImmoWizard(models.TransientModel):
    _name = 'immo.wizard'

    immobilisation_id = fields.Many2one(comodel_name="immo.immobilisation", readonly=True)
    
    file = fields.Binary(string="Séléctionner un fichier excel", required=True)
    
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('immo.wizard'))
    def create_objects(self,model_ref,values):
        return self.env[model_ref].create(values)

    def import_cession(self):
        df = pandas.io.excel.read_excel(base64.b64decode(self.file), engine='xlrd',
        dtype={'Date': str,
               'Compte':str,
               'Brut':str,
               'Cumul':str,
               'Net':str,
               'Cession':str,
               'Plus':str,
               'Moins':str,
               })
        values = df['Date'].values
        date = values
        values = df['Compte'].values
        compte = values
        values = df['Brut'].values
        brut = values
        values = df['Cumul'].values
        cumul = values
        values = df['Net'].values
        net = values
        values = df['Cession'].values
        cession = values
        values = df['Plus'].values
        plus = values
        values = df['Moins'].values
        moins = values
        for date,compte, brut, cumul, net, cession, plus, moins   in zip(date,compte, brut, cumul, net, cession, plus, moins ):
            account = self.env['account.account'].search([('code','=',str(compte)),('company_id','=',self.company_id.id)])
            if not account.exists():
                raise ValidationError(_('Ce Compte " %s " n\'exist pas dans le plan comptable Maroccain, veuillez corriger votre fichier puis réessayer' % (compte)))
            else:
                cession_lines = [{
                    'cession' : cession,
                    'date_in' :date,
                    'code':compte,
                    'amortissement_cumul' : cumul ,                   
                    'montant_brut':brut ,
                    'amortissement_net' :net ,
                    'plus_value' :plus ,
                    'minece_value' :moins ,
                    'immo_id' :self.immobilisation_id.id  ,
                    'company_id' :self.company_id.id  ,
                }]
                self.create_objects('immo.immobilisation.line',cession_lines)