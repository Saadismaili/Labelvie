from odoo import models, fields, api, _    

class AccountMoveLineInherit(models.Model):

    _inherit = 'account.move.line'
    
    # fields for disallowed expense that helps us calculate report of table 3 
    disallowed_expense_id = fields.Many2one(string='Dépense non autorisée', comodel_name='account.disallowed.expenses.category', required=False)
    disallowed_price  = fields.Float(string='Prix ​​non autorisé')
    is_exempt  = fields.Boolean("c'est exonéré ?")


    # overiding onchange_currency  
    @api.onchange('currency_id')
    def _onchange_currency(self):
        for line in self:
            company = line.move_id.company_id or self.env.company
            if line.move_id.is_invoice(include_receipts=True):
                line._onchange_price_subtotal()
            elif not line.move_id.reversed_entry_id:
                balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, line.move_id.date or fields.Date.context_today(line))
                line.debit = balance if balance > 0.0 else 0.0
                line.credit = -balance if balance < 0.0 else 0.0

    # overiding onchange_amount_currency
    @api.onchange('amount_currency')
    def _onchange_amount_currency(self):
        for line in self:
            company = line.move_id.company_id  or self.env.company
            if not line.currency_id:
                line.write({
                    'currency_id' : self.env.ref('base.MAD')
                })
            balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, line.move_id.date or fields.Date.context_today(line))
            line.debit = balance if balance > 0.0 else 0.0
            line.credit = -balance if balance < 0.0 else 0.0
            if not line.move_id.is_invoice(include_receipts=True):
                continue
            line.update(line._get_fields_onchange_balance())
            line.update(line._get_price_total_and_subtotal())
