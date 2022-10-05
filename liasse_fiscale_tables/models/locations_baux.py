# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class LocationsBaux(models.Model):
    _name = 'locations.baux'
    _description = 'Locations Baux'

    name = fields.Char(string=u"Nom",default="TABLEAU DES LOCATIONS ET BAUX AUTRES QUE LE CREDIT-BAIL",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    locations_baux_line_ids = fields.One2many(comodel_name="locations.baux.line", inverse_name="locations_baux_id", string="Lignes", required=False, copy=True, )

    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('locations.baux'))

    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    check_line = fields.Boolean(string="check", default = False, readonly=True,compute='check_lines',store=True)
    @api.depends('locations_baux_line_ids')
    def check_lines(self):
        for rec in self: 
            if rec.locations_baux_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
                
    def get_lines(self):
        for rec in self: 
            if rec.locations_baux_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
    
    def get_xml(self,parent):
        for rec in self:
            if rec.locations_baux_line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(28) # read documentation
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                i=0
                val_1 = val_2 = val_3 = 0
                for line in rec.locations_baux_line_ids:
                    i+=1
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(1267)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(1268)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.lieu_situation)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(1269)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.nom_prenom)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(14964)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.raison)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(14965)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.adress)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(14040)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.n_if)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(14041)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.n_cin)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(17919)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.date_conclusion)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(1270)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.card_num)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(1271)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_annuel)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(1272)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_loyer)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(1273)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.nature_contrat_bail)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(1274)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.nature_contrat_period)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    val_1 += line.n_if
                    val_2 += line.montant_annuel
                    val_3 += line.montant_loyer
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14042)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_1)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1279)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_2)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1280)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_3)
                    
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
            else:
                pass
class LocationsBauxLine(models.Model):
    _name = 'locations.baux.line'
    _description = 'LIGNES Locations Baux'

    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('locations.baux.line'))
    name = fields.Char(string=u"Nature du bien loué",required=True,)
    code = fields.Char(string=u"Code",required=True,)
    lieu_situation = fields.Char(string=u"Lieu de Situation",required=False,)
    nom_prenom = fields.Char(string=u"Nom et prénoms du propriétaire",  required=False, )
    raison = fields.Char(string=u"Raison sociale du propriétaire",  required=False, )
    adress = fields.Char(string=u"Aresse du propriétaire",  required=False, )
    n_if = fields.Integer(string=u"N° IF du propriétaire",  required=False, )
    n_cni = fields.Char(string=u"N° CNI du propriétaire",  required=False, )
    date_conclusion = fields.Date(string="Date de conclusion de l'acte de location",required=False, )
    montant_annuel = fields.Float(string="Montant annuel de location",  required=False, )
    card_num = fields.Char(string=u"N° Carte du propriétaire",  required=False, )
    montant_loyer = fields.Float(string="Montant du loyer compris dans les charges de l'exercice",  required=False, )
    nature_contrat_bail = fields.Char(string=u"Nature du contrat-Bail-ordinaire", required=False, )
    nature_contrat_period = fields.Char(string=u"(Nème période)", required=False, )
    locations_baux_id = fields.Many2one(comodel_name="locations.baux", string="Locations Baux", required=False, )