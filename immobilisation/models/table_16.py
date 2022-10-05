# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class TableSexten(models.Model):
    _name = 'immo.dotation'
    _description = 'ETAT DE DOTATIONS AUX AMORTISSEMENTS RELATIFS AUX IMMOBILISATIONS'

    name = fields.Char(string=u"Nom",default="ETAT DE DOTATIONS AUX AMORTISSEMENTS RELATIFS AUX IMMOBILISATIONS",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='immo.dotation.line',inverse_name='immo_id' )
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('immo.dotation'))
    # Code Edi
    edi_name = fields.Integer(string=u"Immobilisation concernée",default=10061,readonly=True)
    edi_date_in = fields.Integer(string='Date d\'entrée',default=1078, readonly=True)
    edi_acquisition_price = fields.Integer(string=u"Prix d\'acquisition",  default=1079, readonly=True)
    edi_revaluation_value = fields.Integer(string=u"Valeur comptable après réévaluation",  default=1080,readonly=False )
    edi_amortissement_internal = fields.Integer(string=u"Amortissements antérieurs",  default=1081,readonly=True )
    edi_taux = fields.Integer(string=u"Taux",  default=1082, readonly=True)
    edi_duration = fields.Integer(string=u"Durée", default=1083, readonly=True)
    edi_normal_amortissement = fields.Integer(string=u"Amortissements normaux ou accélérés de l'exercice",  default=1084, readonly=True)
    edi_end_amortissement = fields.Integer(string=u"Total des amortissements à la fin de l'exercice", default=1085, readonly=True)
    edi_observation = fields.Integer(string=u"Observations",  default=1086, readonly=True)  
    
    def get_lines(self):
        """This Function calculates Table 16 sub-Lines with its affectations"""
        for rec in self:
            rec.line_ids = [(5,0,0)]
            assets = self.env['account.asset.asset'].search([('id','!=',False),('company_id','=',self.env.company.id)])
            sum_initial = sum_start = 0
            for asset in assets:
                if not asset.date_cession or asset.date_cession.year >= rec.fy_n_id.date_end.year :
                    if asset.depreciation_line_ids:
                        sum_initial = sum_start = 0
                        if asset.invoice_date.year <= rec.fy_n_id.date_end.year :
                            if not asset.date_cession or  asset.date_cession.year > rec.fy_n_id.date_end.year:

                                for depreciation in asset.depreciation_line_ids:
                                    if depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                        sum_start += depreciation.amount
                                    elif depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                        sum_initial += depreciation.amount                                
                                self.env['immo.dotation.line'].create({
                                    'name':asset.name,
                                    'date_in':asset.invoice_date,
                                    'code':'',
                                    'acquisition_price':asset.value,
                                    'revaluation_value': 0.0,
                                    'amortissement_internal': asset.cumul_amortissements_anterieurs + sum_start ,
                                    'taux':(1/asset.method_number)*100,
                                    'duration':asset.method_number,
                                    'normal_amortissement':sum_initial,
                                    'end_amortissement':sum_initial + asset.cumul_amortissements_anterieurs + sum_start,
                                    'observation': asset.category_id.name ,
                                    'category_id':asset.category_id.id,
                                    'immo_id': rec.id 
                                })
                            elif asset.date_cession and asset.date_cession.year == rec.fy_n_id.date_end.year:
                                for depreciation in asset.depreciation_line_ids:
                                    if depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                        sum_start += depreciation.amount
                                    elif depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                        sum_initial += depreciation.amount                                
                                self.env['immo.dotation.line'].create({
                                    'name':asset.name,
                                    'date_in':asset.invoice_date,
                                    'code':'',
                                    'acquisition_price':asset.value,
                                    'revaluation_value': 0.0,
                                    'amortissement_internal': asset.cumul_amortissements_anterieurs + sum_start ,
                                    'taux':(1/asset.method_number)*100,
                                    'duration':asset.method_number,
                                    'normal_amortissement':sum_initial,
                                    'end_amortissement':sum_initial + asset.cumul_amortissements_anterieurs + sum_start,
                                    'observation': asset.category_id.name ,
                                    'category_id':asset.category_id.id,
                                    'immo_id': rec.id 
                                })
                                self.env['immo.dotation.line'].create({
                                    'name':asset.name,
                                    'date_in':asset.date_cession,
                                    'code':'',
                                    'acquisition_price':(-1)*(asset.value),
                                    'revaluation_value': 0.0,
                                    'amortissement_internal': (-1)*(asset.cumul_amortissements_anterieurs + sum_start) ,
                                    'taux':(1/asset.method_number)*100,
                                    'duration':asset.method_number,
                                    'normal_amortissement':(-1)*(sum_initial),
                                    'end_amortissement':(-1)*(sum_initial + asset.cumul_amortissements_anterieurs + sum_start),
                                    'observation': 'Cession du'  + str(asset.date_cession) ,
                                    'category_id':asset.category_id.id,
                                    'immo_id': rec.id 
                                })
            l = self.env['immo.dotation.line'].search([('id','=',rec.line_ids[0].id),('company_id','=',self.env.company.id)]).category_id.id
            list_ = [l]
            for line in rec.line_ids:
                if line.category_id.id != l :
                    l = line.category_id.id
                    list_.append(line.category_id.id)
            sequence = 0
            for line in list_:
                sequence +=1
                x = y = z = r = 0
                lines = self.env['immo.dotation.line'].search([('immo_id','=',rec.id),('category_id','=',line),('company_id','=',self.env.company.id)])
                for res in lines:
                    res.sequence = sequence
                    x += res.acquisition_price
                    y += res.amortissement_internal
                    z += res.normal_amortissement
                    r += res.end_amortissement
                self.env['immo.dotation.line'].create({
                                        'name':'Total General',
                                        'acquisition_price':x,
                                        'amortissement_internal': y ,
                                        'normal_amortissement':z,
                                        'end_amortissement':r,
                                        'sequence': sequence ,
                                        'category_id': line ,
                                        'immo_id': rec.id 
                                    })
                      
    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(12) # Pre-defined table ID 
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                i = 0
                acquisition_price = revaluation_value =amortissement_internal =taux = duration = normal_amortissement = end_amortissement = 0
                
                for line in rec.line_ids:
                    end_amortissement += line.end_amortissement
                    normal_amortissement += line.normal_amortissement
                    duration += line.duration
                    taux += line.taux
                    amortissement_internal += line.amortissement_internal
                    revaluation_value += line.revaluation_value
                    acquisition_price += line.acquisition_price
                    i+=1
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_name)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_date_in)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.date_in)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_acquisition_price)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.acquisition_price)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_revaluation_value)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.revaluation_value)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_amortissement_internal)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.amortissement_internal)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_taux)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.taux)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_duration)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.duration)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_normal_amortissement)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.normal_amortissement)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_end_amortissement)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.end_amortissement)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_observation)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.observation)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1088)
                etree.SubElement(valeur_cellule, "valeur").text = str(acquisition_price)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1089)
                etree.SubElement(valeur_cellule, "valeur").text = str(revaluation_value)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1090)
                etree.SubElement(valeur_cellule, "valeur").text = str(amortissement_internal)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1091)
                etree.SubElement(valeur_cellule, "valeur").text = str(taux)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1092)
                etree.SubElement(valeur_cellule, "valeur").text = str(duration)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1093)
                etree.SubElement(valeur_cellule, "valeur").text = str(normal_amortissement)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1094)
                etree.SubElement(valeur_cellule, "valeur").text = str(end_amortissement)

                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(22)
                etree.SubElement(extra_field_valeur,"valeur").text = str(normal_amortissement)
                
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(50)
                etree.SubElement(extra_field_valeur,"valeur").text = str(rec.fy_n_id.date_end)
                
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(51)
                etree.SubElement(extra_field_valeur,"valeur").text = str(rec.fy_n_id.date_start)
                
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(52)
                etree.SubElement(extra_field_valeur,"valeur").text = str(rec.fy_n_id.date_end)
            else:
                pass
                    
