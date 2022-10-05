# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)


class Provisions(models.Model):
    _name = 'provisions'
    _description = 'TABLEAU DES PROVISIONS'

    name = fields.Char(string=u"Nom",default="TABLEAU DES PROVISIONS",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    provisions_line_ids = fields.One2many(comodel_name="provisions.line", inverse_name="provisions_id", string="Lignes", required=False, copy=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('provisions'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(Provisions,self).create({
            'fy_n_id':self.fy_n_id.id,
            'provisions_line_ids' : self.env['provisions.line'].create([{'name':'1. Provisions pour dépréciation de l\'actif immobilisé','edi_montant_debut':1748,'edi_dotation_exploitation':1749,'edi_dotation_financiere':1750,'edi_dotation_non_courante':1751,'edi_reprises_exploitation':1752,'edi_reprises_financiere':1753,'edi_reprises_non_courante':1754,'edi_montant_fin':1755,'provisions_id':self.id,},
                                                                        {'name':'2. Provisions réglementées','edi_montant_debut':1784,'edi_dotation_exploitation':1785,'edi_dotation_financiere':1786,'edi_dotation_non_courante':1787,'edi_reprises_exploitation':1788,'edi_reprises_financiere':1789,'edi_reprises_non_courante':1790,'edi_montant_fin':1791,'provisions_id':self.id,},
                                                                        {'name':'3. Provisions durables pour risques et charges','edi_montant_debut':1827,'edi_dotation_exploitation':1828,'edi_dotation_financiere':1829,'edi_dotation_non_courante':1830,'edi_reprises_exploitation':1831,'edi_reprises_financiere':1832,'edi_reprises_non_courante':1833,'edi_montant_fin':1834,'provisions_id':self.id,},
                                                                        {'name':'SOUS TOTAL (A)','edi_montant_debut':1844,'edi_dotation_exploitation':1845,'edi_dotation_financiere':1846,'edi_dotation_non_courante':1847,'edi_reprises_exploitation':1848,'edi_reprises_financiere':1849,'edi_reprises_non_courante':1850,'edi_montant_fin':1851,'provisions_id':self.id,},
                                                                        {'name':'4. Provisions pour dépréciation de l\'actif circulant (hors trésorerie)','edi_montant_debut':1877,'edi_dotation_exploitation':1878,'edi_dotation_financiere':1879,'edi_dotation_non_courante':1880,'edi_reprises_exploitation':1881,'edi_reprises_financiere':1882,'edi_reprises_non_courante':1883,'edi_montant_fin':1884,'provisions_id':self.id,},
                                                                        {'name':'5. Autres Provisions pour risques et charge','edi_montant_debut':1894,'edi_dotation_exploitation':1895,'edi_dotation_financiere':1896,'edi_dotation_non_courante':1897,'edi_reprises_exploitation':1898,'edi_reprises_financiere':1899,'edi_reprises_non_courante':1900,'edi_montant_fin':1901,'provisions_id':self.id,},
                                                                        {'name':'6. Provisions pour dépréciation des comptes de trésorerie','edi_montant_debut':1903,'edi_dotation_exploitation':1904,'edi_dotation_financiere':1905,'edi_dotation_non_courante':1906,'edi_reprises_exploitation':1907,'edi_reprises_financiere':1908,'edi_reprises_non_courante':1909,'edi_montant_fin':1910,'provisions_id':self.id,},
                                                                        {'name':'SOUS TOTAL (B)','edi_montant_debut':1912,'edi_dotation_exploitation':1913,'edi_dotation_financiere':1914,'edi_dotation_non_courante':1915,'edi_reprises_exploitation':1916,'edi_reprises_financiere':1917,'edi_reprises_non_courante':1918,'edi_montant_fin':1919,'provisions_id':self.id,},
                                                                        {'name':'TOTAL (A+B)','edi_montant_debut':1921,'edi_dotation_exploitation':1922,'edi_dotation_financiere':1923,'edi_dotation_non_courante':1924,'edi_reprises_exploitation':1925,'edi_reprises_financiere':1926,'edi_reprises_non_courante':1927,'edi_montant_fin':1928,'provisions_id':self.id,},
                                                                  ]),})

    def from_string_to_list(self,val,list):
        list = []
        for x in str(val):
            list.append(x)
        return list
    
    def list_verification(self,list1,list2):
        if len(list1) == 2:
            if list1[0] == list2[0] and list1[1] == list2[1]:
                return True
        elif len(list1) == 3:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2]:
                return True
        elif len(list1) == 4:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] :
                return True
        elif len(list1) == 5:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] and list1[4] == list2[4]:
                return True
        else:
            return False

    def bal_calulator_previous_years(self,code):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for ref in rec.fy_n_id:
                        for item in entry.line_ids:
                            if ref.date_end.year > entry.date.year:
                                item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                col = rec.from_string_to_list(code,col)
                                if rec.list_verification(col,item_code):
                                    bal += abs(item.credit - item.debit)
            return bal
    
    def bal_calulator_current_year(self,code):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for ref in rec.fy_n_id:
                        for item in entry.line_ids:
                            if ref.date_end.year == entry.date.year:
                                item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                col = rec.from_string_to_list(code,col)
                                if rec.list_verification(col,item_code):
                                    bal += abs(item.debit - item.credit)
            return bal
                
    def get_lines(self):
        for rec in self:
            line_1 = self.env['provisions.line'].search([('name','=','1. Provisions pour dépréciation de l\'actif immobilisé'),('provisions_id','=',rec.id)])
            line_1.write({'montant_debut':rec.bal_calulator_previous_years('29'),
                          'dotation_exploitation':rec.bal_calulator_current_year('6194'),
                          'dotation_financiere': rec.bal_calulator_current_year('6392'),
                          'dotation_non_courante': rec.bal_calulator_current_year('6596'),
                          'reprises_exploitation': rec.bal_calulator_current_year('7194'),
                          'reprises_financiere': rec.bal_calulator_current_year('7392'),
                          'reprises_non_courante': rec.bal_calulator_current_year('7596'),
                          'montant_fin':rec.bal_calulator_previous_years('29')  + rec.bal_calulator_current_year('6194') + rec.bal_calulator_current_year('6392') + rec.bal_calulator_current_year('6596') - 1 * (rec.bal_calulator_current_year('7194') + rec.bal_calulator_current_year('7392') + rec.bal_calulator_current_year('7596'))})
            
            line_2 = self.env['provisions.line'].search([('name','=','2. Provisions réglementées'),('provisions_id','=',rec.id)])
            line_2.write({'montant_debut':rec.bal_calulator_previous_years('135'),
                          'dotation_exploitation':line_2.dotation_exploitation,
                          'dotation_financiere': line_2.dotation_financiere,
                          'dotation_non_courante': rec.bal_calulator_current_year('6594'),
                          'reprises_exploitation': line_2.reprises_exploitation,
                          'reprises_financiere': line_2.reprises_financiere,
                          'reprises_non_courante': rec.bal_calulator_current_year('7594'),
                          'montant_fin':rec.bal_calulator_previous_years('135') +line_2.dotation_exploitation +line_2.dotation_financiere + rec.bal_calulator_current_year('6594')  -1*(rec.bal_calulator_current_year('7594')+line_2.reprises_exploitation +line_2.reprises_financiere)})
            
            line_3 = self.env['provisions.line'].search([('name','=','3. Provisions durables pour risques et charges'),('provisions_id','=',rec.id)])
            line_3.write({'montant_debut':rec.bal_calulator_previous_years('15'),
                          'dotation_exploitation':rec.bal_calulator_current_year('6195'),
                          'dotation_financiere': rec.bal_calulator_current_year('6393'),
                          'dotation_non_courante': rec.bal_calulator_current_year('6595'),
                          'reprises_exploitation': rec.bal_calulator_current_year('7195'),
                          'reprises_financiere': rec.bal_calulator_current_year('7393'),
                          'reprises_non_courante': rec.bal_calulator_current_year('7595'),
                          'montant_fin':rec.bal_calulator_previous_years('15')  + rec.bal_calulator_current_year('6195') + rec.bal_calulator_current_year('6393') + rec.bal_calulator_current_year('6595') - 1 * (rec.bal_calulator_current_year('7195') + rec.bal_calulator_current_year('7393') + rec.bal_calulator_current_year('7595'))})

            line_4 = self.env['provisions.line'].search([('name','=','SOUS TOTAL (A)'),('provisions_id','=',rec.id)])
            line_4.write({'montant_debut':line_1.montant_debut + line_2.montant_debut + line_3.montant_debut,
                          'dotation_exploitation':line_1.dotation_exploitation +line_2.dotation_exploitation + line_3.dotation_exploitation,
                          'dotation_financiere': line_1.dotation_financiere +line_2.dotation_financiere + line_3.dotation_financiere,
                          'dotation_non_courante': line_1.dotation_non_courante +line_2.dotation_non_courante + line_3.dotation_non_courante,
                          'reprises_exploitation': line_1.reprises_exploitation +line_2.reprises_exploitation + line_3.reprises_exploitation,
                          'reprises_financiere': line_1.reprises_financiere +line_2.reprises_financiere + line_3.reprises_financiere,
                          'reprises_non_courante': line_1.reprises_non_courante +line_2.reprises_non_courante + line_3.reprises_non_courante,
                          'montant_fin':line_1.montant_fin +line_2.montant_fin + line_3.montant_fin})
            
            line_5 = self.env['provisions.line'].search([('name','=','4. Provisions pour dépréciation de l\'actif circulant (hors trésorerie)'),('provisions_id','=',rec.id)])
            line_5.write({'montant_debut':rec.bal_calulator_previous_years('39'),
                          'dotation_exploitation':rec.bal_calulator_current_year('6196'),
                          'dotation_financiere': rec.bal_calulator_current_year('6394'),
                          'dotation_non_courante': rec.bal_calulator_current_year('6596'),
                          'reprises_exploitation': rec.bal_calulator_current_year('7196'),
                          'reprises_financiere': rec.bal_calulator_current_year('7394'),
                          'reprises_non_courante': rec.bal_calulator_current_year('7596'),
                          'montant_fin':rec.bal_calulator_previous_years('39')  + rec.bal_calulator_current_year('6196') + rec.bal_calulator_current_year('6394') + rec.bal_calulator_current_year('6596') - 1 * (rec.bal_calulator_current_year('7196') + rec.bal_calulator_current_year('7394') + rec.bal_calulator_current_year('7596'))})
            
            line_6 = self.env['provisions.line'].search([('name','=','5. Autres Provisions pour risques et charge'),('provisions_id','=',rec.id)])
            line_6.write({'montant_debut':rec.bal_calulator_previous_years('45'),
                          'dotation_exploitation':rec.bal_calulator_previous_years('61957'),
                          'dotation_financiere': line_6.dotation_financiere,
                          'dotation_non_courante': rec.bal_calulator_previous_years('65957'),
                          'reprises_exploitation': line_6.reprises_exploitation,
                          'reprises_financiere': line_6.reprises_financiere,
                          'reprises_non_courante': rec.bal_calulator_previous_years('75957'),
                          'montant_fin':rec.bal_calulator_previous_years('45') + line_6.dotation_financiere -  line_6.reprises_exploitation - line_6.reprises_financiere + rec.bal_calulator_current_year('61957') + rec.bal_calulator_current_year('65957') - rec.bal_calulator_previous_years('75957')})
            
            line_7 = self.env['provisions.line'].search([('name','=','6. Provisions pour dépréciation des comptes de trésorerie'),('provisions_id','=',rec.id)])
            line_7.write({'montant_debut':rec.bal_calulator_previous_years('59'),
                          'dotation_exploitation':line_7.dotation_exploitation,
                          'dotation_financiere': rec.bal_calulator_previous_years('6396'),
                          'dotation_non_courante': line_7.dotation_non_courante,
                          'reprises_exploitation': line_7.reprises_exploitation,
                          'reprises_financiere': rec.bal_calulator_previous_years('7396'),
                          'reprises_non_courante': line_7.reprises_non_courante,
                          'montant_fin':rec.bal_calulator_previous_years('59') + line_7.dotation_exploitation + line_7.dotation_non_courante - line_7.reprises_exploitation - line_7.reprises_non_courante +  rec.bal_calulator_previous_years('6396') -rec.bal_calulator_previous_years('7396')})
            
            line_8 = self.env['provisions.line'].search([('name','=','SOUS TOTAL (B)'),('provisions_id','=',rec.id)])
            line_8.write({'montant_debut':line_5.montant_debut + line_6.montant_debut +line_7.montant_debut,
                          'dotation_exploitation':line_5.dotation_exploitation + line_6.dotation_exploitation +line_7.dotation_exploitation,
                          'dotation_financiere': line_5.dotation_financiere + line_6.dotation_financiere +line_7.dotation_financiere,
                          'dotation_non_courante': line_5.dotation_non_courante + line_6.dotation_non_courante +line_7.dotation_non_courante,
                          'reprises_exploitation': line_5.reprises_exploitation + line_6.reprises_exploitation +line_7.reprises_exploitation,
                          'reprises_financiere': line_5.reprises_financiere + line_6.reprises_financiere +line_7.reprises_financiere,
                          'reprises_non_courante': line_5.reprises_non_courante + line_6.reprises_non_courante +line_7.reprises_non_courante,
                          'montant_fin':line_5.montant_fin + line_6.montant_fin +line_7.montant_fin})
            
            line_9 = self.env['provisions.line'].search([('name','=','TOTAL (A+B)'),('provisions_id','=',rec.id)])
            line_9.write({'montant_debut':line_4.montant_debut + line_8.montant_debut,
                          'dotation_exploitation':line_4.dotation_exploitation + line_8.dotation_exploitation,
                          'dotation_financiere': line_4.dotation_financiere + line_8.dotation_financiere,
                          'dotation_non_courante': line_4.dotation_non_courante + line_8.dotation_non_courante,
                          'reprises_exploitation': line_4.reprises_exploitation + line_8.reprises_exploitation,
                          'reprises_financiere': line_4.reprises_financiere + line_8.reprises_financiere,
                          'reprises_non_courante': line_4.reprises_non_courante + line_8.reprises_non_courante,
                          'montant_fin':line_4.montant_fin + line_8.montant_fin})
    
    def get_xml(self,parent):
        for rec in self:
            if rec.provisions_line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(37) # read documentation XML
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                for line in rec.provisions_line_ids:
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_debut)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_debut)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_dotation_exploitation)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.dotation_exploitation)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_dotation_financiere)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.dotation_financiere)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_dotation_non_courante)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.dotation_non_courante)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_reprises_exploitation)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.reprises_exploitation)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_reprises_financiere)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.reprises_financiere)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_reprises_non_courante)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.reprises_non_courante)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_fin)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_fin)
                    
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(71)
                etree.SubElement(extra_field_valeur,"valeur").text = str(rec.fy_n_id.date_end)
                
                
            else:
                pass
            
