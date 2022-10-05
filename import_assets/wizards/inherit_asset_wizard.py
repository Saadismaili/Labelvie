from odoo import models , fields, api, _ 

class ASSETImport(models.TransientModel):
    _inherit = 'import.asset'


    def convert_debit_credit(self,val,x):

        if val[x] != '':
            
            val[x] = float(val[x])
        else:
            val[x] = 0.0
    
    def create_objects(self,model_ref,values):
        return self.env[model_ref].create(values)
            