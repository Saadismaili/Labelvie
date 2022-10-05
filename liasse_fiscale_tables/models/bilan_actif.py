# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)


class BilanActiv(models.Model):
    _name = "bilan.active"

    _description = 'TABLEAU de Bilan Active'

    name = fields.Char(string=u"Nom",default="Bilan Active",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='bilan.active.ligne',inverse_name='bilan_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('bilan.active'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(2)
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                for line in rec.line_ids:
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_gross)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.gross)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_amort)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.amort)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.net)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_prev_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.prev_net)
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
            else:
                pass

    
    @api.model
    def create(self, values):
        return super(BilanActiv,self).create({
            'line_ids' : self.env['bilan.active.ligne'].create([{'name':'IMMOBILISATIONS EN NON VALEURS (A)','code_edi_gross':497,'code_edi_amort':498,'code_edi_net':499,'code_edi_prev_net':500,'bilan_id':self.id,},
                                                                  {'name':'* Frais préliminaires','code_edi_gross':238,'code_edi_amort':241,'code_edi_net':244,'code_edi_prev_net':247,'bilan_id':self.id,},
                                                                  {'name':'* Charges à repartir sur plusieurs exercices','code_edi_gross':239,'code_edi_amort':242,'code_edi_net':245,'code_edi_prev_net':248,'bilan_id':self.id,},
                                                                  {'name':'* Primes de remboursement des obligations','code_edi_gross':240,'code_edi_amort':243,'code_edi_net':246,'code_edi_prev_net':249,'bilan_id':self.id,},
                                                                  {'name':'IMMOBILISATIONS INCORPORELLES (B)','code_edi_gross':502,'code_edi_amort':503,'code_edi_net':504,'code_edi_prev_net':505,'bilan_id':self.id,},
                                                                  {'name':'* Immobilisation en recherche et développement','code_edi_gross':274,'code_edi_amort':278,'code_edi_net':282,'code_edi_prev_net':286,'bilan_id':self.id,},
                                                                  {'name':'* Brevets, marques, droits et valeurs similaires','code_edi_gross':275,'code_edi_amort':279,'code_edi_net':283,'code_edi_prev_net':287,'bilan_id':self.id,},
                                                                  {'name':'* Fonds commercial','code_edi_gross':276,'code_edi_amort':280,'code_edi_net':284,'code_edi_prev_net':288,'bilan_id':self.id,},
                                                                  {'name':'* Autres immobilisations incorporelles','code_edi_gross':277,'code_edi_amort':281,'code_edi_net':285,'code_edi_prev_net':289,'bilan_id':self.id,},
                                                                  {'name':'IMMOBILISATIONS CORPORELLES (C)','code_edi_gross':507,'code_edi_amort':508,'code_edi_net':509,'code_edi_prev_net':510,'bilan_id':self.id,},
                                                                  {'name':'* Terrains','code_edi_gross':207,'code_edi_amort':214,'code_edi_net':221,'code_edi_prev_net':228,'bilan_id':self.id,},
                                                                  {'name':'* Constructions','code_edi_gross':208,'code_edi_amort':215,'code_edi_net':222,'code_edi_prev_net':229,'bilan_id':self.id,},
                                                                  {'name':'* Installations techniques, matériel et outillage','code_edi_gross':209,'code_edi_amort':216,'code_edi_net':223,'code_edi_prev_net':230,'bilan_id':self.id,},
                                                                  {'name':'* Matériel transport','code_edi_gross':210,'code_edi_amort':217,'code_edi_net':224,'code_edi_prev_net':231,'bilan_id':self.id,},
                                                                  {'name':'* Mobilier, matériel de bureau et aménagements div,','code_edi_gross':211,'code_edi_amort':218,'code_edi_net':225,'code_edi_prev_net':232,'bilan_id':self.id,},
                                                                  {'name':'* Autres immobilisations corporelles','code_edi_gross':212,'code_edi_amort':219,'code_edi_net':226,'code_edi_prev_net':233,'bilan_id':self.id,},
                                                                  {'name':'* Immobilisations corporelles en cours','code_edi_gross':213,'code_edi_amort':220,'code_edi_net':227,'code_edi_prev_net':234,'bilan_id':self.id,},
                                                                  {'name':'IMMOBILISATIONS FINANCIERES (D)','code_edi_gross':512,'code_edi_amort':513,'code_edi_net':514,'code_edi_prev_net':515,'bilan_id':self.id,},
                                                                  {'name':'* Prêts immobilisés','code_edi_gross':254,'code_edi_amort':258,'code_edi_net':262,'code_edi_prev_net':266,'bilan_id':self.id,},
                                                                  {'name':'* Autres créances financières','code_edi_gross':255,'code_edi_amort':259,'code_edi_net':263,'code_edi_prev_net':267,'bilan_id':self.id,},
                                                                  {'name':'* Titres de participation','code_edi_gross':256,'code_edi_amort':260,'code_edi_net':264,'code_edi_prev_net':268,'bilan_id':self.id,},
                                                                  {'name':'* Autres titres immobilisés','code_edi_gross':257,'code_edi_amort':261,'code_edi_net':265,'code_edi_prev_net':269,'bilan_id':self.id,},
                                                                  {'name':'ECARTS DE CONVERSION -ACTIF (E)','code_edi_gross':517,'code_edi_amort':518,'code_edi_net':519,'code_edi_prev_net':520,'bilan_id':self.id,},
                                                                  {'name':'* Diminution des créances immobilisées','code_edi_gross':192,'code_edi_amort':194,'code_edi_net':196,'code_edi_prev_net':198,'bilan_id':self.id,},
                                                                  {'name':'* Augmentation des dettes de financement','code_edi_gross':193,'code_edi_amort':195,'code_edi_net':197,'code_edi_prev_net':199,'bilan_id':self.id,},                                                                  
                                                                  {'name':'TOTAL I (A+B+C+D+E)','code_edi_gross':291,'code_edi_amort':292,'code_edi_net':293,'code_edi_prev_net':294,'bilan_id':self.id,},
                                                                  {'name':'STOCKS (F)','code_edi_gross':522,'code_edi_amort':523,'code_edi_net':524,'code_edi_prev_net':525,'bilan_id':self.id,},
                                                                  {'name':'* Marchandises','code_edi_gross':160,'code_edi_amort':165,'code_edi_net':170,'code_edi_prev_net':175,'bilan_id':self.id,},
                                                                  {'name':'* Matières et fournitures, consommables','code_edi_gross':161,'code_edi_amort':166,'code_edi_net':171,'code_edi_prev_net':176,'bilan_id':self.id,},
                                                                  {'name':'* Produits en cours','code_edi_gross':162,'code_edi_amort':167,'code_edi_net':172,'code_edi_prev_net':177,'bilan_id':self.id,},
                                                                  {'name':'* produits intermédiaires et produits résiduels','code_edi_gross':163,'code_edi_amort':168,'code_edi_net':173,'code_edi_prev_net':178,'bilan_id':self.id,},
                                                                  {'name':'* Produits finis','code_edi_gross':164,'code_edi_amort':169,'code_edi_net':174,'code_edi_prev_net':179,'bilan_id':self.id,},                                                                  
                                                                  {'name':'CREANCES DE L\'ACTIF CIRCULANT (G)','code_edi_gross':527,'code_edi_amort':528,'code_edi_net':529,'code_edi_prev_net':530,'bilan_id':self.id,},
                                                                  {'name':'* Fournis. débiteurs, avances et acomptes','code_edi_gross':122,'code_edi_amort':129,'code_edi_net':136,'code_edi_prev_net':143,'bilan_id':self.id,},
                                                                  {'name':'* Clients et comptes rattachés','code_edi_gross':123,'code_edi_amort':130,'code_edi_net':137,'code_edi_prev_net':144,'bilan_id':self.id,},
                                                                  {'name':'* Personnel','code_edi_gross':124,'code_edi_amort':131,'code_edi_net':138,'code_edi_prev_net':145,'bilan_id':self.id,},
                                                                  {'name':'* Etat','code_edi_gross':125,'code_edi_amort':132,'code_edi_net':139,'code_edi_prev_net':146,'bilan_id':self.id,},
                                                                  {'name':'* Comptes d\'associés','code_edi_gross':126,'code_edi_amort':133,'code_edi_net':140,'code_edi_prev_net':147,'bilan_id':self.id,},
                                                                  {'name':'* Autres débiteurs','code_edi_gross':127,'code_edi_amort':134,'code_edi_net':141,'code_edi_prev_net':148,'bilan_id':self.id,},
                                                                  {'name':'* Comptes de régularisation-Actif','code_edi_gross':128,'code_edi_amort':135,'code_edi_net':142,'code_edi_prev_net':149,'bilan_id':self.id,},
                                                                  {'name':'TITRES VALEURS DE PLACEMENT (H)','code_edi_gross':181,'code_edi_amort':182,'code_edi_net':183,'code_edi_prev_net':184,'bilan_id':self.id,},
                                                                  {'name':'ECARTS DE CONVERSION-ACTIF ( I )','code_edi_gross':151,'code_edi_amort':152,'code_edi_net':153,'code_edi_prev_net':154,'bilan_id':self.id,},                                                                  
                                                                  {'name':'TOTAL II ( F+G+H+I )','code_edi_gross':296,'code_edi_amort':297,'code_edi_net':298,'code_edi_prev_net':299,'bilan_id':self.id,},
                                                                  {'name':'TRESORERIE-ACTIF','code_edi_gross':532,'code_edi_amort':533,'code_edi_net':534,'code_edi_prev_net':535,'bilan_id':self.id,},
                                                                  {'name':'* Chèques et valeurs à encaisser','code_edi_gross':303,'code_edi_amort':306,'code_edi_net':309,'code_edi_prev_net':312,'bilan_id':self.id,},
                                                                  {'name':'* Banques, T.G et C.P','code_edi_gross':304,'code_edi_amort':307,'code_edi_net':310,'code_edi_prev_net':313,'bilan_id':self.id,},
                                                                  {'name':'* Caisses, Régies d\'avances et accréditifs','code_edi_gross':305,'code_edi_amort':308,'code_edi_net':311,'code_edi_prev_net':314,'bilan_id':self.id,},
                                                                  {'name':'TOTAL III','code_edi_gross':316,'code_edi_amort':317,'code_edi_net':318,'code_edi_prev_net':319,'bilan_id':self.id,},
                                                                  {'name':'TOTAL GENERAL (I+II+III)','code_edi_gross':186,'code_edi_amort':187,'code_edi_net':188,'code_edi_prev_net':189,'bilan_id':self.id,},
                                                                 ]),})
    # this function convert from string to list 
    def from_string_to_list(self,val,list):
        list = []
        for x in str(val):
            list.append(x)
        return list
    # this function verify if the code assigned to the line is the same assigned to account move line 
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
    # this function returns the previous year balance amount of each specific code assigned
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
                                    if str(item_code[0] +item_code[1]) == '51' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7119' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7129':
                                        bal += item.debit - item.credit
                                    elif item_code[0] == '2' and str(item_code[0] +item_code[1]) != '28' and str(item_code[0] +item_code[1]) != '29' :
                                        bal += item.debit - item.credit
                                    elif item_code[0] == '3' and str(item_code[0] +item_code[1]) != '39':
                                        bal += item.debit - item.credit
                                    elif item_code[0] == '6' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6119' and  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6129':
                                        bal += item.debit - item.credit
                                    elif item_code[0] == '1' or item_code[0] == '4' or str(item_code[0] +item_code[1]) == '55' or str(item_code[0] +item_code[1]) == '59':
                                        bal += item.credit - item.debit
                                    elif  item_code[0] == '7' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7119' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7129' :
                                        bal += item.credit - item.debit 
                                    elif   str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6119' or str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6129' or str(item_code[0] +item_code[1]) == '28' or str(item_code[0] +item_code[1]) == '29' or str(item_code[0] +item_code[1]) == '39' :
                                        bal += item.credit - item.debit 
            return bal
    # this function returns the current year balance amount of each specific code assigned
    def bal_calulator_current_year(self,code):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for ref in rec.fy_n_id:
                        for item in entry.line_ids:
                            if ref.date_end.year >= entry.date.year:
                                item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                col = rec.from_string_to_list(code,col)
                                if rec.list_verification(col,item_code):
                                    if str(item_code[0] +item_code[1]) == '51' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7119' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7129':
                                        bal += item.debit - item.credit
                                    elif item_code[0] == '2' and str(item_code[0] +item_code[1]) != '28' and str(item_code[0] +item_code[1]) != '29' :
                                        bal += item.debit - item.credit
                                    elif item_code[0] == '3' and str(item_code[0] +item_code[1]) != '39':
                                        bal += item.debit - item.credit
                                    elif item_code[0] == '6' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6119' and  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6129':
                                        bal += item.debit - item.credit
                                    elif item_code[0] == '1' or item_code[0] == '4' or str(item_code[0] +item_code[1]) == '55' or str(item_code[0] +item_code[1]) == '59':
                                        bal += item.credit - item.debit
                                    elif  item_code[0] == '7' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7119' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7129' :
                                        bal += item.credit - item.debit
                                    elif   str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6119' or str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6129' or str(item_code[0] +item_code[1]) == '28' or str(item_code[0] +item_code[1]) == '29' or str(item_code[0] +item_code[1]) == '39' :
                                        bal += item.credit - item.debit                                           
            return bal
    # this function modifies each line with its specific calculations 
    def get_lines(self):
        for rec in self:
            line_1 = self.env['bilan.active.ligne'].search([('name','=','* Frais préliminaires'),('bilan_id','=',rec.id)])
            line_1.write({'gross':self.bal_calulator_current_year('211'),
            'amort':self.bal_calulator_current_year('2811'),
            'net':self.bal_calulator_current_year('211') - self.bal_calulator_current_year('2811'),
            'prev_net':self.bal_calulator_previous_years('211') - self.bal_calulator_previous_years('2811'),
            })
            
            line_2 = self.env['bilan.active.ligne'].search([('name','=','* Charges à repartir sur plusieurs exercices'),('bilan_id','=',rec.id)])
            line_2.write({'gross':self.bal_calulator_current_year('212'),
            'amort':self.bal_calulator_current_year('2812'),
            'net':self.bal_calulator_current_year('212') - self.bal_calulator_current_year('2812'),
            'prev_net':self.bal_calulator_previous_years('212') - self.bal_calulator_previous_years('2812'),
            })
            line_3 = self.env['bilan.active.ligne'].search([('name','=','* Primes de remboursement des obligations'),('bilan_id','=',rec.id)])
            line_3.write({'gross':self.bal_calulator_current_year('213'),
            'amort':self.bal_calulator_current_year('2813'),
            'net':self.bal_calulator_current_year('213') - self.bal_calulator_current_year('2813'),
            'prev_net':self.bal_calulator_previous_years('213') - self.bal_calulator_previous_years('2813'),
            })
            line_4 = self.env['bilan.active.ligne'].search([('name','=','IMMOBILISATIONS EN NON VALEURS (A)'),('bilan_id','=',rec.id)])
            line_4.write({'gross':line_1.gross + line_3.gross + line_2.gross,
            'amort':line_1.amort + line_3.amort + line_2.amort,
            'net':line_1.net + line_3.net + line_2.net,
            'prev_net':line_1.prev_net + line_3.prev_net + line_2.prev_net,
            })

            line_5 = self.env['bilan.active.ligne'].search([('name','=','* Immobilisation en recherche et développement'),('bilan_id','=',rec.id)])
            line_5.write({'gross':self.bal_calulator_current_year('221'),
            'amort':self.bal_calulator_current_year('2821'),
            'net':self.bal_calulator_current_year('221') - self.bal_calulator_current_year('2821'),
            'prev_net':self.bal_calulator_previous_years('221') - self.bal_calulator_previous_years('2821'),
            })
            line_6 = self.env['bilan.active.ligne'].search([('name','=','* Brevets, marques, droits et valeurs similaires'),('bilan_id','=',rec.id)])
            line_6.write({'gross':self.bal_calulator_current_year('222'),
            'amort':self.bal_calulator_current_year('2822'),
            'net':self.bal_calulator_current_year('222') - self.bal_calulator_current_year('2822'),
            'prev_net':self.bal_calulator_previous_years('222') - self.bal_calulator_previous_years('2822'),
            })
            line_7 = self.env['bilan.active.ligne'].search([('name','=','* Fonds commercial'),('bilan_id','=',rec.id)])
            line_7.write({'gross':self.bal_calulator_current_year('223'),
            'amort':self.bal_calulator_current_year('2823'),
            'net':self.bal_calulator_current_year('223') - self.bal_calulator_current_year('2823'),
            'prev_net':self.bal_calulator_previous_years('223') - self.bal_calulator_previous_years('2823'),
            })
            line_8 = self.env['bilan.active.ligne'].search([('name','=','* Autres immobilisations incorporelles'),('bilan_id','=',rec.id)])
            line_8.write({'gross':self.bal_calulator_current_year('228'),
            'amort':self.bal_calulator_current_year('2828'),
            'net':self.bal_calulator_current_year('228') - self.bal_calulator_current_year('2828'),
            'prev_net':self.bal_calulator_previous_years('228') - self.bal_calulator_previous_years('2828'),
            })
            line_9 = self.env['bilan.active.ligne'].search([('name','=','IMMOBILISATIONS INCORPORELLES (B)'),('bilan_id','=',rec.id)])
            line_9.write({'gross':line_5.gross + line_6.gross + line_7.gross+ line_8.gross,
            'amort':line_5.amort + line_6.amort + line_7.amort + line_8.amort ,
            'net':line_5.net + line_6.net + line_7.net + line_8.net,
            'prev_net':line_5.prev_net + line_6.prev_net + line_7.prev_net + line_8.prev_net,
            })

            line_10 = self.env['bilan.active.ligne'].search([('name','=','* Terrains'),('bilan_id','=',rec.id)])
            line_10.write({'gross':self.bal_calulator_current_year('231'),
            'amort':self.bal_calulator_current_year('2831'),
            'net':self.bal_calulator_current_year('231') - self.bal_calulator_current_year('2831'),
            'prev_net':self.bal_calulator_previous_years('231') - self.bal_calulator_previous_years('2831'),
            })
            line_11 = self.env['bilan.active.ligne'].search([('name','=','* Constructions'),('bilan_id','=',rec.id)])
            line_11.write({'gross':self.bal_calulator_current_year('232'),
            'amort':self.bal_calulator_current_year('2832'),
            'net':self.bal_calulator_current_year('232') - self.bal_calulator_current_year('2832'),
            'prev_net':self.bal_calulator_previous_years('232') - self.bal_calulator_previous_years('2832'),
            })
            line_12 = self.env['bilan.active.ligne'].search([('name','=','* Installations techniques, matériel et outillage'),('bilan_id','=',rec.id)])
            line_12.write({'gross':self.bal_calulator_current_year('233'),
            'amort':self.bal_calulator_current_year('2833'),
            'net':self.bal_calulator_current_year('233') - self.bal_calulator_current_year('2833'),
            'prev_net':self.bal_calulator_previous_years('233') - self.bal_calulator_previous_years('2833'),
            })
            line_13 = self.env['bilan.active.ligne'].search([('name','=','* Matériel transport'),('bilan_id','=',rec.id)])
            line_13.write({'gross':self.bal_calulator_current_year('234'),
            'amort':self.bal_calulator_current_year('2834'),
            'net':self.bal_calulator_current_year('234') - self.bal_calulator_current_year('2834'),
            'prev_net':self.bal_calulator_previous_years('234') - self.bal_calulator_previous_years('2834'),
            })
            line_14 = self.env['bilan.active.ligne'].search([('name','=','* Mobilier, matériel de bureau et aménagements div,'),('bilan_id','=',rec.id)])
            line_14.write({'gross':self.bal_calulator_current_year('235'),
            'amort':self.bal_calulator_current_year('2835'),
            'net':self.bal_calulator_current_year('235') - self.bal_calulator_current_year('2835'),
            'prev_net':self.bal_calulator_previous_years('235') - self.bal_calulator_previous_years('2835'),
            })
            line_15 = self.env['bilan.active.ligne'].search([('name','=','* Autres immobilisations corporelles'),('bilan_id','=',rec.id)])
            line_15.write({'gross':self.bal_calulator_current_year('238'),
            'amort':self.bal_calulator_current_year('2838'),
            'net':self.bal_calulator_current_year('238') - self.bal_calulator_current_year('2838'),
            'prev_net':self.bal_calulator_previous_years('238') - self.bal_calulator_previous_years('2838'),
            })
            line_16 = self.env['bilan.active.ligne'].search([('name','=','* Immobilisations corporelles en cours'),('bilan_id','=',rec.id)])
            line_16.write({'gross':self.bal_calulator_current_year('239'),
            'net':self.bal_calulator_current_year('239'),
            'prev_net':self.bal_calulator_previous_years('239'),
            })
            line_17 = self.env['bilan.active.ligne'].search([('name','=','IMMOBILISATIONS CORPORELLES (C)'),('bilan_id','=',rec.id)])
            line_17.write({'gross':line_10.gross + line_11.gross + line_12.gross + line_13.gross + line_14.gross + line_15.gross + line_16.gross,
            'amort':line_10.amort + line_11.amort + line_12.amort + line_13.amort + line_14.amort + line_15.amort + line_16.amort,
            'net':line_10.net + line_11.net + line_12.net + line_13.net + line_14.net + line_15.net + line_16.net ,
            'prev_net':line_10.prev_net + line_11.prev_net + line_12.prev_net + line_13.prev_net + line_14.prev_net + line_15.prev_net + line_16.prev_net ,
            })
    # 
            line_18 = self.env['bilan.active.ligne'].search([('name','=','* Prêts immobilisés'),('bilan_id','=',rec.id)])
            line_18.write({'gross':self.bal_calulator_current_year('241'),
            'amort':self.bal_calulator_current_year('2941'),
            'net':self.bal_calulator_current_year('241') - self.bal_calulator_current_year('2941'),
            'prev_net':self.bal_calulator_previous_years('241') - self.bal_calulator_previous_years('2941'),
            })
            line_19 = self.env['bilan.active.ligne'].search([('name','=','* Autres créances financières'),('bilan_id','=',rec.id)])
            line_19.write({'gross':self.bal_calulator_current_year('248'),
            'amort':self.bal_calulator_current_year('2948'),
            'net': self.bal_calulator_current_year('248') - self.bal_calulator_current_year('2948'),
            'prev_net': self.bal_calulator_previous_years('248') - self.bal_calulator_previous_years('2948'),
            })
            line_20 = self.env['bilan.active.ligne'].search([('name','=','* Titres de participation'),('bilan_id','=',rec.id)])
            line_20.write({'gross':self.bal_calulator_current_year('251'),
            'amort':self.bal_calulator_current_year('2951'),
            'net':self.bal_calulator_current_year('251') - self.bal_calulator_current_year('2951'),
            'prev_net':self.bal_calulator_previous_years('251') - self.bal_calulator_previous_years('2951'),
            })
            line_21 = self.env['bilan.active.ligne'].search([('name','=','* Autres titres immobilisés'),('bilan_id','=',rec.id)])
            line_21.write({'gross':self.bal_calulator_current_year('258'),
            'amort':self.bal_calulator_current_year('2958'),
            'net':self.bal_calulator_current_year('258') -self.bal_calulator_current_year('2958'),
            'prev_net':self.bal_calulator_previous_years('258') -self.bal_calulator_previous_years('2958'),
            })
            line_22 = self.env['bilan.active.ligne'].search([('name','=','IMMOBILISATIONS FINANCIERES (D)'),('bilan_id','=',rec.id)])
            line_22.write({'gross':line_18.gross + line_19.gross + line_20.gross+ line_21.gross,
            'amort':line_18.amort + line_19.amort + line_20.amort + line_21.amort ,
            'net':line_18.net + line_19.net + line_20.net + line_21.net,
            'prev_net':line_18.prev_net + line_19.prev_net + line_20.prev_net + line_21.prev_net,
            })