class ProvisionsLine(models.Model):
    _name = 'provisions.line'
    _description = 'LIGNES TABLEAU DES PROVISIONS'

    code = fields.Char(string=u"Code",)
    name = fields.Char(string=u"Nature",required=True,readonly=True)
    montant_debut = fields.Float(string=u"Montant début exercice",  required=False,readonly=True )
    dotation_exploitation = fields.Float(string=u"Dotation d'exploitation",  required=False,readonly=True  )
    dotation_financiere = fields.Float(string=u"Dotation financières",  required=False, readonly=False )
    dotation_non_courante = fields.Float(string=u"Dotation Non courantes",  required=False, readonly=False )
    reprises_exploitation = fields.Float(string=u"Reprises d'exploitation",  required=False, readonly=False )
    reprises_financiere = fields.Float(string=u"Reprises financières",  required=False, readonly=False )
    reprises_non_courante = fields.Float(string=u"Reprises Non courantes",  required=False, readonly=False )
    montant_fin = fields.Float(string=u"Montant fin exercice",  required=False, readonly=True )
    
    # Code edi
    edi_montant_debut = fields.Integer(string=u"Montant début exercice",  required=False,readonly=True )
    edi_dotation_exploitation = fields.Integer(string=u"Dotation d'exploitation",  required=False,readonly=True  )
    edi_dotation_financiere = fields.Integer(string=u"Dotation financières",  required=False, readonly=False )
    edi_dotation_non_courante = fields.Integer(string=u"Dotation Non courantes",  required=False, readonly=False )
    edi_reprises_exploitation = fields.Integer(string=u"Reprises d'exploitation",  required=False, readonly=False )
    edi_reprises_financiere = fields.Integer(string=u"Reprises financières",  required=False, readonly=False )
    edi_reprises_non_courante = fields.Integer(string=u"Reprises Non courantes",  required=False, readonly=False )
    edi_montant_fin = fields.Integer(string=u"Montant fin exercice",  required=False, readonly=True )
    
    
    # Relational Fields
    provisions_id = fields.Many2one(comodel_name="provisions", string="Provisions", required=False, readonly=True  )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('provisions.line'))