# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)


class TitreParticipation(models.Model):
    _name = 'titre.participation'
    _description = 'TITRE DE PARTICIPATION'

    name = fields.Char(string=u"Nom",default="TABLEAU DES TITRES DE PARTICIPATION",required=True,)
    # Relational Fields
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('titre.participation'))
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    titre_participation_line_ids = fields.One2many(comodel_name="titre.participation.line", inverse_name="titre_participation_id", string="Lignes", required=False, copy=True)
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    # Code Edi 
    edi_name = fields.Integer(string=u"Raison sociale de la Société émettrice",required=True,default=2044)
    edi_code = fields.Integer(string=u"Code", required=True, default=14065)
    edi_secteur_activite = fields.Integer(string=u"Secteur d'activité",required=False,default=2045)
    edi_capital_social = fields.Integer(string=u"Capital social",  required=False,default=2046 )
    edi_participation_capital = fields.Integer(string=u"Participation au capital en %",  required=False,default=2047 )
    edi_prix_acquisition = fields.Integer(string=u"Prix d'acquisition global",  required=False,default=2048 )
    edi_valeur_comptable_nette = fields.Integer(string=u"Valeur comptable nette",  required=False,default=2049 )
    edi_date_cloture = fields.Integer(string=u"Date de cloture" ,required=False,default=2050 )
    edi_situation_nette = fields.Integer(string=u"Situation nette",  required=False, default=2051)
    edi_resultat_net = fields.Integer(string=u"Résultat net",  required=False,default=2052 )
    edi_produits_inscrits = fields.Integer(string=u"Produits inscrits au C.P.C de l'exercice",  required=False,default=2053 )
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    check_line = fields.Boolean(string="check", default = False, readonly=True,compute='check_lines',store=True)
    @api.depends('titre_participation_line_ids')
    def check_lines(self):
        for rec in self: 
            if rec.titre_participation_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
                
    def get_lines(self):
        for rec in self: 
            if rec.titre_participation_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
    
    def get_xml(self,parent):
        for rec in self:
            if rec.titre_participation_line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(39) # read documentation XML
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                i = 0
                val_1 = val_2 = val_3 = val_4 = val_5 = val_6 = val_7 = val_8 = 0
                for line in rec.titre_participation_line_ids:
                    i += 1
                    val_1 += line.capital_social
                    val_2 += line.participation_capital
                    val_3 += line.prix_acquisition
                    val_4 += line.valeur_comptable_nette
                    val_5 += line.situation_nette
                    val_6 += line.resultat_net
                    val_7 += line.produits_inscrits
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_name)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_code)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.code)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_secteur_activite)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.secteur_activite)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_capital_social)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.capital_social)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_participation_capital)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.participation_capital)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_prix_acquisition)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.prix_acquisition)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_valeur_comptable_nette)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.valeur_comptable_nette)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_date_cloture)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.date_cloture)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_situation_nette)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.situation_nette)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_resultat_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.resultat_net)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_produits_inscrits)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.produits_inscrits)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2056)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_1)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2057)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_2)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2058)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_3)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2059)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_4)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2061)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_5)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2062)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_6)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(2063)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_7)
                    
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
            else:
                pass
    
class TitreParticipationLine(models.Model):
    _name = 'titre.participation.line'
    _description = 'LIGNES DES TITRES DE PARTICIPATION'

    
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('titre.participation.line'))
    name = fields.Char(string=u"Raison sociale de la Société émettrice",required=True,)
    code = fields.Char(string=u"N° IF", required=True, )
    secteur_activite = fields.Char(string=u"Secteur d'activité",required=False,)
    capital_social = fields.Float(string=u"Capital social",  required=False, )
    participation_capital = fields.Float(string=u"Participation au capital en %",  required=False, )
    prix_acquisition = fields.Float(string=u"Prix d'acquisition global",  required=False, )
    valeur_comptable_nette = fields.Float(string=u"Valeur comptable nette",  required=False, )
    date_cloture = fields.Date(string=u"Date de cloture" ,required=False, )
    situation_nette = fields.Float(string=u"Situation nette",  required=False, )
    resultat_net = fields.Float(string=u"Résultat net",  required=False, )
    produits_inscrits = fields.Float(string=u"Produits inscrits au C.P.C de l'exercice",  required=False, )
    
    titre_participation_id = fields.Many2one(comodel_name="titre.participation", string="Titre Participation", required=False, )