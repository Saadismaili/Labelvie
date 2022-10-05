""" init py report account.report.passage """
import ast
import json

import io
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import format_date
from odoo.tools.misc import xlsxwriter
from odoo.tools.safe_eval import safe_eval

# pylint: disable=no-member, unused-argument, consider-using-ternary
# pylint: disable=no-self-use, unused-variable, redefined-outer-name
# pylint: disable=too-many-arguments, too-many-locals, protected-access
# pylint: disable=too-many-nested-blocks
class AccountReportPassage(models.AbstractModel):
    """ init py report account.report.passage """
    _name = "account.report.passage"
    _description = "account.report.passage"
    _inherit = "account.report.profit"
    _group_model = 'passage.group'

    @api.model
    def _get_report_name(self):
        """
        Override  _get_report_name
        """
        return _("Passage")
    
    def print_pdf(self, options):
        
        return {
                'type': 'ir_actions_account_report_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'pdf',
                         'financial_id': self.env.context.get('id'),
                         }
                }
    
    def open_line_journal_items(self, options, params=None):
        """
        open_line_journal_items
        """
        if not params:
            params = {}

        name_obj = params.get('caret_options', False)
        if name_obj:
            line = self.env[name_obj].browse(params.get('id', 0))
            ctx = self.env.context.copy()
            ctx.update(search_default_posted=1)
            action = self.env.ref('account.action_move_line_select').read()[0]
            if 'domain' in action and not action['domain']:
                action['domain']='[]'
            domain = expression.normalize_domain(ast.literal_eval(action.get('domain', '[]')))
            account_ids, sub_account_ids = line.get_accounts()
            period_fiscal_year_year = line.period_fiscal_year_year
            previous_fiscal_year = line.previous_fiscal_year
            specific_year = line.specific_year
            rapport_specific_year=line.rapport_specific_year
            all_acc_ids = account_ids | sub_account_ids
            if all_acc_ids:
                domain = expression.AND(
                    [domain, [('account_id', 'in', all_acc_ids.ids),
                              ('parent_state', '!=', 'cancel')]])
            if options:
                if options.get('date'):
                    opt_date = options['date']
                    if opt_date.get('date_from'):
                        date_from = self._get_date_from(
                            options, period_fiscal_year_year=period_fiscal_year_year,previous_fiscal_year=previous_fiscal_year)
                        domain = expression.AND(
                            [domain, [('date', '>=', date_from)]])
                    if opt_date.get('date_to'):
                        domain = expression.AND(
                            [domain, [('date', '<=', opt_date['date_to'])]])
                    if not opt_date.keys() & {'date_from', 'date_to'} \
                            and opt_date.get('date'):
                        domain = expression.AND(
                            [domain, [('date', '<=', opt_date['date'])]])
                if options.get('all_entries'):
                    ctx.update(search_default_unposted=1)
                action['domain'] = domain
            action['context'] = ctx
            return action
        return {}

    def _get_date_from(self, options,period_fiscal_year_year=None,previous_fiscal_year=None,specific_year=None,rapport_specific_year=None):
        """
        Get Date From
        :return:
        """
        if options and options.get('date'):
            if period_fiscal_year_year or previous_fiscal_year:
                date_to = options.get('date').get('date_to')
                return self._get_from_fiscal_year(date_to)[1]
        return '1900-01-01'
    
    @api.model
    def _get_columns_name(self, options):
        """
        Override function _get_columns_name
        """
        columns = [{'name': '', 'style': 'width:2%'},
                   {'name': '', 'style': 'width:80%'},
                   {'name': _('MONTANT'), 'class': 'number'},
                   {'name': _('MONTANT'), 'class': 'number'},
                    ]
        count_opt = len(options['comparison']['periods'])
        if options.get('comparison') and options['comparison'].get('periods'):
            columns += [{'name': _('Net'), 'class': 'number '}] * count_opt
        return columns



    # pylint: disable=invalid-name, too-many-branches, too-many-statements
    @api.model
    def _get_lines(self, options, line_id=None):
        """
        Override function _get_lines
        """
        # Create new options with 'unfold_all' to compute the initial balances.
        # Then, the '_do_query' will compute
        # all sums/unaffected earnings/initial balances for all comparisons.
        self.print_pdf(options=options)
        lines = []
        passage_data = []
        ctx = self.env.context.copy()
        number_of_columns = self._number_of_columns or 2
        min_python_value_numbers = 4
        if number_of_columns == 1:
            min_python_value_numbers = 2
        group_model = self._group_model
        count_opt = len(options['comparison']['periods'])
        date_from = options['date']['date_from']
        date_to = options['date']['date_to']
        dateto_datetime = datetime.strptime(date_to, "%Y-%m-%d")
        datefrom_datetime = datetime.strptime(date_from, "%Y-%m-%d")
        ctx.update(date_from=date_from, date_to=date_to,
                   year=dateto_datetime.year)
        gorup_ids = self.env[group_model].search([], order='sequence asc')
        list_groups = {}
        acc_obj = self.env['account.account']
        test_cal = 0
        calcul = 0
        cal_reports_1 = 0
        cal_reports_2 = 0
        cal_reports_3 = 0
        cal_reports_4 = 0
        n_4 = bal_4 = n_3 = n_2 = n_1 = bal_3 = bal_2 = bal_1 = 0
        for group in gorup_ids:
            if group.group_type == 'lines':
                group_lines = []
                group_columns = []
                for line in group.line_ids:
                    account_ids = line.account_ids
                    subtraction_account_ids = line.subtraction_account_ids
                    account2_ids = line.account2_ids
                    subtraction_account2_ids = line.subtraction_account2_ids
                    if line.account_source_method == 'code':
                        account_ids = subtraction_account_ids = acc_obj
                        account2_ids = subtraction_account2_ids = acc_obj
                        results = line.with_context(ctx).run_code()
                        counts = 0
                        for one_row in results:
                            counts += 1
                            if len(one_row) < min_python_value_numbers:
                                raise UserError(
                                    _('Error Python Value In Group/Line: %s/%s.'
                                      '') % (group.name, line.name)
                                )
                            name = one_row[0]
                            value1 = one_row[1]
                            columns = [{'name': self.format_value(value1),
                                        'class': 'number',
                                        'no_format_name': value1,
                                        'title': 'Python Code'}]
                            if min_python_value_numbers > 2:
                                value2 = one_row[2]
                                value3 = one_row[3]
                                columns.append({
                                    'name': self.format_value(value2),
                                    'class': 'number',
                                    'no_format_name': value2,
                                    'title': 'Python Code'
                                })
                                columns.append({
                                    'name': self.format_value(value3),
                                    'class': 'number',
                                    'no_format_name': value3,
                                    'title': 'Python Code',
                                })
                            for year in range(1, count_opt + 1):
                                columns.append({
                                    'name': self.format_value(
                                        0),
                                    'class': 'number',
                                    'no_format_name': 0,
                                    'title': 'Compare %s' % year
                                })
                            group_lines.append({
                                'id': "line_%d_code_%d" % (line.id, counts),
                                'name': name,
                                'title_hover': name,
                                'columns': self.action_sign_columns(
                                    columns, value_type=line.value_type,
                                    view_type=line.view_type),
                                'unfoldable': False,
                                'left_col': line.left_char,
                                'caret_options': '',
                            })
                        continue
                    elif line.account_source_method == 'domain':
                        if line.accounts_domain:
                            account_ids = acc_obj.search(
                                safe_eval(line.accounts_domain))
                        if line.accounts2_domain:
                            account2_ids = acc_obj.search(
                                safe_eval(line.accounts2_domain))
                        if line.subtraction_accounts_domain:
                            subtraction_account_ids = acc_obj.search(safe_eval(
                                line.subtraction_accounts_domain))
                        if line.subtraction_accounts2_domain:
                            subtraction_account2_ids = acc_obj.search(safe_eval(
                                line.subtraction_accounts2_domain))

                    balance = balance2 = 0
                    if account_ids:
                        balance = self._get_account_values(
                            options, account_ids.ids,
                                period_fiscal_year_year=line.period_fiscal_year_year
                                ,specific_year=line.specific_year,rapport_specific_year=line.rapport_specific_year)
                    if subtraction_account_ids:
                        balance -= self._get_account_values(
                            options, subtraction_account_ids.ids,
                                period_fiscal_year_year=line.period_fiscal_year_year
                                ,specific_year=line.specific_year,rapport_specific_year=line.rapport_specific_year)
                    if account2_ids:
                        balance2 = self._get_account_values(
                            options, account2_ids.ids,
                                period_fiscal_year_year=line.period_fiscal_year_year
                                ,specific_year=line.specific_year,rapport_specific_year=line.rapport_specific_year)
                    if subtraction_account2_ids:
                        balance2 -= self._get_account_values(
                            options, subtraction_account2_ids.ids,
                                period_fiscal_year_year=line.period_fiscal_year_year
                                ,specific_year=line.specific_year,rapport_specific_year=line.rapport_specific_year)
                    net = balance - balance2 # i modify here 
                    
                    result_cal = 0
                    report_cal = 0
                    plus_account_domain = '[["code","=like","619%"]]'
                    plus_account_ids = group.account_ids
                    plus_account_ids = acc_obj.search(
                            safe_eval(plus_account_domain))
                    plus_report_domain = '["|","|",["code","=like","71%"],["code","=like","73%"],["code","=like","75%"]]'
                    minus_report_domain = '["|","|","|",["code","=like","61%"],["code","=like","63%"],["code","=like","65%"],["code","=like","67%"]]'
                    account_repport_plus_ids = group.account_ids
                    account_repport_minus_ids = group.subtraction_account_ids
                    account_repport_plus_ids = acc_obj.search(
                            safe_eval(plus_report_domain))
                    account_repport_minus_ids = acc_obj.search(
                            safe_eval(minus_report_domain))
                    if account_repport_plus_ids:
                        report_cal = self._get_account_values(
                            options, account_repport_plus_ids.ids,period_fiscal_year_year=True)
                    if account_repport_minus_ids:
                        report_cal -= self._get_account_values(
                            options, account_repport_minus_ids.ids,period_fiscal_year_year=True)
                        
                    # calculate other lines from disallowed expense     
                    if line.period_fiscal_year != False and line.period_fiscal_year != None and line.period_fiscal_year != '666':
                        move_line = self.env['account.move.line'].search([('disallowed_expense_id.code','=',line.period_fiscal_year),('date','>=',datefrom_datetime),('date','<=',dateto_datetime),('company_id','=',self.env.company.id)])
                        if move_line.exists():
                            balance = 0
                            for move in move_line:
                                balance += move.disallowed_price
                        else:
                            balance = 0

                    # calculate reintegration - dediction   
                    if str(line.group_id.sequence) in ['30','40']:
                        calcul += balance
                    if str(line.group_id.sequence) in ['70','60']:
                        calcul -= balance
                    
                    # here we calculate the benifice and perte 
                    if line.specific_line_type == 'perte':
                        if balance2 < 0 :
                            balance2 = abs(balance2)
                        else:
                            balance2 = 0
                    elif line.specific_line_type == 'benifice':
                        if balance2 > 0 :
                            balance2 = balance2
                        else:
                            balance2 = 0
                    elif line.specific_line_type == 'perte_brut':
                        
                        if report_cal < 0 :
                            balance2 = abs(report_cal ) - calcul
                        else:
                            balance2 = 0
                    elif line.specific_line_type == 'benifice_brut':
                        if report_cal > 0 :
                            balance2 = report_cal + calcul
                        else:
                            balance2 = 0
                    elif line.specific_line_type == 'perte_net':
                        if report_cal < 0 :
                            balance2 = abs(report_cal) - calcul
                        else:
                            balance2 = 0
                    elif line.specific_line_type == 'benifice_net':
                        if report_cal > 0 :
                            balance2 = report_cal + calcul
                        else:
                            balance2 = 0
                    else:
                        balance2 = balance2
                        balance = balance
                    # Cumul repport part
                    date_from = options['date']['date_from']
                    date_to = options['date']['date_to']
                    date_to = date_to.split('-')
                    date_from = date_from.split('-')
                    prev_year = int(date_to[0]) 
                    date_to = str(prev_year) + '-' + date_to[1] + '-' + date_to[2]
                    date_from = str(prev_year) + '-' + date_from[1] + '-' + date_from[2]
                    dateto_datetime = datetime.strptime(date_to, "%Y-%m-%d")
                    datefrom_datetime = datetime.strptime(date_from, "%Y-%m-%d")
                    passage_data = self.env['passage.enterieur'].search([('date','>=',datefrom_datetime),('date','<=',dateto_datetime),('company_id','=',self.env.company.id)])    
                    passage_data_2 = self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)])    
                    cumul_mouvements = self.env['account.move'].search([('date','<=',dateto_datetime),('state','=','posted'),('company_id','=',self.env.company.id)],order="date asc")
                    cumul_final = 0
                    enterieur = 0             
                    if str(line.sequence) == '75' and str(line.period_fiscal_year) == '666':
                        var_cal = 0
                        if passage_data_2 and passage_data_2.date.year < dateto_datetime.year:
                            enterieur = passage_data_2.cumule_amorti 
                        
                        for move in cumul_mouvements:
                            disallowed_expense = 0
                            sum_619 = 0
                            sum_charge_net = 0
                            sum_prod_net = 0
                            if move.date.year < dateto_datetime.year:
                                for ligne in move.line_ids:
                                    if ligne.disallowed_expense_id:
                                        disallowed_expense += ligne.disallowed_price
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1]) in ['67','47','17'] :
                                        disallowed_expense += abs(ligne.debit - ligne.credit)
                                    if  str(ligne.account_id.code[0] + ligne.account_id.code[1] + ligne.account_id.code[2] + ligne.account_id.code[3]) in ['6118','6128','6148','6168','6178','6188','6198','6318','6338','6388','6398','7321','7325'] :
                                        disallowed_expense += abs(ligne.debit - ligne.credit)
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1] + ligne.account_id.code[2] + ligne.account_id.code[3] + ligne.account_id.code[4]) in ['63118','73811']:
                                        disallowed_expense += abs(ligne.debit - ligne.credit)
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1] + ligne.account_id.code[2]) == '619':
                                        sum_619 += ligne.debit - ligne.credit
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1]) in ['73','75','71'] :
                                        sum_prod_net += ligne.debit - ligne.credit 
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1]) in ['63','65','67','61']:
                                        sum_charge_net += ligne.debit - ligne.credit
                                if ( abs(sum_prod_net) - abs(sum_charge_net))  < 0 :
                                
                                    if  abs(abs(sum_prod_net) - abs(sum_charge_net)) > sum_619 :
                                        if passage_data_2 and passage_data_2.date.year == dateto_datetime.year - 1 :
                                            var_cal =  passage_data_2.exercice_n_3 + passage_data_2.exercice_n_2 + passage_data_2.exercice_n_1
                                            if  move.date.year == dateto_datetime.year - 1:
                                                var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619 
                                        elif passage_data_2 and passage_data_2.date.year == dateto_datetime.year - 2 :
                                            var_cal = passage_data_2.exercice_n_2 + passage_data_2.exercice_n_1
                                            if move.date.year== dateto_datetime.year - 2 or move.date.year== dateto_datetime.year - 1:
                                                var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619
                                        elif passage_data_2 and passage_data_2.date.year == dateto_datetime.year - 3 :
                                            var_cal =  passage_data_2.exercice_n_2 + passage_data_2.exercice_n_1
                                            if move.date.year== dateto_datetime.year - 3 or move.date.year== dateto_datetime.year - 2 or move.date.year== dateto_datetime.year - 1:
                                                var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619
                                        else:
                                            var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619
                                            
                                            
                                        cumul_final += sum_619
                                    else:
                                        cumul_final += abs(sum_prod_net - sum_charge_net)
                                else :
                                    if  abs(sum_prod_net) - abs(sum_charge_net) - abs(var_cal) - disallowed_expense  >= cumul_final + enterieur :
                                        cumul_final = 0
                                        if passage_data_2 and  passage_data_2.date.year < move.date.year:
                                            enterieur = 0
                                        balance = cumul_final + enterieur
                                    else:
                                        balance = 0
                            elif move.date.year == dateto_datetime.year:
                                for ligne in move.line_ids:
                                    if ligne.disallowed_expense_id:
                                        disallowed_expense += ligne.disallowed_price
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1]) in ['67','47','17'] :
                                        disallowed_expense += abs(ligne.debit - ligne.credit)
                                    if  str(ligne.account_id.code[0] + ligne.account_id.code[1] + ligne.account_id.code[2] + ligne.account_id.code[3]) in ['6118','6128','6148','6168','6178','6188','6198','6318','6338','6388','6398','7321','7325'] :
                                        disallowed_expense += abs(ligne.debit - ligne.credit)
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1] + ligne.account_id.code[2] + ligne.account_id.code[3] + ligne.account_id.code[4]) in ['63118','73811']:
                                        disallowed_expense += abs(ligne.debit - ligne.credit)
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1] + ligne.account_id.code[2]) == '619':
                                        sum_619 += ligne.debit - ligne.credit
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1]) in ['73','75','71'] :
                                        sum_prod_net += ligne.debit - ligne.credit 
                                    if str(ligne.account_id.code[0] + ligne.account_id.code[1]) in ['63','65','67','61']:
                                        sum_charge_net += ligne.debit - ligne.credit
                                if abs(sum_prod_net) - abs(sum_charge_net) > 0:
                                    if  abs(sum_prod_net) - abs(sum_charge_net) - abs(var_cal) - disallowed_expense  >= cumul_final + enterieur :
                                            balance = cumul_final + enterieur
                                            cumul_final = 0
                                            enterieur = 0        
                        if passage_data:
                            balance=0 
                    # exercices repport part
                    if line.rapport_specific_year == '4':
                        bal_4 = 0
                        if report_cal > 0 and report_cal + calcul > 0:
                            if balance < 0 :
                                result_cal = self._get_account_values(
                                options, plus_account_ids.ids,rapport_specific_year=line.rapport_specific_year)
                                if abs(balance) >= abs(result_cal) :
                                    balance = abs(balance) - abs(result_cal) - bal_4
                                    if line.period_fiscal_year == '666':

                                        if passage_data and passage_data.exercice_n_4 > 0:
                                            balance = passage_data.exercice_n_4
                                        elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 3:
                                            balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                        elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 2:
                                            balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_2
                                        elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                            balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_3  
                                        else:
                                            balance = balance
                                            
                                else:
                                    balance = 0
                            else:
                                if line.period_fiscal_year == '666':
                                    if passage_data and passage_data.exercice_n_4 > 0:
                                        balance = passage_data.exercice_n_4
                                    elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 3:
                                        balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                    elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 2:
                                        balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_2
                                    elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                        balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_3  
                                    else:
                                        balance = 0
                                else:
                                    balance = 0
                            if (report_cal + calcul - abs(balance)) >= 0 :
                                balance = abs(balance)
                                bal_4 = balance
                                n_4 = report_cal + calcul - balance
                            else:
                                balance = 0
                        else:
                                balance = 0
                    elif line.rapport_specific_year == '3':
                        bal_3 = 0
                        if n_4 > 0:
                            if balance < 0  :
                                if plus_account_ids:
                                    result_cal = self._get_account_values(
                                    options, plus_account_ids.ids,rapport_specific_year=line.rapport_specific_year)
                                    if abs(balance) >= abs(result_cal) :
                                        balance = abs(balance) - abs(result_cal) - bal_3
                                        if line.period_fiscal_year == '666':
                                            if passage_data and passage_data.exercice_n_3 > 0:
                                                balance = passage_data.exercice_n_3
                                            elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 2:
                                                balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                            elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                                balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_2
                                            else:
                                                balance = balance
                                                
                                    else:
                                        balance = 0
                            else:
                                if line.period_fiscal_year == '666':

                                    if passage_data and passage_data.exercice_n_3 > 0:
                                        balance = passage_data.exercice_n_3
                                    elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 2:
                                        balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                    elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                        balance =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_2 
                                    else:
                                        balance = 0
                                else:
                                    balance = 0
                            if (n_4 - abs(balance)) >= 0 :
                                balance = abs(balance)
                                bal_3 = balance
                                n_3 = n_4 - balance
                            else:
                                balance = 0
                        else:
                                balance = 0
                    elif line.rapport_specific_year == '2':
                        bal_2 = 0
                        if n_3 > 0:
                            if balance < 0  :
                                if plus_account_ids:
                                    result_cal = self._get_account_values(
                                    options, plus_account_ids.ids,rapport_specific_year=line.rapport_specific_year)
                                if abs(balance) >= abs(result_cal) :
                                    balance = abs(balance) - abs(result_cal) - bal_2
                                    if line.period_fiscal_year == '666':
                                        if passage_data and passage_data.exercice_n_2 > 0:
                                            balance = passage_data.exercice_n_2
                                        elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1 :
                                            balance =self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                        else:
                                            balance = balance
                                            
                                else:
                                    balance = 0
                            else:
                                if line.period_fiscal_year == '666':
                                    if passage_data and passage_data.exercice_n_2 > 0:
                                        balance = passage_data.exercice_n_2
                                    elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                        balance = self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                    else:
                                        balance = 0
                                else:
                                    balance = 0
                            if (n_3 - abs(balance)) >= 0 :
                                balance = abs(balance)
                                bal_2 = balance
                                n_2 = n_3 - balance
                            else:
                                balance = 0
                        else:
                            balance = 0
                    elif line.rapport_specific_year == '1':
                        bal_1 = 0
                        if n_2 > 0:
                            if balance < 0 :
                                if plus_account_ids:
                                    result_cal = self._get_account_values(
                                    options, plus_account_ids.ids,rapport_specific_year=line.rapport_specific_year)
                                if abs(balance) >= abs(result_cal) :
                                    balance = abs(balance) - abs(result_cal) - bal_1
                                    if line.period_fiscal_year == '666':
                                        if passage_data and passage_data.exercice_n_1 > 0:
                                            balance = passage_data.exercice_n_1
                                        else:
                                            balance = balance
                                            
                                else:
                                    balance = 0
                            else:
                                if line.period_fiscal_year == '666':
                                    
                                    if passage_data and passage_data.exercice_n_1 > 0:
                                        balance = passage_data.exercice_n_1
                                    else:
                                        balance = 0
                                else:
                                    balance = 0
                            if (n_2 - abs(balance)) >= 0 :
                                balance = abs(balance)
                                bal_1 = balance
                                n_1 = n_2 - balance
                            else:
                                balance = 0
                        else:
                            balance = 0
                    else:
                        balance2 = balance2
                        balance = balance
                        
                    # exercices part cumulatif
                    if line.specific_year == '1':
                        
                        if balance2 < 0 :
                            if plus_account_ids:
                                result_cal = self._get_account_values(
                                    options, plus_account_ids.ids,specific_year=line.specific_year)
                                if abs(balance2) >= abs(result_cal) :
                                    balance2 = abs(balance2) - abs(result_cal)
                                    if line.period_fiscal_year == '666':
                                        if passage_data and passage_data.exercice_n_1 > 0:
                                            balance2 = passage_data.exercice_n_1
                                            cal_reports_1 = balance2
                                        else:
                                            balance2 = balance2
                                            cal_reports_1 = balance2
                                            
                                else:
                                    balance2 = 0
                                    cal_reports_1 = balance2
                        else:
                            if line.period_fiscal_year == '666':
                                
                                if passage_data and passage_data.exercice_n_1 > 0:
                                    balance2 = passage_data.exercice_n_1
                                    cal_reports_1 = balance2
                                else:
                                    balance2 = 0
                                    cal_reports_1 = balance2
                            else:
                                balance2 = 0
                                cal_reports_1 = balance2
                        if bal_1 > 0 :
                            balance2 = 0
                    elif line.specific_year == '2':
                        
                        if balance2 < 0  :
                            if plus_account_ids:
                                result_cal = self._get_account_values(
                                    options, plus_account_ids.ids,specific_year=line.specific_year)
                                if abs(balance2) >= abs(result_cal) :
                                    balance2 = abs(balance2) - abs(result_cal)
                                    if line.period_fiscal_year == '666':
                                        if passage_data and passage_data.exercice_n_2 > 0:
                                            balance2 = passage_data.exercice_n_2
                                        elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1 :
                                            balance2 =self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                        else:
                                            balance2 = balance2
                                            
                                else:
                                    balance2 = 0
                        else:
                            if line.period_fiscal_year == '666':
                                if passage_data and passage_data.exercice_n_2 > 0:
                                    balance2 = passage_data.exercice_n_2
                                elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                    balance2 = self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                else:
                                    balance2 = 0
                            else:
                                balance2 = 0
                        if bal_2 > 0 :
                            balance2 = 0
                        if account_repport_plus_ids:
                            report_cal = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='1')
                            bal_n_4 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='5')
                            bal_n_3 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='4')
                            bal_n_2 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='3')
                        if account_repport_minus_ids:
                            report_cal -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='1')
                            bal_n_4 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='5')
                            bal_n_3 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='4')
                            bal_n_2 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='3')
                        if passage_data_2 :
                            if passage_data_2.date.year == dateto_datetime.year - 1:
                                bal_n_4 = passage_data_2.exercice_n_3
                                bal_n_3 = passage_data_2.exercice_n_2
                                bal_n_2 = passage_data_2.exercice_n_1
                            if passage_data_2.date.year == dateto_datetime.year - 2:
                                bal_n_4 = passage_data_2.exercice_n_2
                                bal_n_3 = passage_data_2.exercice_n_1
                            if passage_data_2.date.year == dateto_datetime.year - 3:
                                bal_n_4 = passage_data_2.exercice_n_1
                        if report_cal - bal_n_4 - bal_n_3 - bal_n_2  >= 0:
                            balance2 = 0
                        if passage_data_2 and passage_data_2.date.year == dateto_datetime.year:
                            balance2 = passage_data_2.exercice_n_2
                  
                    elif line.specific_year == '3': 
                        if balance2 < 0  :
                            if plus_account_ids:
                                result_cal = self._get_account_values(
                                    options, plus_account_ids.ids,specific_year=line.specific_year)
                            if abs(balance2) >= abs(result_cal) :
                                balance2 = abs(balance2) - abs(result_cal)
                                if line.period_fiscal_year == '666':
                                    if passage_data and passage_data.exercice_n_3 > 0:
                                        balance2 = passage_data.exercice_n_3
                                        cal_reports_3 = balance2
                                    elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 2:
                                        balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                        cal_reports_3 = balance2
                                    elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                        balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_2
                                        cal_reports_3 = balance2
                                    else:
                                        balance2 = balance2
                                        cal_reports_3 = balance2
                                        
                            else:
                                balance2 = 0
                                cal_reports_3 = balance2
                        else:
                            if line.period_fiscal_year == '666':

                                if passage_data and passage_data.exercice_n_3 > 0:
                                    balance2 = passage_data.exercice_n_3
                                    cal_reports_3 = balance2
                                elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 2:
                                    balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                    cal_reports_3 = balance2
                                elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                    balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_2 
                                    cal_reports_3 = balance2
                                else:
                                    balance2 = 0
                                    cal_reports_3 = balance2
                            else:
                                balance2 = 0
                                cal_reports_3 = balance2
                        if bal_3 > 0 :
                            balance2 = 0
                        if account_repport_plus_ids:
                            report_cal = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='1')
                            bal_n_4 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='5')
                            bal_n_3 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='4')
                        if account_repport_minus_ids:
                            report_cal -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='1')
                            bal_n_4 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='5')
                            bal_n_3 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='4')
                        if passage_data_2 :
                            if passage_data_2.date.year == dateto_datetime.year - 1:
                                bal_n_4 = passage_data_2.exercice_n_3
                                bal_n_3 = passage_data_2.exercice_n_2
                            if passage_data_2.date.year == dateto_datetime.year - 2:
                                bal_n_4 = passage_data_2.exercice_n_2
                                bal_n_3 = passage_data_2.exercice_n_1
                            if passage_data_2.date.year == dateto_datetime.year - 3:
                                bal_n_4 = passage_data_2.exercice_n_1
                        if report_cal - bal_n_4 - bal_n_3  >= 0:
                            balance2 = 0
                        if account_repport_plus_ids:
                            report_cal = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='2')
                            bal_n_4 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='6')
                            bal_n_3 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='5')
                        if account_repport_minus_ids:
                            report_cal -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='2')
                            bal_n_4 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='6')
                            bal_n_3 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='5')
                        if passage_data_2 :
                            if passage_data_2.date.year == dateto_datetime.year - 1:
                                bal_n_4 = passage_data_2.exercice_n_3
                                bal_n_3 = passage_data_2.exercice_n_2
                            if passage_data_2.date.year == dateto_datetime.year - 2:
                                bal_n_4 = passage_data_2.exercice_n_2
                                bal_n_3 = passage_data_2.exercice_n_1
                            if passage_data_2.date.year == dateto_datetime.year - 3:
                                bal_n_4 = passage_data_2.exercice_n_1
                        if report_cal - bal_n_4 - bal_n_3>= 0:
                            balance2 = 0
                        
                        if passage_data_2 and passage_data_2.date.year == dateto_datetime.year:
                            balance2 = passage_data_2.exercice_n_3
                    elif line.specific_year == '4':
                        
                        if balance2 < 0 :
                            if balance2 < 0  :
                                if plus_account_ids:
                                    result_cal = self._get_account_values(
                                        options, plus_account_ids.ids,specific_year=line.specific_year)
                                if abs(balance2) >= abs(result_cal) :
                                    balance2 = abs(balance2) - abs(result_cal)
                                    if line.period_fiscal_year == '666':

                                        if passage_data and passage_data.exercice_n_4 > 0:
                                            balance2 = passage_data.exercice_n_4
                                            cal_reports_4 = balance2
                                        elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 3:
                                            balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                            cal_reports_4 = balance2
                                        elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 2:
                                            balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_2
                                            cal_reports_4 = balance2
                                        elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                            balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_3 
                                            cal_reports_4 = balance2 
                                        else:
                                            balance2 = balance2
                                            cal_reports_4 = balance2
                                            
                                else:
                                    balance2 = 0
                                    cal_reports_4 = balance2
                        else:
                            if line.period_fiscal_year == '666':
                                if passage_data and passage_data.exercice_n_4 > 0:
                                    balance2 = passage_data.exercice_n_4
                                    cal_reports_4 = balance2
                                elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 3:
                                    balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_1
                                    cal_reports_4 = balance2
                                elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 2:
                                    balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_2
                                    cal_reports_4 = balance2
                                elif self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]) and self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).date.year == dateto_datetime.year - 1:
                                    balance2 =  self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)]).exercice_n_3  
                                    cal_reports_4 = balance2
                                else:
                                    balance2 = 0
                                    cal_reports_4 = balance2
                            else:
                                balance2 = 0
                                cal_reports_4 = balance2
                        if bal_4 > 0 :
                            balance2 = 0
                        if account_repport_plus_ids:
                            report_cal = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='1')
                            bal_n_4 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='5')
                            bal_n_3 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='4')
                        if account_repport_minus_ids:
                            report_cal -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='1')
                            bal_n_4 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='5')
                        if passage_data_2 :
                            if passage_data_2.date.year == dateto_datetime.year - 1:
                                bal_n_4 = passage_data_2.exercice_n_3
                            if passage_data_2.date.year == dateto_datetime.year - 2:
                                bal_n_4 = passage_data_2.exercice_n_2
                            if passage_data_2.date.year == dateto_datetime.year - 3:
                                bal_n_4 = passage_data_2.exercice_n_1
                        if report_cal - bal_n_4 >= 0:
                            balance2 = 0
                        if account_repport_plus_ids:
                            report_cal = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='2')
                            bal_n_4 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='6')
                        if account_repport_minus_ids:
                            report_cal -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='2')
                            bal_n_4 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='6')
                        if passage_data_2 :
                            if passage_data_2.date.year == dateto_datetime.year - 1:
                                bal_n_4 = passage_data_2.exercice_n_3
                            if passage_data_2.date.year == dateto_datetime.year - 2:
                                bal_n_4 = passage_data_2.exercice_n_2
                            if passage_data_2.date.year == dateto_datetime.year - 3:
                                bal_n_4 = passage_data_2.exercice_n_1
                        if report_cal - bal_n_4 >= 0:
                            balance2 = 0

                        if account_repport_plus_ids:
                            report_cal = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='3')
                            bal_n_4 = self._get_account_values(
                            options, account_repport_plus_ids.ids,specific_year='7')
                        if account_repport_minus_ids:
                            report_cal -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='3')
                            bal_n_4 -= self._get_account_values(
                                options, account_repport_minus_ids.ids,specific_year='7')
                        if passage_data_2 :
                            if passage_data_2.date.year == dateto_datetime.year - 1:
                                bal_n_4 = passage_data_2.exercice_n_3
                            if passage_data_2.date.year == dateto_datetime.year - 2:
                                bal_n_4 = passage_data_2.exercice_n_2
                            if passage_data_2.date.year == dateto_datetime.year - 3:
                                bal_n_4 = passage_data_2.exercice_n_1
                        if report_cal - bal_n_4 >= 0:
                            balance2 = 0
                        
                        if passage_data_2 and passage_data_2.date.year == dateto_datetime.year:
                            balance2 = passage_data_2.exercice_n_4

                    else:
                        balance2 = balance2
                        balance = balance
                    # end of exercices caluclation
                    if number_of_columns == 1:
                        columns = [
                            {
                                'name': self.format_value(balance),
                                'class': 'number', 'no_format_name': balance,
                                'title': 'balance'
                            }
                        ]
                    else:
                        columns = [
                            {
                                'name': self.format_value(balance),
                                'class': 'number', 'no_format_name': balance,
                                'title': 'balance'
                            },
                            {
                                'name': self.format_value(balance2),
                                'class': 'number', 'no_format_name': balance2,
                                'title': 'dep balance'
                            },
                        ]
                    for x in range(1, count_opt + 1):
                        x_dateto = dateto_datetime - relativedelta(years=x)
                        dateto_str = x_dateto.strftime('%Y-%m-%d')
                        x_balance = x_balance2 = 0
                        new_options = options.copy()
                        new_options['date'] = new_options['date'].copy()
                        new_options['date']['date_from'] = '1900-01-01'
                        new_options['date']['date_to'] = dateto_str
                        if account_ids:
                            x_balance = self._get_account_values(
                                new_options, account_ids.ids,
                                period_fiscal_year_year=line.period_fiscal_year_year)
                        if account2_ids:
                            x_balance2 = self._get_account_values(
                                new_options, account2_ids.ids,
                                period_fiscal_year_year=line.period_fiscal_year_year)
                        if subtraction_account_ids:
                            x_balance -= self._get_account_values(
                                new_options, subtraction_account_ids.ids,
                                period_fiscal_year_year=line.period_fiscal_year_year)
                        if subtraction_account2_ids:
                            x_balance2 -= self._get_account_values(
                                new_options, subtraction_account2_ids.ids,
                                period_fiscal_year_year=line.period_fiscal_year_year)
                        x_compare = x_balance - x_balance2 # i modify here +/-
                        columns.append({
                            'name': self.format_value(x_compare),
                            'class': 'number', 'no_format_name': x_compare,
                            'title': 'Compare %s' % x
                        })
                    group_lines.append({
                        'id': line.id,
                        'name': line.name,
                        'title_hover': line.name,
                        'columns': self.action_sign_columns(
                            columns, value_type=line.value_type,
                            view_type=line.view_type),
                        'unfoldable': False,
                        'left_col': line.left_char,
                        'caret_options': line._name,
                    })
                    if not line.disable_sum_group:
                        group_columns.append(columns)
                sum_group_columns = self.copy_list_columns(
                    group_columns, group.name)
                lines.append({
                    'id': group.id,
                    'name': group.name,
                    'title_hover': group.name,
                    'class': 'total',
                    'columns': self.action_sign_columns(
                        sum_group_columns, value_type=group.value_type,
                        view_type=group.view_type),
                    'unfoldable': False,
                    'left_col': group.left_char,
                    'caret_options': group._name,
                })
                if sum_group_columns:
                    list_groups[group.id] = sum_group_columns
                for g_line in group_lines:
                    lines.append(g_line)
            elif group.group_type == 'one_line':
                account_ids = group.account_ids
                subtraction_account_ids = group.subtraction_account_ids
                account2_ids = group.account2_ids
                subtraction_account2_ids = group.subtraction_account2_ids
                if group.account_source_method == 'domain':
                    if group.accounts_domain:
                        account_ids = acc_obj.search(
                            safe_eval(group.accounts_domain))
                    if group.accounts2_domain:
                        account2_ids = acc_obj.search(
                            safe_eval(group.accounts2_domain))
                    if group.subtraction_accounts_domain:
                        subtraction_account_ids = acc_obj.search(
                            safe_eval(group.subtraction_accounts_domain))
                    if group.subtraction_accounts2_domain:
                        subtraction_account2_ids = acc_obj.search(
                            safe_eval(group.subtraction_accounts2_domain))
                balance = balance2 = 0
                if account_ids:
                    balance = self._get_account_values(
                        options, account_ids.ids,period_fiscal_year_year=group.period_fiscal_year_year,previous_fiscal_year=group.previous_fiscal_year)
                if account2_ids:
                    balance2 = self._get_account_values(
                        options, account2_ids.ids,period_fiscal_year_year=group.period_fiscal_year_year,previous_fiscal_year=group.previous_fiscal_year)
                if subtraction_account_ids:
                    balance -= self._get_account_values(
                        options, subtraction_account_ids.ids,period_fiscal_year_year=group.period_fiscal_year_year,previous_fiscal_year=group.previous_fiscal_year)
                if subtraction_account2_ids:
                    balance2 -= self._get_account_values(
                        options, subtraction_account2_ids.ids,period_fiscal_year_year=group.period_fiscal_year_year,previous_fiscal_year=group.previous_fiscal_year)
                net = balance - balance2 
                # Calculate cumul amortissement for all the previous years that their net result < 0 
                date_from = options['date']['date_from']
                date_to = options['date']['date_to']
                date_to = date_to.split('-')
                date_from = date_from.split('-')
                prev_year = int(date_to[0]) 
                date_to = str(prev_year) + '-' + date_to[1] + '-' + date_to[2]
                date_from = str(prev_year) + '-' + date_from[1] + '-' + date_from[2]
                dateto_datetime = datetime.strptime(date_to, "%Y-%m-%d")
                datefrom_datetime = datetime.strptime(date_from, "%Y-%m-%d")
                passage_data = self.env['passage.enterieur'].search([('date','>=',datefrom_datetime),('date','<=',dateto_datetime),('company_id','=',self.env.company.id)])    
                passage_data_2 = self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)])    
                cumul_mouvements = self.env['account.move'].search([('date','<=',dateto_datetime),('state','=','posted'),('company_id','=',self.env.company.id)],order="date asc")
                cumul_final = 0
                enterieur = 0             
                if group.previous_fiscal_year:
                    var_cal = 0
                    if passage_data_2 and passage_data_2.date.year < dateto_datetime.year:
                        enterieur = passage_data_2.cumule_amorti 
                    
                    for move in cumul_mouvements:
                        disallowed_expense = 0
                        sum_619 = 0
                        sum_charge_net = 0
                        sum_prod_net = 0
                        if move.date.year < dateto_datetime.year:
                            for line in move.line_ids:
                                if line.disallowed_expense_id:
                                    disallowed_expense += line.disallowed_price
                                if str(line.account_id.code[0] + line.account_id.code[1]) in ['67','47','17'] :
                                    disallowed_expense += abs(line.debit - line.credit)
                                if  str(line.account_id.code[0] + line.account_id.code[1] + line.account_id.code[2] + line.account_id.code[3]) in ['6118','6128','6148','6168','6178','6188','6198','6318','6338','6388','6398','7321','7325'] :
                                    disallowed_expense += abs(line.debit - line.credit)
                                if str(line.account_id.code[0] + line.account_id.code[1] + line.account_id.code[2] + line.account_id.code[3] + line.account_id.code[4]) in ['63118','73811']:
                                    disallowed_expense += abs(line.debit - line.credit)
                                if str(line.account_id.code[0] + line.account_id.code[1] + line.account_id.code[2]) == '619':
                                    sum_619 += line.debit - line.credit
                                if str(line.account_id.code[0] + line.account_id.code[1]) in ['73','75','71'] :
                                    sum_prod_net += line.debit - line.credit 
                                if str(line.account_id.code[0] + line.account_id.code[1]) in ['63','65','67','61']:
                                    sum_charge_net += line.debit - line.credit
                            if ( abs(sum_prod_net) - abs(sum_charge_net))  < 0 :
                            
                                if  abs(abs(sum_prod_net) - abs(sum_charge_net)) > sum_619 :
                                    if passage_data_2 and passage_data_2.date.year == dateto_datetime.year - 1 :
                                        var_cal =  passage_data_2.exercice_n_3 + passage_data_2.exercice_n_2 + passage_data_2.exercice_n_1
                                        if  move.date.year == dateto_datetime.year - 1:
                                            var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619 
                                    elif passage_data_2 and passage_data_2.date.year == dateto_datetime.year - 2 :
                                        var_cal = passage_data_2.exercice_n_2 + passage_data_2.exercice_n_1
                                        if move.date.year== dateto_datetime.year - 2 or move.date.year== dateto_datetime.year - 1:
                                            var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619
                                    elif passage_data_2 and passage_data_2.date.year == dateto_datetime.year - 3 :
                                        var_cal =  passage_data_2.exercice_n_2 + passage_data_2.exercice_n_1
                                        if move.date.year== dateto_datetime.year - 3 or move.date.year== dateto_datetime.year - 2 or move.date.year== dateto_datetime.year - 1:
                                            var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619
                                    else:
                                        var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619
                                        
                                        
                                    cumul_final += sum_619
                                    balance2 = cumul_final + enterieur
                                else:
                                    cumul_final += abs(sum_prod_net - sum_charge_net)
                                    balance2 = cumul_final + enterieur
                            else :
                                if  abs(sum_prod_net) - abs(sum_charge_net) - abs(var_cal) - disallowed_expense  >= cumul_final + enterieur :
                                    cumul_final = 0
                                    if passage_data_2 and  passage_data_2.date.year < move.date.year:
                                        enterieur = 0
                                    balance2 = 0
                                else:
                                    balance2 = cumul_final + enterieur
                        elif move.date.year == dateto_datetime.year:
                            for line in move.line_ids:
                                if line.disallowed_expense_id:
                                    disallowed_expense += line.disallowed_price
                                if str(line.account_id.code[0] + line.account_id.code[1]) in ['67','47','17'] :
                                    disallowed_expense += abs(line.debit - line.credit)
                                if  str(line.account_id.code[0] + line.account_id.code[1] + line.account_id.code[2] + line.account_id.code[3]) in ['6118','6128','6148','6168','6178','6188','6198','6318','6338','6388','6398','7321','7325'] :
                                    disallowed_expense += abs(line.debit - line.credit)
                                if str(line.account_id.code[0] + line.account_id.code[1] + line.account_id.code[2] + line.account_id.code[3] + line.account_id.code[4]) in ['63118','73811']:
                                    disallowed_expense += abs(line.debit - line.credit)
                                if str(line.account_id.code[0] + line.account_id.code[1] + line.account_id.code[2]) == '619':
                                    sum_619 += line.debit - line.credit
                                if str(line.account_id.code[0] + line.account_id.code[1]) in ['73','75','71'] :
                                    sum_prod_net += line.debit - line.credit 
                                if str(line.account_id.code[0] + line.account_id.code[1]) in ['63','65','67','61']:
                                    sum_charge_net += line.debit - line.credit
                            if abs(sum_prod_net) - abs(sum_charge_net) > 0:
                                if  abs(sum_prod_net) - abs(sum_charge_net) - abs(var_cal) - disallowed_expense  >= cumul_final + enterieur :
                                        cumul_final = 0
                                        enterieur = 0
                                        balance2 = 0
                             
                    if passage_data:
                        balance2 = passage_data.cumule_amorti                       
                    #    End 
                if number_of_columns == 1:
                    columns = [
                        {
                            'name': self.format_value(balance),
                            'class': 'number', 'no_format_name': balance,
                            'title': 'balance'
                        }
                    ]
                else:
                    columns = [
                        {
                            'name': self.format_value(balance),
                            'class': 'number', 'no_format_name': balance,
                            'title': 'balance'
                        },
                        {
                            'name': self.format_value(balance2),
                            'class': 'number', 'no_format_name': balance2,
                            'title': 'dep balance'
                        },
                    ]

                for x in range(1, count_opt + 1):
                    x_dateto = dateto_datetime - relativedelta(years=x)
                    dateto_str = x_dateto.strftime('%Y-%m-%d')
                    x_balance = x_balance2 = 0
                    new_options = options.copy()
                    new_options['date'] = new_options['date'].copy()
                    new_options['date']['date_from'] = '1900-01-01'
                    new_options['date']['date_to'] = dateto_str
                    if account_ids:
                        x_balance = self._get_account_values(
                            new_options, account_ids.ids,period_fiscal_year_year=group.period_fiscal_year_year)
                    if account2_ids:
                        x_balance2 = self._get_account_values(
                            new_options, account2_ids.ids,period_fiscal_year_year=group.period_fiscal_year_year)
                    if subtraction_account_ids:
                        x_balance -= self._get_account_values(
                            new_options, subtraction_account_ids.ids,period_fiscal_year_year=group.period_fiscal_year_year)
                    if subtraction_account2_ids:
                        x_balance2 -= self._get_account_values(
                            new_options, subtraction_account2_ids.ids,period_fiscal_year_year=group.period_fiscal_year_year)
                    x_compare = x_balance + x_balance2
                    columns.append({
                        'name': self.format_value(x_compare),
                        'class': 'number', 'no_format_name': x_compare,
                        'title': 'Compare %s' % x
                    })
                if columns:
                    list_groups[group.id] = columns
                lines.append({
                    'id': group.id,
                    'name': group.name,
                    'title_hover': group.name,
                    'class': 'total',
                    'columns': self.action_sign_columns(
                        columns, value_type=group.value_type,
                        view_type=group.view_type),
                    'unfoldable': False,
                    'left_col': group.left_char,
                    'caret_options': group._name,
                })
            elif group.group_type == 'sum':   
                group_columns = []
                sum_g_columns = []
                sum_g_ids = sub_g_ids = self.env[group_model]
                if group.summation_domain:
                    sum_g_ids = self.env[group_model].search(
                        safe_eval(group.summation_domain)).ids
                if group.subtraction_domain:
                    sub_g_ids = self.env[group_model].search(
                        safe_eval(group.subtraction_domain)).ids
                for sum_g_id in sum_g_ids:
                    if sum_g_id in list_groups:
                        if list_groups[sum_g_id]:
                            group_columns.append(list_groups[sum_g_id])
                for sub_g_id in sub_g_ids:
                    if sub_g_id in list_groups:
                        if list_groups[sub_g_id]:
                            group_columns.append(
                                self.action_sign_columns(list_groups[sub_g_id],
                                                         value_type='reversed',
                                                         view_type='reversed'),
                            )
                if group_columns:
                    sum_g_columns = self.copy_list_columns(
                        group_columns, group.name, sub=1)
                if sum_g_columns:
                    list_groups[group.id] = sum_g_columns
                if group.name=='TOTAL':
                    test_cal += balance                
                lines.append({
                    'id': group.id,
                    'name': group.name,
                    'title_hover': group.name,
                    'class': 'total',
                    'columns': self.action_sign_columns(
                        sum_g_columns, value_type=group.value_type,
                        view_type=group.view_type),
                    'unfoldable': False,
                    'left_col': group.left_char,
                    'caret_options': group._name,
                })
        return lines





    @api.model
    def _get_data(self, ct_query, where_clause, where_params):
        """
        Get Data
        :param ct_query:
        :param where_clause:
        :param where_params:
        :return:
        """
        debit = credit = balance = 0
        query = '''
SELECT
account_move_line.id,
account_move_line.date,
account_move_line.date_maturity,
account_move_line.name,
account_move_line.ref,
account_move_line.is_exempt,
account_move_line.company_id,
account_move_line.account_id,
account_move_line.payment_id,
account_move_line.currency_id,
account_move_line.amount_currency,
account_move_line.disallowed_expense_id,
ROUND(account_move_line.disallowed_price)
AS disallowed_price,
ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)
AS debit,
ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)
AS credit,
ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)
AS balance,
account_move_line__move_id.name         AS move_name,
company.currency_id                     AS company_currency_id,
partner.name                            AS partner_name,
account.code                            AS account_code,
 
account.name                            AS account_name,
journal.code                            AS journal_code,
journal.name                            AS journal_name,
full_rec.name                           AS full_rec_name
FROM account_move_line
LEFT JOIN account_move account_move_line__move_id
ON account_move_line__move_id.id = account_move_line.move_id
LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
LEFT JOIN res_company company ON company.id = account_move_line.company_id
LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
LEFT JOIN account_account account ON account.id = account_move_line.account_id
LEFT JOIN account_journal journal ON journal.id = account_move_line.journal_id
LEFT JOIN account_full_reconcile full_rec
ON full_rec.id = account_move_line.full_reconcile_id
WHERE %s
ORDER BY account_move_line.date, account_move_line.id

                        ''' % (ct_query, where_clause) # i removed line 545 : account_move_line__move_id.type         AS move_type,
        # ORDER BY account_move_line.date, account_move_line.id
        # pylint: disable=sql-injection
        self._cr.execute(query, where_params)
        for data in self._cr.dictfetchall():
            credit += data['credit']
            debit += data['debit']
            account = self.env['account.account'].search([('id','=',data['account_id'])])
            if str(account.code[0] + account.code[1]) == '51':
                balance += data['debit'] - data['credit']
            elif account.code[0] == '2' and  str(account.code[0] + account.code[1]) != '28' and  str(account.code[0] + account.code[1]) != '29':
                balance += data['debit'] - data['credit']
            elif account.code[0] == '3' and  str(account.code[0] + account.code[1]) != '39':
                balance += data['debit'] - data['credit']
            elif account.code[0] == '1' or account.code[0] == '4' or str(account.code[0] + account.code[1]) == '55'  or str(account.code[0] + account.code[1]) == '28' or str(account.code[0] + account.code[1]) == '29' or str(account.code[0] + account.code[1]) == '39' or str(account.code[0] + account.code[1]) == '59' :
                balance += data['credit'] - data['debit']
            elif str(account.code[0] + account.code[1]+ account.code[2]+account.code[3]) == '6119' or str(account.code[0] + account.code[1]+ account.code[2]+account.code[3]) == '6129' :
                balance += data['credit'] - data['debit']
            elif account.code[0] == '7' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '7119' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '7129':
                balance += data['credit'] - data['debit']
            elif str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) == '7119' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) == '7129':
                balance +=data['debit'] - data['credit'] 
            elif account.code[0] == '6' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '6119' and  str(account.code[0] + account.code[1] + account.code[2] + account.code[3]) != '6129':
                balance += data['debit'] - data['credit']
            if data['is_exempt'] == True:
                balance += data['debit'] - data['credit']
            
                    
                
            # else:
            #     if not data['disallowed_price'] or data['disallowed_price'] == 0 and (str(account.code[0]+account.code[1]) == '67' or str(account.code[0]+account.code[1]+account.code[2]+account.code[3]) in ['6588','6598','6518','6568','6118','6128','6149','6168','6178','6188','6198','6318','6338','6388','6398']):
            #         balance += data['debit'] - data['credit']
                    
            #     elif data['disallowed_price'] :
            #         balance +=float(data['disallowed_price'])
        return debit, credit, balance

    def find_index(self,array):
        for element in array:
            if isinstance(element, str) and ('-' in element):
                return array.index(element)

    @api.model
    def _get_account_values(self, options, account_ids,
                            period_fiscal_year_year=None,previous_fiscal_year=None,specific_year=None,rapport_specific_year=None):
        """
        Compute the balance
        """
        
        domain = [('account_id', 'in', account_ids)]
        tables, where_clause, where_params = self._query_get(
            options, domain=domain)
        date = options.get('date')
        if date:
            date_to = date.get('date_to')
            if period_fiscal_year_year:
                date_from, date_to = self._get_from_fiscal_year(date_to)
                domain += [('date', '>=', date_from), ('date', '<=', date_to)]
                where_params[self.find_index(where_params)] = date_to
                where_params[self.find_index(where_params) + 1] = date_from
                
            elif previous_fiscal_year:
                date_from, date_to = self._get_from_fiscal_year(date_to)
                domain += [('date', '>=', date_from), ('date', '<=', date_to)]
                date_to = date_to.split('-')
                date_from = date_from.split('-')
                prev_year = int(date_to[0]) - 1
                date_to = str(prev_year) + '-' + date_to[1] + '-' + date_to[2]
                date_from = str(prev_year) + '-' + date_from[1] + '-' + date_from[2]
                where_params[self.find_index(where_params)] = date_to
                where_params[self.find_index(where_params) + 1] = date_from
            elif specific_year or rapport_specific_year:
                date_from, date_to = self._get_from_fiscal_year(date_to)
                domain += [('date', '>=', date_from), ('date', '<=', date_to)]
                date_to = date_to.split('-')
                date_from = date_from.split('-')
                if specific_year:
                    prev_year = int(date_to[0]) - int(specific_year)
                if rapport_specific_year:
                    prev_year = int(date_to[0]) - int(rapport_specific_year)
                date_to = str(prev_year) + '-' + date_to[1] + '-' + date_to[2]
                date_from = str(prev_year) + '-' + date_from[1] + '-' + date_from[2]
                where_params[self.find_index(where_params)] = date_to
                where_params[self.find_index(where_params) + 1] = date_from                
        ct_query = self.env['res.currency']._get_query_currency_table(options)
        debit, credit, balance = self._get_data(
            ct_query, where_clause, where_params)
        return balance