class TableSextenLines(models.Model):
    _name = 'immo.dotation.line'
    _description = 'ETAT DE DOTATIONS AUX AMORTISSEMENTS RELATIFS AUX IMMOBILISATIONS LIGNES'
    _order = "sequence asc, id asc"

    name = fields.Char(string=u"Immobilisation concernée",required=True,readonly=True)
    date_in = fields.Date(string='Date d\'entrée', readonly=True)
    code = fields.Char(string=u"Code", required=False, readonly=True)
    sequence  = fields.Integer(string='Sequence',readonly=True)
    acquisition_price = fields.Float(string=u"Prix d\'acquisition",  required=False, readonly=True)
    revaluation_value = fields.Float(string=u"Valeur comptable après réévaluation",  required=False,readonly=False )
    amortissement_internal = fields.Float(string=u"Amortissements antérieurs",  required=False,readonly=True )
    taux = fields.Float(string=u"Taux",  required=False, readonly=True)
    duration = fields.Integer(string=u"Durée",  required=False, readonly=True)
    normal_amortissement = fields.Float(string=u"Amortissements normaux ou accélérés de l'exercice",  required=False, readonly=True)
    end_amortissement = fields.Float(string=u"Total des amortissements à la fin de l'exercice",  required=False, readonly=True)
    observation = fields.Char(string=u"Observations",  required=False, readonly=True) 
    category_id = fields.Many2one(comodel_name="account.asset.category", string="Categorie", required=False,readonly=True)  
    immo_id = fields.Many2one(comodel_name="immo.dotation", string="Dotation", required=False,readonly=True )

    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('immo.dotation.line'))