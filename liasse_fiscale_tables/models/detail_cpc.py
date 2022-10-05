# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)

class DetailCPC(models.Model):
    _name = "detail.cpc"

    _description = 'TABLEAU de Detail CPC'

    name = fields.Char(string=u"Nom",default="Detail CPC",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='detail.cpc.ligne',inverse_name='parent_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('detail.cpc'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(DetailCPC,self).create({
            'line_ids' : self.env['detail.cpc.ligne'].create([{'name':'611 - Achats revendus de marchandises','code_edi_net': 1521,'code_edi_prev_net':1562 ,'parent_id':self.id,},
                                                                  {'name':'* Achats de marchandises','code_edi_net': 1522,'code_edi_prev_net':1563 ,'parent_id':self.id,},
                                                                  {'name':'Variation des stocks de marchandises (±)','code_edi_net': 1523,'code_edi_prev_net':1564 ,'parent_id':self.id,},
                                                                  {'name':'Total-611','code_edi_net': 1524,'code_edi_prev_net':1565 ,'parent_id':self.id,},
                                                                  {'name':'612 - Achats consommés de matières et fournitures','code_edi_net': 1525,'code_edi_prev_net':1566 ,'parent_id':self.id,},
                                                                  {'name':'* Achat de matières premières','code_edi_net': 1526,'code_edi_prev_net':1567 ,'parent_id':self.id,},
                                                                  {'name':'*Variation des stocks de matières premières (+-)','code_edi_net': 1527,'code_edi_prev_net':1568 ,'parent_id':self.id,},
                                                                  {'name':'* Achats de matières et fournitures consommables et d\'emballages','code_edi_net': 1528,'code_edi_prev_net':1569 ,'parent_id':self.id,},
                                                                  {'name':'Variation des stocks de matières, fournitures et emballages (+/-)','code_edi_net': 1529,'code_edi_prev_net':1570 ,'parent_id':self.id,},
                                                                  {'name':'* Achats non stockés de matières et de fournitures','code_edi_net': 1530,'code_edi_prev_net':1571 ,'parent_id':self.id,},
                                                                  {'name':'* Achats de travaux, études et prestations de services','code_edi_net': 1531,'code_edi_prev_net':1572 ,'parent_id':self.id,},
                                                                  {'name':'Total-612','code_edi_net': 1532,'code_edi_prev_net':1573 ,'parent_id':self.id,},
                                                                  {'name':'613/614 - *Autres charges externes','code_edi_net': 1533,'code_edi_prev_net':1574,'parent_id':self.id,},
                                                                  {'name':'* Locations et charges locatives','code_edi_net': 1534,'code_edi_prev_net':1575,'parent_id':self.id,},
                                                                  {'name':'* Redevances de crédit-bail','code_edi_net': 1535,'code_edi_prev_net':1576,'parent_id':self.id,},
                                                                  {'name':'* Entretien et réparations','code_edi_net': 1536,'code_edi_prev_net':1577,'parent_id':self.id,},
                                                                  {'name':'* Primes d\'assurances','code_edi_net': 1537,'code_edi_prev_net':1578,'parent_id':self.id,},
                                                                  {'name':'* Rémunérations du personnel extérieur à l\'entreprise','code_edi_net': 1538,'code_edi_prev_net':1579,'parent_id':self.id,},
                                                                  {'name':'* Rémunérations d\'intermédiaires et honoraires','code_edi_net': 1539,'code_edi_prev_net':10091,'parent_id':self.id,},
                                                                  {'name':'* Redevances pour brevets, marques, droits.......','code_edi_net': 1540,'code_edi_prev_net':10420,'parent_id':self.id,},
                                                                  {'name':'*Transports','code_edi_net': 1541,'code_edi_prev_net':1582,'parent_id':self.id,},
                                                                  {'name':'* Déplacements, missions et réceptions','code_edi_net': 1542,'code_edi_prev_net':1583,'parent_id':self.id,},
                                                                  {'name':'* Reste du poste des autres charges externes','code_edi_net': 1543,'code_edi_prev_net':1584,'parent_id':self.id,},
                                                                  {'name':'Total-613/614','code_edi_net': 1544,'code_edi_prev_net':1585,'parent_id':self.id,},
                                                                  {'name':'617 - * Charges de personnel','code_edi_net': 1545,'code_edi_prev_net':1586,'parent_id':self.id,},
                                                                  {'name':'* Rémunération du personnel','code_edi_net': 1546,'code_edi_prev_net':1587,'parent_id':self.id,},
                                                                  {'name':'* Charges sociales','code_edi_net': 1547,'code_edi_prev_net':1588,'parent_id':self.id,},
                                                                  {'name':'* Reste du poste des charges de personnel','code_edi_net': 1548,'code_edi_prev_net':1589,'parent_id':self.id,},
                                                                  {'name':'Total-617','code_edi_net': 1549,'code_edi_prev_net':1590,'parent_id':self.id,},
                                                                  {'name':'618 - Autres charges d\'exploitation','code_edi_net': 1550,'code_edi_prev_net':1591,'parent_id':self.id,},
                                                                  {'name':'* Jetons de présence','code_edi_net': 1551,'code_edi_prev_net':1592,'parent_id':self.id,},
                                                                  {'name':'* Pertes sur créances irrécouvrables','code_edi_net': 1552,'code_edi_prev_net':1593,'parent_id':self.id,},
                                                                  {'name':'* Reste du poste des autres charges d\'exploitation','code_edi_net': 1553,'code_edi_prev_net':1594,'parent_id':self.id,},
                                                                  {'name':'Total-618','code_edi_net': 1733,'code_edi_prev_net':1734,'parent_id':self.id,},
                                                                  {'name':'638 *Autres charges financières','code_edi_net': 1764,'code_edi_prev_net':1814,'parent_id':self.id,},
                                                                  {'name':'* Charges nettes sur cessions de titres et valeurs de placement','code_edi_net': 1765,'code_edi_prev_net':1815,'parent_id':self.id,},
                                                                  {'name':'* Reste du poste des autres charges financières','code_edi_net': 1766,'code_edi_prev_net':1816,'parent_id':self.id,},
                                                                  {'name':'Total-638','code_edi_net': 1767,'code_edi_prev_net':1817,'parent_id':self.id,},
                                                                  {'name':'658 - Autres charges non courantes','code_edi_net': 1792,'code_edi_prev_net':1807,'parent_id':self.id,},
                                                                  {'name':'* Pénalités sur marchés et dédits','code_edi_net': 1793,'code_edi_prev_net':1808,'parent_id':self.id,},
                                                                  {'name':'* Rappels d\'impôts (autres qu\'impôts sur les résultats)','code_edi_net': 1794,'code_edi_prev_net':1809,'parent_id':self.id,},
                                                                  {'name':'* Pénalités et amendes fiscales et pénales','code_edi_net': 1795,'code_edi_prev_net':1810,'parent_id':self.id,},
                                                                  {'name':'* Créances devenues irrécouvrables','code_edi_net': 1796,'code_edi_prev_net':1811,'parent_id':self.id,},
                                                                  {'name':'* Reste du poste des autres charges non courantes','code_edi_net': 1797,'code_edi_prev_net':1812,'parent_id':self.id,},
                                                                  {'name':'Total-658','code_edi_net': 1798,'code_edi_prev_net':1813,'parent_id':self.id,},
                                                                  {'name':'711 * Ventes de marchandises','code_edi_net': 1963,'code_edi_prev_net':1989,'parent_id':self.id,},
                                                                  {'name':'* Ventes de marchandises au Maroc','code_edi_net': 1964,'code_edi_prev_net':1990,'parent_id':self.id,},
                                                                  {'name':'* Ventes de marchandises à l\'étranger','code_edi_net': 1965,'code_edi_prev_net':1991,'parent_id':self.id,},
                                                                  {'name':'* Reste du poste des ventes de marchandises','code_edi_net': 1966,'code_edi_prev_net':1992,'parent_id':self.id,},
                                                                  {'name':'Total-711','code_edi_net': 1967,'code_edi_prev_net':1993,'parent_id':self.id,},
                                                                  {'name':'712 * Ventes de biens et services produits','code_edi_net': 1968,'code_edi_prev_net':1994,'parent_id':self.id,},
                                                                  {'name':'*Ventes de biens au Maroc','code_edi_net': 1969,'code_edi_prev_net':1995,'parent_id':self.id,},
                                                                  {'name':'*Ventes de biens à l\'étranger','code_edi_net': 1970,'code_edi_prev_net':1996,'parent_id':self.id,},
                                                                  {'name':'*Ventes de services au Maroc','code_edi_net': 1971,'code_edi_prev_net':1997,'parent_id':self.id,},
                                                                  {'name':'*Ventes de services à l\'étranger','code_edi_net': 1972,'code_edi_prev_net':1998,'parent_id':self.id,},
                                                                  {'name':'* Redevances pour brevets, marques, droits..','code_edi_net': 1973,'code_edi_prev_net':1999,'parent_id':self.id,},
                                                                  {'name':'* Reste du poste des ventes et services produits','code_edi_net': 1974,'code_edi_prev_net':2000,'parent_id':self.id,},
                                                                  {'name':'Total-712','code_edi_net': 1975,'code_edi_prev_net':2001,'parent_id':self.id,},
                                                                  {'name':'713 *Variation des stocks de produits','code_edi_net': 1976,'code_edi_prev_net':2002,'parent_id':self.id,},
                                                                  {'name':'* Variation des stocks des biens produits (+/-)','code_edi_net': 1977,'code_edi_prev_net':2003,'parent_id':self.id,},
                                                                  {'name':'*Variation des stocks des services produits (+/-)','code_edi_net': 1978,'code_edi_prev_net':2004,'parent_id':self.id,},
                                                                  {'name':'*Variation des stocks des produits en cours (+/-)','code_edi_net': 1979,'code_edi_prev_net':2005,'parent_id':self.id,},
                                                                  {'name':'Total-713','code_edi_net': 1980,'code_edi_prev_net':2006,'parent_id':self.id,},
                                                                  {'name':'718 * Autres produits d\'exploitation','code_edi_net': 1981,'code_edi_prev_net':2007,'parent_id':self.id,},
                                                                  {'name':'* Jetons de présence reçus','code_edi_net': 1982,'code_edi_prev_net':2008,'parent_id':self.id,},
                                                                  {'name':'* Reste du poste (produits divers)','code_edi_net': 1983,'code_edi_prev_net':2009,'parent_id':self.id,},
                                                                  {'name':'Total-718','code_edi_net': 1984,'code_edi_prev_net':2010,'parent_id':self.id,},
                                                                  {'name':'719 Reprises d\'exploitation, transferts de charges','code_edi_net': 1985,'code_edi_prev_net':2011,'parent_id':self.id,},
                                                                  {'name':'* Reprises','code_edi_net': 1986,'code_edi_prev_net':2012,'parent_id':self.id,},
                                                                  {'name':'*Transferts de charges','code_edi_net': 1987,'code_edi_prev_net':2013,'parent_id':self.id,},
                                                                  {'name':'Total-719','code_edi_net': 1988,'code_edi_prev_net':2014,'parent_id':self.id,},
                                                                  {'name':'738 * Intérêts et autres produits financiers','code_edi_net': 2022,'code_edi_prev_net':2029,'parent_id':self.id,},
                                                                  {'name':'* Intérêts et produits assimilés','code_edi_net': 2024,'code_edi_prev_net':2031,'parent_id':self.id,},
                                                                  {'name':'* Revenus des créances rattachées à des participations','code_edi_net': 2025,'code_edi_prev_net':2032,'parent_id':self.id,},
                                                                  {'name':'* Produits nets sur cessions de titres et valeurs de placement','code_edi_net': 2026,'code_edi_prev_net':2033,'parent_id':self.id,},
                                                                  {'name':'* Reste du poste intérêts et autres produits financiers','code_edi_net': 2027,'code_edi_prev_net':2034,'parent_id':self.id,},
                                                                  {'name':'Total-738','code_edi_net': 2028,'code_edi_prev_net':2035,'parent_id':self.id,},
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
    
    def bal_calulator_current_year(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for code in codes:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if ref.date_end.year == entry.date.year:
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

    def bal_calulator_previous_years(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for code in codes:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if ref.date_end.year -1 == entry.date.year:
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

    def get_lines(self):
        for rec in self:
            line_1 = self.env['detail.cpc.ligne'].search([('name','=','* Achats de marchandises'),('parent_id','=',rec.id)])
            line_1.write({
            'net':self.bal_calulator_current_year(['6111','6112']) ,
            'prev_net':self.bal_calulator_previous_years(['6111','6112']),
            })
            line_2 = self.env['detail.cpc.ligne'].search([('name','=','Variation des stocks de marchandises (±)'),('parent_id','=',rec.id)])
            line_2.write({
            'net':self.bal_calulator_current_year(['6114']),
            'prev_net':self.bal_calulator_previous_years(['6114']),
            })
            line_3 = self.env['detail.cpc.ligne'].search([('name','=','Total-611'),('parent_id','=',rec.id)])
            line_3.write({
            'net':self.bal_calulator_current_year(['611']),
            'prev_net':self.bal_calulator_previous_years(['611']),
            })
            line_4 = self.env['detail.cpc.ligne'].search([('name','=','* Achat de matières premières'),('parent_id','=',rec.id)])
            line_4.write({
            'net':self.bal_calulator_current_year(['6121']),
            'prev_net':self.bal_calulator_previous_years(['6121']),
            })
            line_5 = self.env['detail.cpc.ligne'].search([('name','=','*Variation des stocks de matières premières (+-)'),('parent_id','=',rec.id)])
            line_5.write({
            'net':self.bal_calulator_current_year(['61241']) ,
            'prev_net':self.bal_calulator_previous_years(['61241']),
            })
            line_6 = self.env['detail.cpc.ligne'].search([('name','=','* Achats de matières et fournitures consommables et d\'emballages'),('parent_id','=',rec.id)])
            line_6.write({
            'net':self.bal_calulator_current_year(['6122','6123','6128']),
            'prev_net':self.bal_calulator_previous_years(['6123','6123','6128']),
            })
            line_7 = self.env['detail.cpc.ligne'].search([('name','=','Variation des stocks de matières, fournitures et emballages (+/-)'),('parent_id','=',rec.id)])
            line_7.write({
            'net':self.bal_calulator_current_year(['61242','61243']),
            'prev_net':self.bal_calulator_previous_years(['61242','61243']),
            })
            line_8 = self.env['detail.cpc.ligne'].search([('name','=','* Achats non stockés de matières et de fournitures'),('parent_id','=',rec.id)])
            line_8.write({
            'net':self.bal_calulator_current_year(['6125']),
            'prev_net':self.bal_calulator_previous_years(['6125']),
            })
            line_9 = self.env['detail.cpc.ligne'].search([('name','=','* Achats de travaux, études et prestations de services'),('parent_id','=',rec.id)])
            line_9.write({
            'net':self.bal_calulator_current_year(['6126']),
            'prev_net':self.bal_calulator_previous_years(['6126']),
            })
            line_10 = self.env['detail.cpc.ligne'].search([('name','=','Total-612'),('parent_id','=',rec.id)])
            line_10.write({
            'net':self.bal_calulator_current_year(['612']),
            'prev_net':self.bal_calulator_previous_years(['612']),
            })
            line_11 = self.env['detail.cpc.ligne'].search([('name','=','* Locations et charges locatives'),('parent_id','=',rec.id)])
            line_11.write({
            'net':self.bal_calulator_current_year(['6131']),
            'prev_net':self.bal_calulator_previous_years(['6131']),
            })
            line_12 = self.env['detail.cpc.ligne'].search([('name','=','* Redevances de crédit-bail'),('parent_id','=',rec.id)])
            line_12.write({
            'net':self.bal_calulator_current_year(['6132']),
            'prev_net':self.bal_calulator_previous_years(['6132']),
            })

            line_13 = self.env['detail.cpc.ligne'].search([('name','=','* Entretien et réparations'),('parent_id','=',rec.id)])
            line_13.write({
            'net':self.bal_calulator_current_year(['6133']),
            'prev_net':self.bal_calulator_previous_years(['6133']),
            })

            line_14 = self.env['detail.cpc.ligne'].search([('name','=','* Primes d\'assurances'),('parent_id','=',rec.id)])
            line_14.write({
            'net':self.bal_calulator_current_year(['6134']),
            'prev_net':self.bal_calulator_previous_years(['6134']),
            })
            line_15 = self.env['detail.cpc.ligne'].search([('name','=','* Rémunérations du personnel extérieur à l\'entreprise'),('parent_id','=',rec.id)])
            line_15.write({
            'net':self.bal_calulator_current_year(['6135']) ,
            'prev_net':self.bal_calulator_previous_years(['6135']),
            })
            line_16 = self.env['detail.cpc.ligne'].search([('name','=','* Rémunérations d\'intermédiaires et honoraires'),('parent_id','=',rec.id)])
            line_16.write({
            'net':self.bal_calulator_current_year(['6136']) ,
            'prev_net':self.bal_calulator_previous_years(['6136']),
            })


            line_17 = self.env['detail.cpc.ligne'].search([('name','=','* Redevances pour brevets, marques, droits.......'),('parent_id','=',rec.id)])
            line_17.write({
            'net':self.bal_calulator_current_year(['6137']) ,
            'prev_net':self.bal_calulator_previous_years(['6137']),
            })
            line_18 = self.env['detail.cpc.ligne'].search([('name','=','*Transports'),('parent_id','=',rec.id)])
            line_18.write({
            'net':self.bal_calulator_current_year(['6142']) ,
            'prev_net':self.bal_calulator_previous_years(['6142']),
            })
            line_19 = self.env['detail.cpc.ligne'].search([('name','=','* Déplacements, missions et réceptions'),('parent_id','=',rec.id)])
            line_19.write({
            'net':self.bal_calulator_current_year(['6143']) ,
            'prev_net':self.bal_calulator_previous_years(['6143']),
            })

            line_20 = self.env['detail.cpc.ligne'].search([('name','=','* Reste du poste des autres charges externes'),('parent_id','=',rec.id)])
            line_20.write({
            'net':self.bal_calulator_current_year(['6144','6145','6146','6147','6148','6149']) ,
            'prev_net':self.bal_calulator_previous_years(['6144','6145','6146','6147','6148','6149']),
            })


            line_21 = self.env['detail.cpc.ligne'].search([('name','=','Total-613/614'),('parent_id','=',rec.id)])
            line_21.write({
            'net':self.bal_calulator_current_year(['614','613']) ,
            'prev_net':self.bal_calulator_previous_years(['614','613']),
            })
            line_22 = self.env['detail.cpc.ligne'].search([('name','=','* Rémunération du personnel'),('parent_id','=',rec.id)])
            line_22.write({
            'net':self.bal_calulator_current_year(['6171']) ,
            'prev_net':self.bal_calulator_previous_years(['6171']),
            })

            line_23 = self.env['detail.cpc.ligne'].search([('name','=','* Charges sociales'),('parent_id','=',rec.id)])
            line_23.write({
            'net':self.bal_calulator_current_year(['6174']) ,
            'prev_net':self.bal_calulator_previous_years(['6174']),
            })
            line_24 = self.env['detail.cpc.ligne'].search([('name','=','* Reste du poste des charges de personnel'),('parent_id','=',rec.id)])
            line_24.write({
            'net':self.bal_calulator_current_year(['6176','6177','6178']) ,
            'prev_net':self.bal_calulator_previous_years(['6176','6177','6178']),
            })
            line_25 = self.env['detail.cpc.ligne'].search([('name','=','Total-617'),('parent_id','=',rec.id)])
            line_25.write({
            'net':self.bal_calulator_current_year(['617']) ,
            'prev_net':self.bal_calulator_previous_years(['617']),
            })

            line_26 = self.env['detail.cpc.ligne'].search([('name','=','* Jetons de présence'),('parent_id','=',rec.id)])
            line_26.write({
            'net':self.bal_calulator_current_year(['6181']) ,
            'prev_net':self.bal_calulator_previous_years(['6181']),
            })

            line_27 = self.env['detail.cpc.ligne'].search([('name','=','* Pertes sur créances irrécouvrables'),('parent_id','=',rec.id)])
            line_27.write({
            'net':self.bal_calulator_current_year(['6182']) ,
            'prev_net':self.bal_calulator_previous_years(['6182']),
            })
            line_28 = self.env['detail.cpc.ligne'].search([('name','=','* Reste du poste des autres charges d\'exploitation'),('parent_id','=',rec.id)])
            line_28.write({
            'net':self.bal_calulator_current_year(['6185','6186','6188']) ,
            'prev_net':self.bal_calulator_previous_years(['6185','6186','6188']),
            })
            line_29 = self.env['detail.cpc.ligne'].search([('name','=','Total-618'),('parent_id','=',rec.id)])
            line_29.write({
            'net':self.bal_calulator_current_year(['618']) ,
            'prev_net':self.bal_calulator_previous_years(['618']),
            })
            line_30 = self.env['detail.cpc.ligne'].search([('name','=','* Charges nettes sur cessions de titres et valeurs de placement'),('parent_id','=',rec.id)])
            line_30.write({
            'net':self.bal_calulator_current_year(['6385']) ,
            'prev_net':self.bal_calulator_previous_years(['6385']),
            })
            line_31 = self.env['detail.cpc.ligne'].search([('name','=','* Reste du poste des autres charges financières'),('parent_id','=',rec.id)])
            line_31.write({
            'net':self.bal_calulator_current_year(['6382','6386','6388']) ,
            'prev_net':self.bal_calulator_previous_years(['6382','6386','6388']),
            })
            line_32 = self.env['detail.cpc.ligne'].search([('name','=','Total-638'),('parent_id','=',rec.id)])
            line_32.write({
            'net':self.bal_calulator_current_year(['638']) ,
            'prev_net':self.bal_calulator_previous_years(['638']),
            })
            line_34 = self.env['detail.cpc.ligne'].search([('name','=','* Pénalités sur marchés et dédits'),('parent_id','=',rec.id)])
            line_34.write({
            'net':self.bal_calulator_current_year(['6581']) ,
            'prev_net':self.bal_calulator_previous_years(['6581']),
            })
            line_35 = self.env['detail.cpc.ligne'].search([('name','=','* Rappels d\'impôts (autres qu\'impôts sur les résultats)'),('parent_id','=',rec.id)])
            line_35.write({
            'net':self.bal_calulator_current_year(['6582']) ,
            'prev_net':self.bal_calulator_previous_years(['6582']),
            })
            line_36 = self.env['detail.cpc.ligne'].search([('name','=','* Pénalités et amendes fiscales et pénales'),('parent_id','=',rec.id)])
            line_36.write({
            'net':self.bal_calulator_current_year(['6583']) ,
            'prev_net':self.bal_calulator_previous_years(['6583']),
            })

            line_37 = self.env['detail.cpc.ligne'].search([('name','=','* Créances devenues irrécouvrables'),('parent_id','=',rec.id)])
            line_37.write({
            'net':self.bal_calulator_current_year(['6585']) ,
            'prev_net':self.bal_calulator_previous_years(['6585']),
            })

            line_38 = self.env['detail.cpc.ligne'].search([('name','=','* Reste du poste des autres charges non courantes'),('parent_id','=',rec.id)])
            line_38.write({
            'net':self.bal_calulator_current_year(['6586','6588']) ,
            'prev_net':self.bal_calulator_previous_years(['6586','6588']),
            })

            line_39 = self.env['detail.cpc.ligne'].search([('name','=','Total-658'),('parent_id','=',rec.id)])
            line_39.write({
            'net':self.bal_calulator_current_year(['658']) ,
            'prev_net':self.bal_calulator_previous_years(['658']),
            })

            line_40 = self.env['detail.cpc.ligne'].search([('name','=','* Ventes de marchandises au Maroc'),('parent_id','=',rec.id)])
            line_40.write({
            'net':self.bal_calulator_current_year(['7111']) ,
            'prev_net':self.bal_calulator_previous_years(['7111']),
            })
            line_41 = self.env['detail.cpc.ligne'].search([('name','=','* Ventes de marchandises à l\'étranger'),('parent_id','=',rec.id)])
            line_41.write({
            'net':self.bal_calulator_current_year(['7113']) ,
            'prev_net':self.bal_calulator_previous_years(['7113']),
            })
            line_42 = self.env['detail.cpc.ligne'].search([('name','=','* Reste du poste des ventes de marchandises'),('parent_id','=',rec.id)])
            line_42.write({
            'net':self.bal_calulator_current_year(['7118','7119']) ,
            'prev_net':self.bal_calulator_previous_years(['7118','7119']),
            })
            line_43 = self.env['detail.cpc.ligne'].search([('name','=','Total-711'),('parent_id','=',rec.id)])
            line_43.write({
            'net':self.bal_calulator_current_year(['711']) ,
            'prev_net':self.bal_calulator_previous_years(['711']),
            })
            
            line_2222 = self.env['detail.cpc.ligne'].search([('name','=','712 * Ventes de biens et services produits'),('parent_id','=',rec.id)])
            line_2222.write({
            'net':self.bal_calulator_current_year(['712']) ,
            'prev_net':self.bal_calulator_previous_years(['712']),
            })

            line_44 = self.env['detail.cpc.ligne'].search([('name','=','*Ventes de biens au Maroc'),('parent_id','=',rec.id)])
            line_44.write({
            'net':self.bal_calulator_current_year(['7121']) ,
            'prev_net':self.bal_calulator_previous_years(['7121']),
            })

            line_45 = self.env['detail.cpc.ligne'].search([('name','=','*Ventes de biens à l\'étranger'),('parent_id','=',rec.id)])
            line_45.write({
            'net':self.bal_calulator_current_year(['7122']) ,
            'prev_net':self.bal_calulator_previous_years(['7122']),
            })

            line_46 = self.env['detail.cpc.ligne'].search([('name','=','*Ventes de services au Maroc'),('parent_id','=',rec.id)])
            line_46.write({
            'net':self.bal_calulator_current_year(['7124']) ,
            'prev_net':self.bal_calulator_previous_years(['7124']),
            })
            line_47 = self.env['detail.cpc.ligne'].search([('name','=','*Ventes de services à l\'étranger'),('parent_id','=',rec.id)])
            line_47.write({
            'net':self.bal_calulator_current_year(['7125']) ,
            'prev_net':self.bal_calulator_previous_years(['7125']),
            })
            line_48 = self.env['detail.cpc.ligne'].search([('name','=','* Redevances pour brevets, marques, droits..'),('parent_id','=',rec.id)])
            line_48.write({
            'net':self.bal_calulator_current_year(['7126']) ,
            'prev_net':self.bal_calulator_previous_years(['7126']),
            })
            line_49 = self.env['detail.cpc.ligne'].search([('name','=','* Reste du poste des ventes et services produits'),('parent_id','=',rec.id)])
            line_49.write({
            'net':self.bal_calulator_current_year(['7127','7128','7129']) ,
            'prev_net':self.bal_calulator_previous_years(['7127','7128','7129']),
            })
            line_50 = self.env['detail.cpc.ligne'].search([('name','=','Total-712'),('parent_id','=',rec.id)])
            line_50.write({
            'net':self.bal_calulator_current_year(['712']) ,
            'prev_net':self.bal_calulator_previous_years(['712']),
            })
            line_51 = self.env['detail.cpc.ligne'].search([('name','=','* Variation des stocks des biens produits (+/-)'),('parent_id','=',rec.id)])
            line_51.write({
            'net':self.bal_calulator_current_year(['7132']) ,
            'prev_net':self.bal_calulator_previous_years(['7132']),
            })
            line_52 = self.env['detail.cpc.ligne'].search([('name','=','*Variation des stocks des services produits (+/-)'),('parent_id','=',rec.id)])
            line_52.write({
            'net':self.bal_calulator_current_year(['7134']) ,
            'prev_net':self.bal_calulator_previous_years(['7134']),
            })
            line_53 = self.env['detail.cpc.ligne'].search([('name','=','*Variation des stocks des produits en cours (+/-)'),('parent_id','=',rec.id)])
            line_53.write({
            'net':self.bal_calulator_current_year(['7131']) ,
            'prev_net':self.bal_calulator_previous_years(['7131']),
            })
            line_54 = self.env['detail.cpc.ligne'].search([('name','=','Total-713'),('parent_id','=',rec.id)])
            line_54.write({
            'net':self.bal_calulator_current_year(['713']) ,
            'prev_net':self.bal_calulator_previous_years(['713']),
            })
            line_55 = self.env['detail.cpc.ligne'].search([('name','=','* Jetons de présence reçus'),('parent_id','=',rec.id)])
            line_55.write({
            'net':self.bal_calulator_current_year(['7181']) ,
            'prev_net':self.bal_calulator_previous_years(['7181']),
            })
            line_56 = self.env['detail.cpc.ligne'].search([('name','=','Total-718'),('parent_id','=',rec.id)])
            line_56.write({
            'net':self.bal_calulator_current_year(['718']) ,
            'prev_net':self.bal_calulator_previous_years(['718']),
            })
            line_57 = self.env['detail.cpc.ligne'].search([('name','=','* Reste du poste (produits divers)'),('parent_id','=',rec.id)])
            line_57.write({
            'net':self.bal_calulator_current_year(['7182','7185','7186','7188']) ,
            'prev_net':self.bal_calulator_previous_years(['7182','7185','7186','7188']),
            })
            line_58 = self.env['detail.cpc.ligne'].search([('name','=','* Reprises'),('parent_id','=',rec.id)])
            line_58.write({
            'net':self.bal_calulator_current_year(['7191','7192','7193','7194','7195','7196','7198']) ,
            'prev_net':self.bal_calulator_previous_years(['7191','7192','7193','7194','7195','7196','7198']),
            })
            line_59 = self.env['detail.cpc.ligne'].search([('name','=','*Transferts de charges'),('parent_id','=',rec.id)])
            line_59.write({
            'net':self.bal_calulator_current_year(['7197']) ,
            'prev_net':self.bal_calulator_previous_years(['7197']),
            })
            line_60 = self.env['detail.cpc.ligne'].search([('name','=','Total-719'),('parent_id','=',rec.id)])
            line_60.write({
            'net':self.bal_calulator_current_year(['719']) ,
            'prev_net':self.bal_calulator_previous_years(['719']),
            })
            line_61 = self.env['detail.cpc.ligne'].search([('name','=','* Intérêts et produits assimilés'),('parent_id','=',rec.id)])
            line_61.write({
            'net':self.bal_calulator_current_year(['7381']) ,
            'prev_net':self.bal_calulator_previous_years(['7381']),
            })
            line_62 = self.env['detail.cpc.ligne'].search([('name','=','* Revenus des créances rattachées à des participations'),('parent_id','=',rec.id)])
            line_62.write({
            'net':self.bal_calulator_current_year(['7383']) ,
            'prev_net':self.bal_calulator_previous_years(['7383']),
            })
            line_63 = self.env['detail.cpc.ligne'].search([('name','=','* Produits nets sur cessions de titres et valeurs de placement'),('parent_id','=',rec.id)])
            line_63.write({
            'net':self.bal_calulator_current_year(['7385']) ,
            'prev_net':self.bal_calulator_previous_years(['7385']),
            })
            line_64 = self.env['detail.cpc.ligne'].search([('name','=','* Reste du poste intérêts et autres produits financiers'),('parent_id','=',rec.id)])
            line_64.write({
            'net':self.bal_calulator_current_year(['7384','7386','7388']) ,
            'prev_net':self.bal_calulator_previous_years(['7384','7386','7388']),
            })
            line_65 = self.env['detail.cpc.ligne'].search([('name','=','Total-738'),('parent_id','=',rec.id)])
            line_65.write({
            'net':self.bal_calulator_current_year(['738']) ,
            'prev_net':self.bal_calulator_previous_years(['738']),
            })
            
    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(34) # read documentation XML
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                for line in rec.line_ids:
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.net)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_prev_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.prev_net)
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(70)
                etree.SubElement(extra_field_valeur,"valeur").text = str(rec.fy_n_id.date_end)
            else:
                pass
            
class DetailCPCLignes(models.Model):
    _name = "detail.cpc.ligne"

    name = fields.Char(string=u"Nom",required=True,readonly=True)
    net  = fields.Float(string=u"Net",readonly=True)
    prev_net  = fields.Float(string=u"Net d'exercice précédent",readonly=True)
    
    
    # Code edi
    code_edi_net  = fields.Integer(string=u"Code Edi Net",readonly=True)
    code_edi_prev_net  = fields.Integer(string=u"Edi Net d'exercice précédent",readonly=True)
    
    # relational fields 
    parent_id = fields.Many2one(string='bilan id', comodel_name='detail.cpc')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('detail.cpc.ligne'))



