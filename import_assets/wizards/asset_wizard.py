from odoo import models, fields,_
import openpyxl
import xlrd
import base64
import io
import csv
from odoo.exceptions import UserError, ValidationError
import datetime as dt
import pandas


class ImportAssetWizard(models.TransientModel):
   _name = 'import.asset'

   file = fields.Binary(string="Séléctionner un fichier excel", required=True)

   def import_assets(self):
        # print(self.file)
        df = pandas.io.excel.read_excel(base64.b64decode(self.file), engine='xlrd',
        dtype={'Date': str,
               'Compte':str,
               'Prix':str,
               'Durée':str,
               'Observation':str,})

        values = df['Date'].values
        date = values
        values = df['Compte'].values
        compte = values
        values = df['Prix'].values
        price = values
        values = df['Durée'].values
        duration = values
        values = df['Observation'].values
        observation = values
        

        for date,compte, price, duration,observation  in zip(date,compte, price, duration,observation ):
            account_prov = self.env['account.account'].search([('id','!=',False)],limit=1)
            while len(account_prov.code) != len(str(compte)):
                if len(str(compte)) > len(account_prov.code):
                    accountings = self.env['account.account'].search([('code','!=',False)])
                    for acc in accountings:
                        acc.write({'code':str(acc.code)+'0'})
                elif len(str(compte)) < len(account_prov.code):
                    compte = str(compte)+'0'
            
            # if isinstance(price, int) or isinstance(price, float):
            #     price = price   
            # elif '.' in str(price) :
            #     price = float(price)
            # else:
            #     price = 0.0
            asset_category = self.env['account.asset.category'].search([('account_immo_id','=', self.env['account.account'].search([('code','=', str(compte))]).id)],limit=1)
            if asset_category.exists():
                asset = [{
                    'name' : observation,
                    'value' :price,
                    'category_id':asset_category.id,
                    'date' : date ,                   
                    'invoice_date':date ,
                    'first_depreciation_manual_date' :date ,
                    'method_number' :duration ,
                    'method_period' :12 ,
                    'prorata' :True  ,
                    'state' :'open'  ,
                }]
                self.create_objects('account.asset.asset',asset)
            else:
                pass
        
            
       
            
    
                        
        


       
        
            


    
    