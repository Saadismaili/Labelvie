# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class RepartitionCapitalSocial(models.Model):
    _name = 'repartition.capital.social'
    _description = 'ETAT DE REPARTITION DU CAPITAL SOCIAL'

    name = fields.Char(string=u"Nom",default="ETAT DE REPARTITION DU CAPITAL SOCIAL",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    repartition_capital_social_line_ids = fields.One2many(comodel_name="repartition.capital.social.line", inverse_name="repartition_capital_social_id", string="Lignes", required=False, copy=True )

    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('repartition.capital.social'))

    edi_name = fields.Integer(string=u"Nom, prénoms des principaux associés",readonly=True,default=2094)
    edi_raison_social = fields.Integer(string=u"raison sociale des principaux associés",readonly=True,default=17887)
    edi_n_if = fields.Integer(string=u"IF",readonly=True,default=13536)
    edi_n_cin = fields.Integer(string=u"CIN",readonly=True,default=13537)
    edi_n_etr = fields.Integer(string=u"N° Carte d'étranger",readonly=True,default=14560)
    edi_adresse = fields.Integer(string=u"Adresse",readonly=True,default=2095)
    edi_nbre_titre_exe_prec = fields.Integer(string=u"Nbre de titre de l'exercice précedent",  readonly=True,default=2096 )
    edi_nbre_titre_exe_actuel = fields.Integer(string=u"Nbre de titre de l'exercice actuel",  readonly=True,default=2097 )
    edi_valeur_nominal = fields.Integer(string=u"valeur nominal de chaque action ou part sociale",  readonly=True,default=2098 )
    edi_montant_capital_souscrit = fields.Integer(string=u"Montant du capital souscrit",  readonly=True, default=2099)
    edi_montant_capital_appele = fields.Integer(string=u"Montant du capital appelé",  readonly=True,default=2100 )
    edi_montant_capital_libere = fields.Integer(string=u"Montant du capital Libéré",  readonly=True,default=2101 )
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    check_line = fields.Boolean(string="check", default = False, readonly=True,compute='check_lines',store=True)
    @api.depends('repartition_capital_social_line_ids')
    def check_lines(self):
        for rec in self: 
            if rec.repartition_capital_social_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
                
    def get_lines(self):
        for rec in self: 
            if rec.repartition_capital_social_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
    def get_xml(self,parent):
        for rec in self:
            if rec.repartition_capital_social_line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(41) # Pre-defined table ID 
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                i = 0
                capital = 0
                for line in rec.repartition_capital_social_line_ids:
                    i+=1
                    capital += line.montant_capital_souscrit
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_name)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_raison_social)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.raison_social)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_n_if)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.n_if)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_n_cin)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.n_cin)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_n_etr)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.n_etr)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_adresse)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.adresse)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_nbre_titre_exe_prec)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.nbre_titre_exe_prec)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_nbre_titre_exe_actuel)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.nbre_titre_exe_actuel)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_valeur_nominal)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.valeur_nominal)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_montant_capital_souscrit)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_capital_souscrit)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_montant_capital_appele)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_capital_appele)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_montant_capital_libere)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_capital_libere)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(18)
                etree.SubElement(extra_field_valeur,"valeur").text = str(capital)
            else:
                pass
class RepartitionCapitalSocialLine(models.Model):
    _name = 'repartition.capital.social.line'
    _description = 'LIGNES ETAT DE REPARTITION DU CAPITAL SOCIAL'

    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('repartition.capital.social.line'))
    name = fields.Char(string=u"Nom, prénoms des principaux associés",required=True,)
    raison_social = fields.Char(string=u"raison sociale des principaux associés",required=True,)
    n_if = fields.Integer(string=u"IF",required=False,)
    n_cin = fields.Char(string=u"CIN",required=False,)
    n_etr = fields.Char(string=u"N° Carte d'étranger",required=False,)
    adresse = fields.Char(string=u"Adresse",required=False,)
    nbre_titre_exe_prec = fields.Integer(string=u"Nbre de titre de l'exercice précedent",  required=False, )
    nbre_titre_exe_actuel = fields.Integer(string=u"Nbre de titre de l'exercice actuel",  required=False, )
    valeur_nominal = fields.Float(string=u"valeur nominal de chaque action ou part sociale",  required=False, )
    montant_capital_souscrit = fields.Float(string=u"Montant du capital souscrit",  required=False, )
    montant_capital_appele = fields.Float(string=u"Montant du capital appelé",  required=False, )
    montant_capital_libere = fields.Float(string=u"Montant du capital Libéré",  required=False, )
    repartition_capital_social_id = fields.Many2one(comodel_name="repartition.capital.social", string="REPARTITION DU CAPITAL SOCIAL", required=False, )