# 
            line_23 = self.env['bilan.active.ligne'].search([('name','=','*  Titres de participation'),('bilan_id','=',rec.id)])
            line_23.write({'gross':self.bal_calulator_current_year('271'),
            'net':self.bal_calulator_current_year('271'),
            'prev_net':self.bal_calulator_previous_years('271'),
            })
            line_24 = self.env['bilan.active.ligne'].search([('name','=','*  Autres titres immobilisés'),('bilan_id','=',rec.id)])
            line_24.write({'gross':self.bal_calulator_current_year('272'),
            'net':self.bal_calulator_current_year('272'),
            'prev_net':self.bal_calulator_previous_years('272'),
            })
            line_25 = self.env['bilan.active.ligne'].search([('name','=','ECARTS DE CONVERSION -ACTIF (E)'),('bilan_id','=',rec.id)])
            line_25.write({'gross':line_24.gross+ line_23.gross,
            'amort':line_23.amort + line_24.amort ,
            'net': line_23.net + line_24.net,
            'prev_net': line_23.prev_net + line_24.prev_net,
            })

            line_26 = self.env['bilan.active.ligne'].search([('name','=','TOTAL I (A+B+C+D+E)'),('bilan_id','=',rec.id)])
            line_26.write({'gross':line_25.gross + line_22.gross + line_17.gross+ line_9.gross + line_4.gross,
            'amort':line_25.amort + line_9.amort + line_22.amort + line_17.amort + line_4.amort ,
            'net':line_25.net + line_22.net + line_17.net + line_9.net + + line_4.net,
            'prev_net':line_25.prev_net + line_22.prev_net + line_17.prev_net + line_9.prev_net + + line_4.prev_net,
            })

            line_27 = self.env['bilan.active.ligne'].search([('name','=','* Marchandises'),('bilan_id','=',rec.id)])
            line_27.write({'gross':self.bal_calulator_current_year('311'),
            'amort':self.bal_calulator_current_year('3911'),
            'net':self.bal_calulator_current_year('311') - self.bal_calulator_current_year('3911'),
            'prev_net':self.bal_calulator_previous_years('311') - self.bal_calulator_previous_years('3911'),
            })
            line_28 = self.env['bilan.active.ligne'].search([('name','=','* Matières et fournitures, consommables'),('bilan_id','=',rec.id)])
            line_28.write({'gross':self.bal_calulator_current_year('312'),
            'amort':self.bal_calulator_current_year('3912'),
            'net': self.bal_calulator_current_year('312') - self.bal_calulator_current_year('3912'),
            'prev_net': self.bal_calulator_previous_years('312') - self.bal_calulator_previous_years('3912'),
            })
            line_29 = self.env['bilan.active.ligne'].search([('name','=','* Produits en cours'),('bilan_id','=',rec.id)])
            line_29.write({'gross':self.bal_calulator_current_year('313'),
            'amort':self.bal_calulator_current_year('3913'),
            'net':self.bal_calulator_current_year('313') - self.bal_calulator_current_year('3913'),
            'prev_net':self.bal_calulator_previous_years('313') - self.bal_calulator_previous_years('3913'),
            })
            line_30 = self.env['bilan.active.ligne'].search([('name','=','* produits intermédiaires et produits résiduels'),('bilan_id','=',rec.id)])
            line_30.write({'gross':self.bal_calulator_current_year('314'),
            'amort':self.bal_calulator_current_year('3914'),
            'net':self.bal_calulator_current_year('314') -self.bal_calulator_current_year('3914'),
            'prev_net':self.bal_calulator_previous_years('314') -self.bal_calulator_previous_years('3914'),
            })
            line_31 = self.env['bilan.active.ligne'].search([('name','=','* Produits finis'),('bilan_id','=',rec.id)])
            line_31.write({'gross':self.bal_calulator_current_year('315'),
            'amort':self.bal_calulator_current_year('3915'),
            'net':self.bal_calulator_current_year('315') -self.bal_calulator_current_year('3915'),
            'prev_net':self.bal_calulator_previous_years('315') -self.bal_calulator_previous_years('3915'),
            })
            line_32 = self.env['bilan.active.ligne'].search([('name','=','STOCKS (F)'),('bilan_id','=',rec.id)])
            line_32.write({'gross':line_27.gross + line_28.gross + line_29.gross + line_30.gross+ line_31.gross,
            'amort':line_27.amort + line_28.amort + line_29.amort + line_30.amort  + line_31.amort,
            'net':line_27.net+ line_28.net + line_29.net + line_30.net + line_31.net,
            'prev_net':line_27.prev_net+ line_28.prev_net + line_29.prev_net + line_30.prev_net + line_31.prev_net,
            })

            line_34 = self.env['bilan.active.ligne'].search([('name','=','* Fournis. débiteurs, avances et acomptes'),('bilan_id','=',rec.id)])
            line_34.write({'gross':self.bal_calulator_current_year('341'),
            'amort':self.bal_calulator_current_year('3941'),
            'net':self.bal_calulator_current_year('341') - self.bal_calulator_current_year('3941'),
            'prev_net':self.bal_calulator_previous_years('341') - self.bal_calulator_previous_years('3941'),
            })
            line_35 = self.env['bilan.active.ligne'].search([('name','=','* Clients et comptes rattachés'),('bilan_id','=',rec.id)])
            line_35.write({'gross':self.bal_calulator_current_year('342'),
            'amort':self.bal_calulator_current_year('3942'),
            'net':self.bal_calulator_current_year('342') - self.bal_calulator_current_year('3942'),
            'prev_net':self.bal_calulator_previous_years('342') - self.bal_calulator_previous_years('3942'),
            })
            line_36 = self.env['bilan.active.ligne'].search([('name','=','* Personnel'),('bilan_id','=',rec.id)])
            line_36.write({'gross':self.bal_calulator_current_year('343'),
            'amort':self.bal_calulator_current_year('3943'),
            'net':self.bal_calulator_current_year('343') - self.bal_calulator_current_year('3943'),
            'prev_net':self.bal_calulator_previous_years('343') - self.bal_calulator_previous_years('3943'),
            })
            line_37 = self.env['bilan.active.ligne'].search([('name','=','* Etat'),('bilan_id','=',rec.id)])
            line_37.write({'gross':self.bal_calulator_current_year('345'),
            'net': self.bal_calulator_current_year('345') ,
            'prev_net': self.bal_calulator_previous_years('345') ,
            })
            line_38 = self.env['bilan.active.ligne'].search([('name','=','* Comptes d\'associés'),('bilan_id','=',rec.id)])
            line_38.write({'gross':self.bal_calulator_current_year('346'),
            'amort':self.bal_calulator_current_year('3946'),
            'net':self.bal_calulator_current_year('346') - self.bal_calulator_current_year('3946'),
            'prev_net':self.bal_calulator_previous_years('346') - self.bal_calulator_previous_years('3946'),
            })
            line_39 = self.env['bilan.active.ligne'].search([('name','=','* Autres débiteurs'),('bilan_id','=',rec.id)])
            line_39.write({'gross':self.bal_calulator_current_year('348'),
            'amort':self.bal_calulator_current_year('3948'),
            'net':self.bal_calulator_current_year('348') -self.bal_calulator_current_year('3948'),
            'prev_net':self.bal_calulator_previous_years('348') -self.bal_calulator_previous_years('3948'),
            })
            line_40 = self.env['bilan.active.ligne'].search([('name','=','* Comptes de régularisation-Actif'),('bilan_id','=',rec.id)])
            line_40.write({'gross':self.bal_calulator_current_year('349'),
            'net':self.bal_calulator_current_year('349'),
            'prev_net':self.bal_calulator_previous_years('349'),
            })
            line_41 = self.env['bilan.active.ligne'].search([('name','=','CREANCES DE L\'ACTIF CIRCULANT (G)'),('bilan_id','=',rec.id)])
            line_41.write({'gross':line_40.gross + line_34.gross + line_35.gross + line_36.gross  + line_37.gross +line_38.gross  + line_39.gross,
            'amort':line_40.amort + line_34.amort + line_35.amort + line_36.amort  + line_37.amort +line_38.amort  + line_39.amort,
            'net':line_40.net + line_34.net + line_35.net + line_36.net  + line_37.net +line_38.net  + line_39.net,
            'prev_net':line_40.prev_net + line_34.prev_net + line_35.prev_net + line_36.prev_net  + line_37.prev_net +line_38.prev_net  + line_39.prev_net,
            })

            line_42 = self.env['bilan.active.ligne'].search([('name','=','TITRES VALEURS DE PLACEMENT (H)'),('bilan_id','=',rec.id)])
            line_42.write({'gross':self.bal_calulator_current_year('35'),
            'amort':self.bal_calulator_current_year('395'),
            'net':self.bal_calulator_current_year('35') - self.bal_calulator_current_year('395'),
            'prev_net':self.bal_calulator_previous_years('35') - self.bal_calulator_previous_years('395'),
            })

            line_43 = self.env['bilan.active.ligne'].search([('name','=','ECARTS DE CONVERSION-ACTIF ( I )'),('bilan_id','=',rec.id)])
            line_43.write({'gross':self.bal_calulator_current_year('37'),
            'amort':self.bal_calulator_current_year('397'),
            'net':self.bal_calulator_current_year('37') - self.bal_calulator_current_year('397'),
            'prev_net':self.bal_calulator_previous_years('37') - self.bal_calulator_previous_years('397'),
            })

            line_44 = self.env['bilan.active.ligne'].search([('name','=','TOTAL II ( F+G+H+I )'),('bilan_id','=',rec.id)])
            line_44.write({'gross':line_43.gross + line_42.gross + line_41.gross + line_32.gross,
            'amort': line_43.amort + line_42.amort + line_41.amort  + line_32.amort,
            'net': line_43.net + line_42.net + line_41.net  + line_32.net,
            'prev_net': line_43.prev_net + line_42.prev_net + line_41.prev_net  + line_32.prev_net,
            })

            line_45 = self.env['bilan.active.ligne'].search([('name','=','* Chèques et valeurs à encaisser'),('bilan_id','=',rec.id)])
            line_45.write({'gross':self.bal_calulator_current_year('511'),
            'amort':0,
            'net':self.bal_calulator_current_year('511') ,
            'prev_net':self.bal_calulator_previous_years('511') ,
            })
            line_46 = self.env['bilan.active.ligne'].search([('name','=','* Banques, T.G et C.P'),('bilan_id','=',rec.id)])
            line_46.write({'gross':self.bal_calulator_current_year('514'),
            'amort': self.bal_calulator_current_year('590') ,
            'net': self.bal_calulator_current_year('514')  - self.bal_calulator_current_year('590') ,
            'prev_net': self.bal_calulator_previous_years('514') - self.bal_calulator_previous_years('590') ,
            })
            line_47 = self.env['bilan.active.ligne'].search([('name','=','* Caisses, Régies d\'avances et accréditifs'),('bilan_id','=',rec.id)])
            line_47.write({'gross':self.bal_calulator_current_year('516'),
            'amort':0,
            'net':self.bal_calulator_current_year('516') ,
            'prev_net':self.bal_calulator_previous_years('516') ,
            })
            line_50 = self.env['bilan.active.ligne'].search([('name','=','TRESORERIE-ACTIF'),('bilan_id','=',rec.id)])
            line_50.write({'gross':line_45.gross + line_46.gross + line_47.gross,
            'amort':line_45.amort  + line_46.amort +line_47.amort  ,
            'net':line_45.net  + line_46.net + line_47.net,
            'prev_net':line_45.prev_net  + line_46.prev_net + line_47.prev_net,
            })

            line_51 = self.env['bilan.active.ligne'].search([('name','=','TOTAL III'),('bilan_id','=',rec.id)])
            line_51.write({'gross':line_50.gross,
            'amort':line_50.amort ,
            'net':line_50.net ,
            'prev_net':line_50.prev_net ,
            })

            line_52 = self.env['bilan.active.ligne'].search([('name','=','TOTAL GENERAL (I+II+III)'),('bilan_id','=',rec.id)])
            line_52.write({'gross':line_50.gross + line_26.gross + line_44.gross ,
            'amort':line_50.amort + line_26.amort + line_44.amort,
            'net':line_50.net + line_26.net + line_44.net,
            'prev_net':line_50.prev_net + line_26.prev_net + line_44.prev_net,
            })


class BilanActivLignes(models.Model):
    _name = "bilan.active.ligne" 

    name = fields.Char(string=u"Nom",required=True,readonly=True)
    gross  = fields.Float(string=u"Brut",readonly=True)
    amort  = fields.Float(string=u"Amortissements et Provisions",readonly=True)
    net  = fields.Float(string=u"Net",readonly=True)
    prev_net  = fields.Float(string=u"Net d'exercice précédent",readonly=True)
    
    # Code edis
    code_edi_gross  = fields.Integer(string=u"Brut Edi",readonly=True)
    code_edi_amort  = fields.Integer(string=u"Amortissement Edi",readonly=True)
    code_edi_net  = fields.Integer(string=u"Net Edi",readonly=True)
    code_edi_prev_net  = fields.Integer(string=u"Prev Net Edi",readonly=True)

    # Relational fields
    bilan_id = fields.Many2one(string='bilan id', comodel_name='bilan.active')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('bilan.active.ligne'))



