# -*- coding: utf-8 -*-

from odoo import models, fields, api,tools
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError
import datetime


class FormulasEngine(models.Model):
    _name = "formulas.engine"
    _description = "Formulas engine"

    name = fields.Char('Nom', required=True)
    description = fields.Text('Description')
    computation_mode = fields.Selection([
        ('count', 'Nombre (count) / Matrice (matrice doit etre coche)'),
        ('sum', 'Somme (sum)'),
        ('python', 'Code Python'),
        ('sql', 'Requete SQL'),
    ],
        string="Mode de calcul",
        required=True)
    model_id = fields.Many2one('ir.model',
                               string='Objet')
    field_id = fields.Many2one('ir.model.fields', string='Champs a sommer')
    date_field_id = fields.Many2one('ir.model.fields', string='Champs date')
    exercice = fields.Selection([
        ('current', 'Exercice N'),
        ('previous', 'Exercice N-1'),
    ],
        string="Exercice fiscale")
    python_code = fields.Text('Code Python')
    sql_code = fields.Text('Code SQL')
    sql_date = fields.Char('Champs date')
    is_matrix = fields.Boolean('Table?')
    field_list = fields.Char('Liste des champs')
    # company_id = fields.Many2one('res.company', u'Société', default=lambda self: self.env.user.company_id, required=False)

    # @api.one
    def check_is_digit_field(self, field):
        self.ensure_one() # has been added
        field_obj = self.env['ir.model.fields']
        if self.check_field(field)[0]:
            field = field_obj.search([('name', '=', field), ('model_id', '=', self.model_id.id)])
            if field.ttype in ('float', 'integer'):
                return True
            else:
                return False

    # @api.one
    def check_field(self, field):
        self.ensure_one() # has been added
        field_obj = self.env['ir.model.fields']
        if self.field_list and (not self.computation_mode in ("python")):
            field = field_obj.search([('name', '=', field), ('model_id', '=', self.model_id.id)])
            if not field:
                return False
            else:
                return True

    # @api.one
    @api.constrains('field_list', 'model_id')
    def check_list_fields(self):
        self.ensure_one() # has been added
        if self.field_list and self.computation_mode in ('count', 'sum'):
            list_fields = self.field_list.replace('[', '').replace(']', '').replace("'", '').split(',')
            for field in list_fields:
                if not self.check_field(field)[0]:
                    raise ValidationError(u"Le champ %s n'existe pas pour le model %s" % (field, self.model_id.name))

    def eval_formula(self, domain):
        for rec in self:
            if rec.computation_mode == 'count':
                if rec.exercice:
                    if rec.exercice == 'current' and self.env.context.get('ex_n', False):
                        ex_n = self.env.context.get('ex_n', False)
                        domain = str(eval(domain))
                    if rec.exercice == 'previous' and self.env.context.get('ex_n_1', False):
                        ex_n_1 = self.env.context.get('ex_n_1', False)
                        domain = str(eval(domain))
                print(rec.eval_count(domain), "EVAL COUNT")
                return rec.eval_count(domain)
            if rec.computation_mode == 'sum':
                if rec.exercice and rec.date_field_id:
                    if rec.exercice == 'current' and self.env.context.get('ex_n', False):
                        fy_id = self.env['date.range'].browse(self.env.context.get('ex_n', False))
                        new_domain = [(rec.date_field_id.name, '>=', fy_id.date_start),
                                      (rec.date_field_id.name, '<=', fy_id.date_end)]
                        domain = str(eval(domain) + new_domain)
                    if rec.exercice == 'previous' and self.env.context.get('ex_n_1', False):
                        fy_id = self.env['date.range'].browse(self.env.context.get('ex_n_1', False))
                        new_domain = [(rec.date_field_id.name, '>=', fy_id.date_start),
                                      (rec.date_field_id.name, '<=', fy_id.date_end)]
                        domain = str(eval(domain) + new_domain)
                amount = tools.float_round(rec.eval_sum(domain), precision_rounding=0.01)
                return amount
            if rec.computation_mode == 'python':

                if rec.exercice:
                    if rec.exercice == 'current' and self.env.context.get('ex_n', False):
                        ex_n = self.env.context.get('ex_n', False)
                        domain = str(eval(domain))
                    if rec.exercice == 'previous' and self.env.context.get('ex_n_1', False):
                        ex_n_1 = self.env.context.get('ex_n_1', False)
                        domain = str(eval(domain))
                return rec.eval_python(domain)
            if rec.computation_mode == 'sql':
                amount = tools.float_round(rec.eval_sql(domain), precision_rounding=0.01)
                return amount

    def eval_sum(self, domain):
        self.ensure_one()
        obj = self.env[self.model_id.model]
        domain = safe_eval(domain)
        field_name = self.field_id.name
        res = obj.read_group(domain, [field_name], [])
        new_value = res and res[0][field_name] or 0.0
        return new_value

    def eval_count(self, domain):
        self.ensure_one()
        obj = self.env[self.model_id.model]
        domain = safe_eval(domain)
        if not self.is_matrix:
            res = obj.search_count(domain)
        else:
            res = obj.search_read(domain, eval(self.field_list))
        return res

    def eval_python(self, domain):
        self.ensure_one()
        code = self.python_code.strip()
        ex_n = self.env.context.get('ex_n', False)
        ex_n_1 = self.env.context.get('ex_n_1', False)
        domain = domain
        localdict = {
            'cr': self.env.cr,
            'uid': self.env.uid,
            'env': self.env,
            'ex_n': ex_n,
            'ex_n_1': ex_n_1,
            'domain': safe_eval(domain),
            'fields': fields,
            'datetime': datetime,
            'result': None,
        }
        safe_eval(code, localdict, mode="exec", nocopy=True)

        result = localdict.get('result') or 0.0
        return result

    def eval_sql(self, domain):
        self.ensure_one()
        sql = self.sql_code.strip()
        if self.exercice and self.sql_date and (
                    self.env.context.get('ex_n', False) or self.env.context.get('ex_n_1', False)):
            if self.exercice == 'current' and self.env.context.get('ex_n', False) and self.sql_date:
                fy_id = self.env['date.range'].browse(self.env.context.get('ex_n', False))
                new_where = " and %s >= % s and %s <= %s" % (
                    self.sql_date, "'%s'" % str(fy_id.date_start), self.sql_date, "'%s'" % str(fy_id.date_end))
                domain += new_where
                self.env.cr.execute(sql.replace('$where$', domain))
            if self.exercice == 'previous' and self.env.context.get('ex_n_1', False) and self.sql_date:
                fy_id = self.env['date.range'].browse(self.env.context.get('ex_n_1', False))
                new_where = " and %s >= % s and %s <= %s" % (
                    self.sql_date, "'%s'" % str(fy_id.date_start), self.sql_date, "'%s'" % str(fy_id.date_end))
                domain += new_where
                self.env.cr.execute(sql.replace('$where$', domain))
        else:
            self.env.cr.execute(sql.replace('$where$', domain))
        if not self.is_matrix:
            result = self.env.cr.fetchone()[0]
        else:
            result = self.env.cr.dictfetchall()
        return result
