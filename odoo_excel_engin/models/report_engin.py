# -*- coding: utf-8 -*-

import datetime
import re
import ast
from xlsxwriter.utility import xl_cell_to_rowcol, xl_col_to_name
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo import models,fields, api,tools
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)


# Rapports Groupe: Ex: Liasse
class ReportGroup(models.Model):
    _name = "report.group"
    _description = "Rapport Excel"

    name = fields.Char('Nom',required=True)
    code_edi = fields.Integer(string='Code edi')
    # company_id = fields.Many2one('res.company', u'Société', default=lambda self: self.env.user.company_id, required=False)
    rapport_ids = fields.One2many(comodel_name='report.groupe.line', inverse_name='group_report_id',
                                   string=u'Rapports')

    # @api.multi
    def report_print(self):
        self.ensure_one()
        report_list = []
        for record in self:
            for report in record.rapport_ids:
                report_list.append(report.report_id.id)
        return self.env['report'].get_action(self.env['report.engin'].browse(report_list), 'report.engin.xlsx')


# Ligne de rapport groupe
class ReportGroupeLine(models.Model):
    _name = "report.groupe.line"
    _description = "Ligne rapport Excel"
    _order = 'sequence, id'

    report_id = fields.Many2one('report.engin', 'Rapport', ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    group_report_id = fields.Many2one('report.group', 'Groupe', ondelete='cascade', readonly=True)
    # company_id = fields.Many2one('res.company', u'Société', default=lambda self: self.env.user.company_id, required=False)


# Rapport: Ex: Actif, Passif
class ReportEngin(models.Model):
    _name = "report.engin"
    _description = "Report engin"

    name = fields.Char(u'Nom', required=True)
    code_edi = fields.Integer(string="Code edi")
    code_python = fields.Boolean(string="Code Python?")
    python = fields.Text()
    edi_python = fields.Many2one("report.pyhton.edi", string="Python Edi")
    line_ids = fields.One2many(comodel_name='report.engin.line', inverse_name='report_id',
                                     string=u'Lignes')
    row_col_ids = fields.One2many(comodel_name='report.engin.row.col', inverse_name='report_id',
                                     string=u'Taille lignes / Colonnes')
    # company_id = fields.Many2one('res.company', u'Société', default=lambda self: self.env.user.company_id, required=False)

    @api.model
    def reset_data(self):
        _logger.error("Deleting the data ....")
        engine_ids = self.env['report.engin'].search([])
        report_group_id = self.env['report.group'].search([])
        engine_lines = self.env['report.engin.line'].search([])
        rc_lines = self.env['report.engin.row.col'].search([])
        list_formulas_lines = self.env['report.list.formulas'].search([])
        group_lines = self.env['report.groupe.line'].search([])
        excel_group_formulas = self.env['excel.report.engin.line'].search([])
        engine_lines.unlink()
        rc_lines.unlink()
        list_formulas_lines.unlink()
        group_lines.unlink()
        excel_group_formulas.unlink()
        engine_ids.unlink()
        report_group_id.unlink()
        _logger.error("Done!")

    # @api.one
    @api.constrains('line_ids')
    def check_unique_formula(self):
        self.ensure_one() # has been added
        for line in self.line_ids:
            if line.is_matrix and len(line.formulas_ids) > 1:
                raise ValidationError(u"Une seule formule peut ête définie pour les tableaux (%s)!" % line.name)

    # @api.multi
    def report_print(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'report.engin.xlsx')

    # @api.multi
    def print_values(self):
        for rec in self:
            for line in rec.line_ids:
                print(line.cell, line.get_cell_value())


class ReportEnginLine(models.Model):
    _name = "report.engin.line"
    _description = "Report engin lines"
    _order = 'report_id desc, sequence, id'

    name = fields.Char(u'Nom', required=True)
    is_matrix = fields.Boolean(u'Tableaux?')
    computation_mode = fields.Selection([
        ('manual', 'Valeur simple'),
        ('compute', 'Formule'),
        ('python', 'Code python'),
    ],
        string="Mode de calcul",
        required=True,
        default='manual')
    cell = fields.Char(u'Cellule', required=True)
    value = fields.Char(u'Valeur')
    format = fields.Char(u'Format')
    python = fields.Text()
    formulas_ids = fields.One2many(comodel_name='report.list.formulas', inverse_name='report_line_id',
                                  string=u'Formules')
    code_edi_ids = fields.One2many(comodel_name='group.code.edi', inverse_name='report_line_id',
                                  string=u'Codes edi')
    sum_ids = fields.One2many(comodel_name='table.sum', inverse_name='report_line_id',
                                  string=u'Totaux')
    report_id = fields.Many2one('report.engin', 'Rapport', ondelete='cascade', readonly=True)
    sequence = fields.Integer(string='Sequence', default=10)

    row = fields.Integer(string="Ligne",compute='get_row_cel',store=True)
    col = fields.Char(string="Colonne",compute='get_row_cel',store=True)
    code_edi = fields.Integer(string="Code edi")
    is_extra_field = fields.Boolean(u'Extra field?')

    excel_formula_cells_ids = fields.One2many('excel.report.engin.line',string =u'Excel formulas lines', compute="get_excel_formula_cells")

    cache_value = fields.Float("Cache value")
    is_cached = fields.Boolean("Cached")
    # company_id = fields.Many2one('res.company', u'Société', default=lambda self: self.env.user.company_id, required=False)

    # @api.multi
    def print_value(self):
        for rec in self:
            print(rec.cell, rec.with_context(ex_n=1,ex_n_1=14).get_cell_value())

    # @api.one
    @api.constrains('code_edi_ids','sum_ids','formulas_ids')
    def check_digit(self):
        self.ensure_one() # has been added
        if self.formulas_ids:
            formula_id = self.formulas_ids[0].formula_id
            if formula_id.computation_mode not in ("python"):
                for code_edi in self.code_edi_ids:
                    if not formula_id.check_field(code_edi.field)[0]:
                        raise ValidationError("Le champ %s n'existe pas pour le model %s" % (code_edi.field, formula_id.model_id.name))
                for sum_field in self.sum_ids:
                    if sum_field.type == 'field':
                        if not formula_id.check_field(sum_field.value)[0]:
                            raise ValidationError(
                                "Le champ %s n'existe pas pour le model %s" % (sum_field.value, formula_id.model_id.name))
                        if not formula_id.check_is_digit_field(sum_field.value)[0]:
                            raise ValidationError(
                                u"Le champ %s doit être un digit" % (sum_field.value))

    # @api.one
    def get_cell_sum_value(self,field):
        self.ensure_one() # has been added
        value = 0.0
        cell_value = self.get_cell_value()[0]
        for elem in cell_value:
            if elem.get(field, False):
                value += elem[field]
        return value

    # @api.one
    def get_cell_value(self):
        self.ensure_one() # has been added
        value = False
        if self.is_cached:
            return self.cache_value
        if self.computation_mode == 'manual':
            if self.excel_formula_cells_ids:
                for line in self.excel_formula_cells_ids:
                    op = 1
                    if line.op == "minus":
                        op = -1
                    cell_value = line.report_line_id.get_cell_value()[0]
                    if isinstance(cell_value, int) or isinstance(cell_value, float) :
                        value += float(line.report_line_id.get_cell_value()[0])*op
            else:
                if self.value.isdigit():
                    value = float(self.value)
                else:
                    if self.value.strip() == "":
                        value = 0.0
                    else:
                        value = self.value
        if self.computation_mode == 'compute':
            for formula in self.formulas_ids:
                if not formula.formula_id.is_matrix:
                    if not isinstance(formula.formula_id.eval_formula(formula.domain), float):
                        value = formula.formula_id.eval_formula(formula.domain)
                    else:
                        op = 1
                        if formula.op == 'minus':
                            op = -1
                        value += formula.formula_id.eval_formula(formula.domain) * op
                else:
                    value = formula.formula_id.eval_formula(formula.domain)
        if isinstance(value, int) or isinstance(value, float):
            self.write({"cache_value" : value, "is_cached":True})
        if not value and not (isinstance(value, int) or isinstance(value, float)):
            value = ""
        return value


    # @api.multi
    @api.depends('value')
    def get_excel_formula_cells(self):
        for record in self:
            list_values = self.env['excel.report.engin.line']
            if record.computation_mode == 'manual' and record.value and not "=IF" in record.value:
                value = record.value.strip()
                report_id = record.report_id
                if value.startswith("=") and value != "=":
                    if (len(value) > 4 and not value[1:4] == "SUM" and not value[1:3] == "IF") or len(value) <= 4:
                        match_formula = re.findall('[\+\-]*[\w\s]+!*\w+', value.replace("'", ""))
                        for elem in match_formula:
                            op = 'plus'
                            if elem.startswith("-"):
                                op = "minus"
                                elem = elem.split("-")[1]
                            if elem.startswith("+"):
                                elem = elem.split("+")[1]
                            if "!" in elem:
                                elem_extern_page = elem.split("!")
                                report_id = self.env['report.engin'].search([('name','=',elem_extern_page[0])])
                                elem = elem_extern_page[1]
                            line_id = self.env['report.engin.line'].search([('cell','=',elem),('report_id','=',report_id.id)])
                            if len(line_id)>1:
                                line_id = line_id[0]
                            if line_id:
                                list_values+=self.env['excel.report.engin.line'].create({
                                        'report_line_id':line_id.id,
                                        'op':op,
                                })
                    if len(value) > 4 and value[1:4] == "SUM":
                        match_formula = value.replace("=SUM","").replace("(","").replace(")","").strip()
                        if ":" in match_formula:
                            elems = match_formula.split(":")
                            num_cel_1 = re.findall('\d+', elems[0])[0]
                            cel_1 = re.findall('[a-zA-Z]+', elems[0])[0]
                            num_cel_2 = re.findall('\d+', elems[1])[0]
                            cel_2 = re.findall('[a-zA-Z]+', elems[1])[0]
                            for code_cell in range(ord(cel_1),ord(cel_2)+1):
                                for range_cell in range(int(num_cel_1),int(num_cel_2)+1):
                                    cell = str(chr(code_cell))+str(range_cell)
                                    line_id = self.env['report.engin.line'].search(
                                        [('cell', '=', cell), ('report_id', '=', report_id.id)])
                                    if len(line_id) > 1:
                                        line_id = line_id[0]
                                    if line_id:
                                        list_values += self.env['excel.report.engin.line'].create({
                                            'report_line_id': line_id.id,
                                            'op': "plus",
                                        })
                        else:
                            line_id = self.env['report.engin.line'].search(
                                [('cell', '=', match_formula), ('report_id', '=', report_id.id)])
                            if len(line_id) > 1:
                                line_id = line_id[0]
                            if line_id:
                                list_values += self.env['excel.report.engin.line'].create({
                                    'report_line_id': line_id.id,
                                    'op': "plus",
                                })
            record.excel_formula_cells_ids = list_values

    # @api.multi
    @api.depends('cell')
    def get_row_cel(self):
        for record in self:
            (row, col) = xl_cell_to_rowcol(record.cell)
            record.row = row+1
            record.col = xl_col_to_name(col)


class ReportEnginRowCol(models.Model):
    _name = "report.engin.row.col"
    _description = "Report engin row/col"

    name = fields.Char(u'Descripion', required=True)
    position = fields.Integer(u'Position', required=True)
    row_value = fields.Integer(u'Taille ligne')
    col_value = fields.Integer(u'Taille colonne')
    report_id = fields.Many2one('report.engin', 'Rapport', ondelete='cascade', readonly=True)


class ReportPyhtonEdi(models.Model):
    _name = "report.pyhton.edi"
    _description = "Python EDI"

    name = fields.Text()


class ReportListFormulas(models.Model):
    _name = "report.list.formulas"
    _description = "Liste formule"

    formula_id = fields.Many2one('formulas.engine', 'Formule', ondelete='cascade')
    domain = fields.Char('Domaine', default='[]')
    report_line_id = fields.Many2one('report.engin.line', 'Ligne de rapport', ondelete='cascade', readonly=True)
    # company_id = fields.Many2one('res.company', u'Société', default=lambda self: self.env.user.company_id, required=False)
    op = fields.Selection([
        ('plus', '+'),
        ('minus', '-'),
    ],
        string="Operateur",
        required=True,
        default='plus')


class GroupCodeEdi(models.Model):
    _name = "group.code.edi"
    _description = "Group code edi"
    _order = 'sequence, id'

    report_line_id = fields.Many2one('report.engin.line', 'Ligne rapport', ondelete='cascade')
    sequence = fields.Integer(string=u'Séquence', default=10)
    code_edi = fields.Integer(string='Code EDI')
    secend_code_edi = fields.Integer(string='Code edi (second)')
    field = fields.Char(string='Champs')


class TableSum(models.Model):
    _name = "table.sum"
    _description = "Table sum"
    _order = 'sequence, id'

    report_line_id = fields.Many2one('report.engin.line', 'Ligne rapport', ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    type = fields.Selection([
        ('field', 'Champs'),
        ('text', 'Texte simple'),
    ],
        string="Type",
        required=True,
        default='field')
    code_edi = fields.Integer(string='Code edi')
    position = fields.Char(string='Position')
    value = fields.Char(string='Valeur')
    row = fields.Integer(string='Ligne')
    format = fields.Char(u'Format')


class ExcelReportEnginLine(models.Model):
        _name = "excel.report.engin.line"
        _description = "Report line Excel Formula"

        report_line_id = fields.Many2one('report.engin.line', 'Rapport', ondelete='cascade', readonly=True)
        cell = fields.Char('Cellule',related="report_line_id.cell")
        report_id = fields.Many2one('report.engin','Rapport',related="report_line_id.report_id")
        op = fields.Selection([
            ('plus', '+'),
            ('minus', '-'),
        ])


class partner_xlsx(models.AbstractModel):
    _inherit = "report.report_xlsx.partner_xlsx"
    def generate_xlsx_report(self, workbook, data, repports):
        engine_lines = self.env['report.engin.line'].search([])
        engine_lines.write({'cache_value': 0.0,'is_cached':False})
        for obj in repports:
            report_name = obj.name
            sheet = workbook.add_worksheet(report_name[:31])
            if obj.code_python:
                ex_n = self.env.context.get('ex_n', False)
                ex_n_1 = self.env.context.get('ex_n_1', False)
                localdict = {
                    'cr': self.env.cr,
                    'uid': self.env.uid,
                    'env': self.env,
                    'ex_n': ex_n,
                    'ex_n_1': ex_n_1,
                    'sheet': sheet,
                    'workbook': workbook,
                    'fields': fields,
                    'datetime': datetime,
                    'result': None,
                }
                safe_eval(obj.python, localdict, mode="exec", nocopy=True)
            else:
                for rc_line in obj.row_col_ids:
                    if rc_line.col_value:
                        sheet.set_column(rc_line.position, rc_line.position, int(rc_line.col_value))
                    if rc_line.row_value:
                        sheet.set_row(rc_line.position, int(rc_line.row_value))
                for line in obj.line_ids:
                        value = 0.0
                        field_list = []
                        if line.computation_mode == 'python':
                            ex_n = self.env.context.get('ex_n', False)
                            ex_n_1 = self.env.context.get('ex_n_1', False)
                            localdict = {
                                'cr': self.env.cr,
                                'uid': self.env.uid,
                                'env': self.env,
                                'ex_n': ex_n,
                                'ex_n_1': ex_n_1,
                                'sheet': sheet,
                                'workbook': workbook,
                                'fields': fields,
                                'datetime': datetime,
                                'result': None,
                            }
                            safe_eval(line.python, localdict, mode="exec", nocopy=True)
                        if line.computation_mode == 'manual':
                            value = line.value
                            if value.isdigit():
                                value = tools.float_round(float(value), precision_rounding=0.01)
                        if line.computation_mode == 'compute':
                            for formula in line.formulas_ids:
                                if not formula.formula_id.is_matrix:
                                    if not isinstance(formula.formula_id.eval_formula(formula.domain), float):
                                        value = formula.formula_id.eval_formula(formula.domain)
                                    else:
                                        op = 1
                                        if formula.op == 'minus':
                                            op=-1
                                        value += tools.float_round(formula.formula_id.eval_formula(formula.domain), precision_rounding=0.01) * op
                                else:
                                    value = formula.formula_id.eval_formula(formula.domain)
                                    field_list = eval(formula.formula_id.field_list)
                        if line.format:
                            format = ast.literal_eval(line.format)
                            if type(value) != list:
                                cell_format = workbook.add_format(format)
                                sheet.write(line.cell,value,cell_format)
                            else:
                                matrix = []
                                for elem in value:
                                    mat = []
                                    for field in field_list:
                                        mat.append(elem[field])
                                    matrix.append(mat)
                                cell_format = workbook.add_format(format)
                                (row, col) = xl_cell_to_rowcol(line.cell)
                                for data in (matrix):
                                    c = col
                                    for d in data:
                                        sheet.write(row, c, d,cell_format)
                                        c = c+1
                                    row += 1
                                for sum_cell in line.sum_ids:
                                    format_cell = workbook.add_format(format)
                                    if sum_cell.format:
                                        format_cell = workbook.add_format(format)
                                    if sum_cell.type == 'text':
                                        sheet.write(row+sum_cell.row, int(sum_cell.position), str(sum_cell.value), format_cell)
                                    if sum_cell.type == 'field':
                                        sum = 0.0
                                        for elem in value:
                                            if elem.get(sum_cell.value,False):
                                                sum += tools.float_round(float(elem[sum_cell.value]), precision_rounding=0.01)
                                        sheet.write(row+sum_cell.row, int(sum_cell.position), sum,format_cell)

                        else:
                            sheet.write(line.cell,line.value)
        return workbook
# partner_xlsx('report.report.engin.xlsx',
#              'report.engin')