# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class InteretsEmprunts(models.Model):
    _name = 'interets.emprunts'
    _description = 'ETAT DES INTERETS DES EMPRUNTS'

    name = fields.Char(string=u"Nom",default="ETAT DES INTERETS DES EMPRUNTS CONTRACTES AUPRES DES ASSOCIES ET DES TIERS",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    interets_emprunts_line_ids = fields.One2many(comodel_name="interets.emprunts.line", inverse_name="interets_emprunts_id", string="Lignes", required=False, copy=True, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('interets.emprunts'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    check_line = fields.Boolean(string="check", default = False, readonly=True,compute='check_lines',store=True)
    @api.depends('interets_emprunts_line_ids')
    def check_lines(self):
        for rec in self: 
            if rec.interets_emprunts_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
                
    def get_lines(self):
        for rec in self: 
            if rec.interets_emprunts_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
    
    def get_xml(self,parent):
        for rec in self:
            if rec.interets_emprunts_line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(27) # read documentation
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                val_1 = val_2 = val_3 = val_4 = val_5 = val_6 = val_7 = 0
                i = 0
                for line in rec.interets_emprunts_line_ids:
                    i+=0
                    val_0 += line.n_if
                    val_1 += line.montant_pret
                    val_2 += line.duree_pret
                    val_3 += line.charge_financiere
                    val_4 += line.remboursement_exercice_ant_principal
                    val_5 += line.remboursement_exercice_ant_intertet
                    val_6 += line.remboursement_exercice_actuel_principal
                    val_7 += line.remboursement_exercice_actuel_intertet
                    
                    if line.type == 'a':
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1208)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14969)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.code)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)

                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1209)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.adresse)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1210)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.n_if)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14968)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.cin)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1211)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_pret)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1212)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.date_pret)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1213)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.duree_pret)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1214)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.taux_interet)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1215)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.charge_financiere)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1216)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.remboursement_exercice_ant_principal)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1217)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.remboursement_exercice_ant_intertet)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1218)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.remboursement_exercice_actuel_principal)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1219)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.remboursement_exercice_actuel_intertet)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1220)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.observations)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    elif line.type == 'b':
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1221)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14970)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.code)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)

                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1222)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.adresse)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1223)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.n_if)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14971)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.cin)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1224)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_pret)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1225)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.date_pret)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1226)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.duree_pret)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1227)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.taux_interet)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1228)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.charge_financiere)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1229)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.remboursement_exercice_ant_principal)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1250)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.remboursement_exercice_ant_intertet)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1251)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.remboursement_exercice_actuel_principal)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1252)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.remboursement_exercice_actuel_intertet)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(1253)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.observations)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1256)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_0)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1257)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_1)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1259)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_2)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1261)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_3)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1262)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_4)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1263)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_5)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1264)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_6)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1265)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_7) 
                   
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(55)
                etree.SubElement(extra_field_valeur,"valeur").text = str(rec.fy_n_id.date_end)
            else:
                pass
class InteretsEmpruntsLine(models.Model):
    _name = 'interets.emprunts.line'
    _description = 'LIGNES ETAT DES INTERETS DES EMPRUNTS'

    type = fields.Selection([
        ('a', u'Associés'),
        ('b', u'Tiers'),
    ],
        string="Type", required = True)
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('interets.emprunts'))
    name = fields.Char(string=u"Nom prénoms",required=True,)
    code = fields.Char(string=u"raison sociale", required=True, )
    adresse = fields.Char(string=u"Adresse",required=True,)
    n_if = fields.Integer(string=u"N° IF",required=True,)
    cin = fields.Char(string=u"N° C.I.N.ou Article I.S.",required=True,)
    montant_pret = fields.Float(string=u"Montant du prêt",  required=False, )
    date_pret = fields.Date(string=u"Date du prêt",required=False, )
    duree_pret = fields.Integer(string=u"Durée du prêt(en mois)", required=False, )
    taux_interet = fields.Char(string=u"Taux d'intérêts",  required=False, )
    charge_financiere = fields.Float(string=u"Charge financière globlale",  required=False, )
    remboursement_exercice_ant_principal = fields.Float(string=u"Remboursement Exercice antérieurs principal",  required=False, )
    remboursement_exercice_ant_intertet = fields.Float(string=u"Remboursement Exercice antérieurs Interêt",  required=False, )
    remboursement_exercice_actuel_principal = fields.Float(string=u"Remboursement Exercice actuel principal",  required=False, )
    remboursement_exercice_actuel_intertet = fields.Float(string=u"Remboursement Exercice actuel Interêt",  required=False, )
    remboursement_exercice_ant = fields.Float(string=u"Remboursement Exercice antérieurs",  required=False, )
    observations = fields.Text(string=u"Observations", required=False, )
    interets_emprunts_id = fields.Many2one(comodel_name="interets.emprunts", string="Interets Emprunts", required=False, )