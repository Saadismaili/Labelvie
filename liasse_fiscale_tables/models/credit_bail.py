# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)

class CreditBail(models.Model):
    _name = 'credit.bail'
    _description = 'TABLEAU DES BIENS EN CREDIT BAIL'

    name = fields.Char(string=u"Nom",default="TABLEAU DES BIENS EN CREDIT BAIL",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    
    # Code edi
    edi_name = fields.Integer(string=u"Code Edi Rubrique",default=1098,readonly=True)
    edi_date_premiere_echeance = fields.Integer(string=u"Code Edi Date de la 1ère échéance",default=1099,readonly=True )
    edi_duuree_contrat = fields.Integer(string=u"Code Edi Durée du contrat en mois", default=1100,readonly=True )
    edi_valeur_estimee = fields.Integer(string=u"Code Edi Valeur estimée du bien à la date du contrat",  default=1101, readonly=True)
    edi_duuree_theorique = fields.Integer(string=u"Code Edi Durée théorique d'amortissement du bien", default=1102,readonly=True )
    edi_cumul_redevance = fields.Integer(string=u"Code Edi Cumul des exercices précedents des redevances", default=1103,readonly=True )
    edi_montant_redevance = fields.Integer(string=u"Code Edi Montant de l'exercice des redevances", default=1104, readonly=True)
    edi_redevance_restant_moins = fields.Integer(string=u"Code Edi Redevances restant à payer A moins d'un an", default=1105,readonly=True )
    edi_redevance_restant_plus = fields.Integer(string=u"Code Edi Redevances restant à payer A plus d'un an", default=1106,readonly=True )
    edi_prix_achat_fin_contrat = fields.Integer(string=u"Code Edi Prix d'achat résiduel en fin de contrat",  default=1107, readonly=True)
    edi_observations = fields.Integer(string=u"Code Edi Observations", default=1108,readonly=True )
    
    # Relational Fields
    credit_bail_line_ids = fields.One2many(comodel_name="credit.bail.line", inverse_name="credit_bail_id", string="Lignes", required=False, copy=True)
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('credit.bail'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    check_line = fields.Boolean(string="check", default = False, readonly=True,compute='check_lines',store=True)
    @api.depends('credit_bail_line_ids')
    def check_lines(self):
        for rec in self: 
            if rec.credit_bail_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
                
    def get_lines(self):
        for rec in self: 
            if rec.credit_bail_line_ids:
                rec.check_line = True
            else:
                rec.check_line = False
    
    def get_xml(self,parent):
        for rec in self:
            if rec.credit_bail_line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(23) # read documentation
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                i=0
                for line in rec.credit_bail_line_ids:
                    i+=1
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_name)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_date_premiere_echeance)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.date_premiere_echeance)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_duuree_contrat)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.duuree_contrat)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_valeur_estimee)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.valeur_estimee)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_duuree_theorique)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.duuree_theorique)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_cumul_redevance)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.cumul_redevance)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_montant_redevance)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_redevance)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_redevance_restant_moins)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.redevance_restant_moins)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_redevance_restant_plus)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.redevance_restant_plus)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_prix_achat_fin_contrat)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.prix_achat_fin_contrat)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(rec.edi_observations)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.observations)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(53)
                etree.SubElement(extra_field_valeur,"valeur").text = str(rec.fy_n_id.date_end)
            else:
                pass
class CreditBailLine(models.Model):
    _name = 'credit.bail.line'
    _description = 'LIGNES TABLEAU DES BIENS EN CREDIT BAIL'
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('credit.bail.line'))
    name = fields.Char(string=u"Rubrique",required=True,)
    code = fields.Char(string=u"Code", required=True, )
    date_premiere_echeance = fields.Date(string=u"Date de la 1ère échéance",required=False, )
    duuree_contrat = fields.Integer(string=u"Durée du contrat en mois", required=False, )
    valeur_estimee = fields.Float(string=u"Valeur estimée du bien à la date du contrat",  required=False, )
    duuree_theorique = fields.Integer(string=u"Durée théorique d'amortissement du bien", required=False, )
    cumul_redevance = fields.Float(string=u"Cumul des exercices précedents des redevances", required=False, )
    montant_redevance = fields.Float(string=u"Montant de l'exercice des redevances", required=False, )
    redevance_restant_moins = fields.Float(string=u"Redevances restant à payer A moins d'un an", required=False, )
    redevance_restant_plus = fields.Float(string=u"Redevances restant à payer A plus d'un an", required=False, )
    prix_achat_fin_contrat = fields.Float(string=u"Prix d'achat résiduel en fin de contrat",  required=False, )
    observations = fields.Text(string=u"Observations", required=False, )
    credit_bail_id = fields.Many2one(comodel_name="credit.bail", string="Credit bail", required=False, )