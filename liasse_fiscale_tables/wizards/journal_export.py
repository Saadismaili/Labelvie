import datetime
import base64
import zipfile
import lxml
import xlwt
import io
from datetime import datetime, timedelta
import base64
from lxml import etree
from openerp import models, api, fields , _
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval

import os

class AccountJournalPrintInherit(models.TransientModel):
    _inherit = 'account.print.journal'
    
    
    def print_xlrd(self):
        data = {
         'date_from': self.date_from, 
         'date_to': self.date_to, 
         'company_id': self.company_id.id,
         'journal_ids':self.journal_ids.ids  
        }
        return self.env.ref('liasse_fiscale_tables.action_liasse_fiscale_tables_xlsx_report').report_action(self, data=data) 

class OsiGenerateMeXlsxReport(models.AbstractModel):
    _name = 'report.liasse_fiscale_tables.account_print_journal'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners=None):
        domain = []
        if data.get('date_from'):
            domain.append(('date', '>=', data.get('date_from')))
        if data.get('date_to'):
            domain.append(('date', '<=', data.get('date_to')))
        if data.get('company_id'):
            domain.append(('company_id', '=', data.get('company_id')))
        
        sheet = workbook.add_worksheet('Journaux')
        bold = workbook.add_format({'bold': True, 'align': 'left',})
        border_top_header = workbook.add_format({ 'align': 'center',})
        border_top_header_2 = workbook.add_format({ 'align': 'left',})
        top_top = workbook.add_format({ 'align': 'center',})
        top_left = workbook.add_format({ 'align': 'center',})
        top_right = workbook.add_format({ 'align': 'center',})
        bottom = workbook.add_format({ 'align': 'center',})
        top_top.set_top(1)
        top_left.set_left(1)
        top_left.set_top(1)
        top_right.set_right(1)
        top_right.set_top(1)
        bottom.set_left(1)
        bottom.set_right(1)
        bottom.set_bottom(1)
        border_left_right_header = workbook.add_format({ 'align': 'center',})
        border_left_right_name = workbook.add_format({ 'align': 'left',})
        border_left_right_vals = workbook.add_format({'align': 'right',})
        border_left_right_name.set_right(1)
        border_left_right_name.set_bottom(1)
        border_left_right_name.set_left(1)
        border_left_right_vals.set_right(1)
        border_left_right_vals.set_left(1)
        border_left_right_vals.set_bottom(1)
        border_top_header.set_right(1)
        border_top_header.set_left(1)
        border_top_header.set_top(1)
        border_left_right_header.set_left(1)
        border_left_right_header.set_right(1)
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 15, })
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        header_row_style_right = workbook.add_format({'bold': True, 'align': 'right', 'border': True})
        header_row_style_left = workbook.add_format({'bold': True, 'align': 'left', 'border': True})
        
        
        journals = self.env['account.journal'].search([('company_id', '=', data.get('company_id')),('id', 'in', data.get('journal_ids'))])
        
        company = self.env['res.company'].search([('id', '=', data.get('company_id'))])
        if journals:
            row = 0
            col = 0
            sheet.write(row, col + 4, str(company.name))
            
            for journal in journals:
                tot_debit  = 0
                tot_credit = 0
                # sheet.write(row, col,  str(datetime.datetime.now()))
                row += 2
                sheet.write(row, col, str(journal.name),title)
                row += 2
                moves = self.env['account.move'].search([('journal_id','=',journal.id),('date', '<=', data.get('date_to')),('company_id', '=', data.get('company_id')),('date', '>=', data.get('date_from')),])
                sheet.set_column(0, 5, 18)
                sheet.write(row , col, 'Date', header_row_style)
                sheet.write(row , col+1, 'Mouvement', header_row_style)
                sheet.write(row , col+2, 'Partenaire', header_row_style)
                sheet.write(row , col+3, 'Compte', header_row_style)
                sheet.write(row , col+4, 'Libellé', header_row_style)
                sheet.write(row , col+5, 'Débit', header_row_style)
                sheet.write(row , col+6, 'Crédit', header_row_style)
                row += 1
                for move in moves:
                    # Header row
                    for line in move.line_ids:
                        tot_debit += line.debit
                        tot_credit += line.credit
                        sheet.write(row, col, str(line.date),border_left_right_name)
                        sheet.write(row, col+1, line.move_id.name,border_left_right_vals)
                        sheet.write(row, col+2, line.partner_id.name,border_left_right_vals)
                        sheet.write(row, col+3, str(line.account_id.code)+ ' ' + str(line.account_id.name),border_left_right_vals)
                        sheet.write(row, col+4, line.name,border_left_right_vals)
                        sheet.write(row, col+5, line.debit,border_left_right_vals)
                        sheet.write(row, col+6, line.credit,border_left_right_vals)
                        row += 1
                sheet.write(row, col, ' ')
                sheet.write(row, col+1, ' ')
                sheet.write(row, col+2, ' ')
                sheet.write(row, col+3, ' ')
                sheet.write(row, col+4, 'Total',border_left_right_vals)
                sheet.write(row, col+5, tot_debit,border_left_right_vals)
                sheet.write(row, col+6, tot_credit,border_left_right_vals)
                row += 3