# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)

class CalculImpot(models.Model):
    _name = 'calcul.impot'
    _description = 'TABLEAU DE CALCUL DES IMPOTS'

    name = fields.Char(string=u"Nom",default="TABLEAU DE CALCUL DES IMPOTS",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    calcul_impot_line_ids = fields.One2many(comodel_name="calcul.impot.line", inverse_name="calcul_impot_id", string="Lignes", required=False, copy=True, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('calcul.impot'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    
    @api.model
    def create(self, values):
        return super(CalculImpot,self).create({
            'fy_n_id':self.fy_n_id.id,
            'calcul_impot_line_ids' : self.env['calcul.impot.line'].create([{'name':'1- CA taxable','type':'1','calcul_impot_id':self.id,},
                                                                        {'name':'2- CA exonéré à 100%','type':'2','calcul_impot_id':self.id,},
                                                                        {'name':'4- Autres produits taxables','type':'4','calcul_impot_id':self.id,},
                                                                        {'name':'- Autres produits d\'exploitation','type':'4','calcul_impot_id':self.id,},
                                                                        {'name':'- Produits financiers','type':'4','calcul_impot_id':self.id,},
                                                                        {'name':'- Subventions','type':'4','calcul_impot_id':self.id,},
                                                                        {'name':'5- Dénominateur','type':'5','calcul_impot_id':self.id,},
                                                                        {'name':'6- Montant de l\'impôt sur les sociétés (IS) dû','type':'6','calcul_impot_id':self.id,},
                                                                  ]),})    
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    def get_lines(self):
        pass
    def get_xml(self,parent):
        for rec in self:
            if rec.calcul_impot_line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(240) #Read documentation please
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                i = j = 0
                for line in rec.calcul_impot_line_ids:
                    if line.type == '1':
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14347)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                    if line.type == '2':
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14349)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                    
                    if line.type == '3':
                        i+=1
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14990)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.taux_reduit)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14353)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                        etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    if line.type == '4':
                        if line.name == '4- Autres produits taxables':
                            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                            cellule = etree.SubElement(valeur_cellule, "cellule")
                            etree.SubElement(cellule, "codeEdi").text = str(17929)
                            etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                        elif line.name == '- Autres produits d\'exploitation':
                            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                            cellule = etree.SubElement(valeur_cellule, "cellule")
                            etree.SubElement(cellule, "codeEdi").text = str(14992)
                            etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                        elif line.name == '- Subventions':
                            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                            cellule = etree.SubElement(valeur_cellule, "cellule")
                            etree.SubElement(cellule, "codeEdi").text = str(14996)
                            etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                        elif line.name == '- Produits financiers':
                            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                            cellule = etree.SubElement(valeur_cellule, "cellule")
                            etree.SubElement(cellule, "codeEdi").text = str(14994)
                            etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                        else:
                            j+=1
                            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                            cellule = etree.SubElement(valeur_cellule, "cellule")
                            etree.SubElement(cellule, "codeEdi").text = str(14355)
                            etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                            etree.SubElement(valeur_cellule, "numeroLigne").text = str(j)
                            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                            cellule = etree.SubElement(valeur_cellule, "cellule")
                            etree.SubElement(cellule, "codeEdi").text = str(14356)
                            etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                            etree.SubElement(valeur_cellule, "numeroLigne").text = str(j)
                    if line.type == '5':
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14380)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                    if line.type == '6':
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(14415)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                    
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
            else:
                pass
class CalculImpotLine(models.Model):
    _name = 'calcul.impot.line'
    _description = 'LIGNES TABLEAU DE CALCUL DES IMPOTS'
    _order = 'type asc,id asc'

    name = fields.Char(string=u"Rubrique",required=True,)
    type  = fields.Selection([('1', 'CA taxable')
                              ,('2', 'CA exonéré à 100%')
                              ,('3', 'CA soumis au taux reduit')
                              ,('4', 'Autres produits taxables')
                              ,('5', 'Dénominateur')
                              ,('6', 'impôt sur les sociétés')]
                             ,string='Type', required=True,)
    
    taux_reduit = fields.Float(string=u"Taux reduit")
    montant = fields.Float(string=u"Montant")
    # relational fields
    calcul_impot_id = fields.Many2one(comodel_name="calcul.impot", string="Impot", required=False, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('calcul.impot.line'))