from odoo import models, fields,_
import openpyxl
import xlrd
import base64
import io
import csv
from odoo.exceptions import UserError, ValidationError
import datetime as dt
import pandas


class ImportJournalEntryWizard(models.TransientModel):
   _name = "import.journal.entry"

   file = fields.Binary(string="Séléctionner un fichier excel", required=True)
   is_file  = fields.Selection(string='Voulez-vous importé', selection=[('piece', 'Une seul piéce'),('grand', 'Grand livre')],required=True, )

   def import_journal_entry(self):
        # print(self.file)
        df = pandas.io.excel.read_excel(base64.b64decode(self.file), engine='xlrd',
        dtype={'date': str,
               'Référence':str,
               'Journal':str,
               'Compte':str,
               'Intitulé':str,
               'Débit':float ,
               'Crédit': float})

        values = df['date'].values
        date = values
        values = df['Compte'].values
        compte = values
        values = df['Référence'].values
        reference = values
        values = df['Intitulé'].values
        intitule = values
        values = df['Débit'].values
        debit = values
        values = df['Crédit'].values
        credit = values
        values = df['Journal'].values
        journal = values
        
        name= reference[0]
        date = date[0]
        journal_id = self.env['account.journal'].search([('name', '=', journal[0])]).id
        self.env['account.move'].create({
        'name':name,
        'date':date,
        'is_imported':True,
        'journal_id' : journal_id})

        for compte,intitule, debit, credit  in zip(compte,intitule, debit, credit ):
            
            account_prov = self.env['account.account'].search([('id','!=',False)],limit=1)
            #  to verify the length of the accounts 
            while len(account_prov.code) != len(str(compte)):
                if len(str(compte)) > len(account_prov.code):
                    accountings = self.env['account.account'].search([('code','!=',False)])
                    for acc in accountings:
                        acc.write({'code':str(acc.code)+'0'})
                elif len(str(compte)) < len(account_prov.code):
                    compte = str(compte)+'0'
            #  to verify the parent account if it exsists or not
            val = str(compte[0]) + str(compte[1]) + str(compte[2]) + str(compte[3])
            
            while len(val) < len(compte):
                val = val + '0'
            
            if '.' in str(debit) :
                debit = float(debit)
            else :
                debit = 0.0
            if '.' in str(credit) :
                credit = float(credit)
            else:
                credit = 0.0
            if debit > 0 and credit > 0:     
                account = self.env['account.account'].search([('code','=',[str(compte)])])
                if not account.exists():
                    result = self.env['account.account'].search([('code','=', str(val))])                    
                    # print('result',result)
                    if result.exists():
                        account_val = [
                            {'code' : compte ,
                            'name' : intitule,
                            'reconcile' :result.reconcile ,
                            'user_type_id' : result.user_type_id.id,
                            }]
                        self.create_objects('account.account',account_val)
                        lines_val_1 = [{'account_id' : self.env['account.account'].search([('code','=',compte)]).id,
                                'partner_id' : False,
                                'name' : intitule,
                                'tax_ids'  : False,
                                'debit'  : debit,
                                'credit': 0,
                                'tax_tag_ids' :False,
                                'tax_tag_invert':False,
                                'move_id':self.env['account.move'].search([('name','=',name),('journal_id','=',journal_id),('date','=',date)],order='id desc', limit=1).id,
                                }]
                        self.create_objects('account.move.line',lines_val_1)
                        lines_val_2 = [{'account_id' : self.env['account.account'].search([('code','=',compte)]).id,
                                'partner_id' : False,
                                'name' : intitule,
                                'tax_ids'  : False,
                                'debit'  : 0,
                                'credit': credit,
                                'tax_tag_ids' :False,
                                'tax_tag_invert':False,
                                'move_id':self.env['account.move'].search([('name','=',name),('journal_id','=',journal_id),('date','=',date)],order='id desc', limit=1).id,
                                }]
                        self.create_objects('account.move.line',lines_val_2)
                    else:
                        raise ValidationError(_('Ce Compte " %s " n\'exist pas dans le plan comptable Maroccain, veuillez corriger votre fichier puis réessayer' % (compte)))
                else:
                    lines_val_1 = [{'account_id' : self.env['account.account'].search([('code','=',compte)]).id,
                            'partner_id' : False,
                            'name' : intitule,
                            'tax_ids'  : False,
                            'debit'  : 0,
                            'credit': credit,
                            'tax_tag_ids' :False,
                            'tax_tag_invert':False,
                            'move_id':self.env['account.move'].search([('name','=',name),('journal_id','=',journal_id),('date','=',date)],order='id desc', limit=1).id,
                            }]
                    self.create_objects('account.move.line',lines_val_1)
                    lines_val_2 = [{'account_id' : self.env['account.account'].search([('code','=',compte)]).id,
                            'partner_id' : False,
                            'name' : intitule,
                            'tax_ids'  : False,
                            'debit'  : debit,
                            'credit': 0,
                            'tax_tag_ids' :False,
                            'tax_tag_invert':False,
                            'move_id':self.env['account.move'].search([('name','=',name),('journal_id','=',journal_id),('date','=',date)],order='id desc', limit=1).id,
                            }]
                    self.create_objects('account.move.line',lines_val_2)
            elif debit > 0 or credit > 0:
                account = self.env['account.account'].search([('code','=',compte)])
                if not account.exists():
                    result = self.env['account.account'].search([('code','=', str(val))])
                    if result.exists():
                        account_val = [
                            {'code' : compte ,
                            'name' : intitule,
                            'reconcile' :result.reconcile ,
                            'user_type_id' : result.user_type_id.id,
                            }]
                        self.create_objects('account.account',account_val)
                        lines_val_1 = [{'account_id' : self.env['account.account'].search([('code','=',compte)]).id,
                                'partner_id' : False,
                                'name' : intitule,
                                'tax_ids'  : False,
                                'debit'  : debit,
                                'credit': credit,
                                'tax_tag_ids' :False,
                                'tax_tag_invert':False,
                                'move_id':self.env['account.move'].search([('name','=',name),('journal_id','=',journal_id),('date','=',date)],order='id desc', limit=1).id,
                                }]
                        self.create_objects('account.move.line',lines_val_1)
                    else:
                        raise ValidationError(_('Ce Compte " %s " n\'exist pas dans le plan comptable Maroccain, veuillez corriger votre fichier puis réessayer' % (compte)))
                else:
                    lines_val_1 = [{'account_id' : self.env['account.account'].search([('code','=',compte)]).id,
                            'partner_id' : False,
                            'name' : intitule,
                            'tax_ids'  : False,
                            'debit'  : debit,
                            'credit': credit,
                            'tax_tag_ids' :False,
                            'tax_tag_invert':False,
                            'move_id':self.env['account.move'].search([('name','=',name),('journal_id','=',journal_id),('date','=',date)],order='id desc', limit=1).id,
                            }]
                    self.create_objects('account.move.line',lines_val_1)
            # asset category part
            
            if str(str(compte[0]) + str(compte[1]))  in ['21','22','23']:
                dotation = '619'+str(compte[1]) + str(compte[2])
                while len(dotation) < len(compte):
                    dotation = dotation + '0'
                amortissement = '28'+str(compte[1]) + str(compte[2]) + str(compte[3])
                while len(amortissement) < len(compte):
                    amortissement = amortissement + '0'
                if str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '211':
                    account_type = '1'
                    label = '* Frais préliminaires'
                    vna = None
                    cession = None
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '212':
                    account_type = '2'
                    label = '* Charges à répartir sur plusieurs exercices'
                    vna = None
                    cession = None
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '213':
                    account_type = '0' 
                    label = '* Primes de remboursement obligations'
                    vna = None
                    cession = None
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '221':
                    account_type = '3'
                    vna = '6512'
                    label = '* Immobilisation en recherche et développement'
                    cession = '7512'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '222':
                    account_type = '4'
                    vna = '6512'
                    label = '* Brevets, marques droits et valeurs similairest'
                    cession = '7512'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '223':
                    account_type = '5'
                    vna = '6512'
                    label = '* Fonds commercial'
                    cession = '7512'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '228':
                    account_type = '6'
                    vna = '6512'
                    label = '* Autres immobilisations incorporelles'
                    cession = '7512'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '231':
                    account_type = '7'
                    vna = '6513'
                    label = '* Terrains'
                    cession = '7513'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '232':
                    account_type = '8'
                    vna = '6513'
                    label = '* Constructions'
                    cession = '7513'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '233':
                    account_type = '9'
                    vna = '6513'
                    label = '* Installations techniques; matériel et outillage'
                    cession = '7513'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '234':
                    account_type = '10'
                    vna = '6513'
                    label = '* Matériel de transport'
                    cession = '7513'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '235':
                    account_type = '11'
                    vna = '6513'
                    label = '* Mobilier, matériel de bureau et aménagements'
                    cession = '7513'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '238':
                    account_type = '12'
                    vna = '6513'
                    label = '* Autres immobilisations corporelles'
                    cession = '7513'
                elif str(str(compte[0]) + str(compte[1]) + str(compte[2])) == '239':
                    account_type = '13'
                    vna = '6513'
                    label = '* Immobilisations corporelles en cours'
                    cession = '7513'
                else:
                    account_type = '14'
                    vna = None
                    label = 'Autre'
                    cession = None
                if vna != None and cession != None:
                    while len(vna) < len(compte):
                        vna = vna + '0'
                    while len(cession) < len(compte):
                        cession = cession + '0'
                    asset_category = [{
                        'name' : label,
                        'account_type' :account_type,
                        'ref_debit_credit':str(debit - credit),
                        'journal_id' : journal_id ,                   
                        'account_immo_id':self.env['account.account'].search([('code','=', str(compte))]).id ,
                        'account_asset_id' :self.env['account.account'].search([('code','=', str(amortissement))]).id ,
                        'account_depreciation_id' :self.env['account.account'].search([('code','=', str(dotation))]).id ,
                        'account_depreciation_expense_id' :self.env['account.account'].search([('code','=', str(dotation))]).id ,
                        'account_vna_id' :self.env['account.account'].search([('code','=', str(vna))]).id  ,
                        'account_revenue_id' :self.env['account.account'].search([('code','=', str(cession))]).id  ,
                    }]
                else:
                    asset_category = [{
                        'name' : label,
                        'account_type' :account_type,
                        'ref_debit_credit':str(debit - credit),
                        'journal_id' : journal_id ,                   
                        'account_immo_id':self.env['account.account'].search([('code','=', str(compte))]).id ,
                        'account_asset_id' :self.env['account.account'].search([('code','=', str(amortissement))]).id ,
                        'account_depreciation_id' :self.env['account.account'].search([('code','=', str(dotation))]).id ,
                        'account_depreciation_expense_id' :self.env['account.account'].search([('code','=', str(dotation))]).id ,
                    }]
                category = self.env['account.asset.category'].search([('ref_debit_credit','=', str(debit - credit))])
                if category.exists():
                    pass
                else:
                    self.create_objects('account.asset.category',asset_category)
        
            
       
            
    
                        
        


       
        
            


    
    