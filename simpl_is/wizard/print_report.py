# -*- coding: utf-8 -*-

import datetime
import base64
import zipfile
import lxml
from lxml import etree
from openerp import models, api, fields , _
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval

import os
directory = os.path.dirname(__file__)

class PrintReport(models.TransientModel):
    """
    The class inherits the "LIASSE FISCALE" print report to add the simpl IS XML file.
    """

    _inherit = "report.engin.print"
    _description = "SIMPL IS"

    def generate_xml(self):
        """
        SIMPL IS XML file generation.

        Args:
            None.

        Returns:
            This function generate the simpl IS XML file.

        Raises:
            FY: Raises an exception if the FY has not a defined previous FY.
        """

        ex_n = self.fy_n_id.id
        if not self.fy_n_id.previous_fiscal_year:
            raise UserError(_(
                "Merci de préciser l'exercice précédent pour l'exercice choisi!"))
        ex_n_1 = self.fy_n_id.previous_fiscal_year.id
        self.with_context(ex_n=ex_n,ex_n_1=ex_n_1)

        engine_lines = self.env['report.engin.line'].search([])
        engine_lines.write({'cache_value' : 0.0, 'is_cached':False})

        for record in self:

            root = etree.Element("Liasse")
            modele =etree.SubElement(root, "modele")
            etree.SubElement(modele, "id").text = str(record.report_id.code_edi)
            resultatFiscal = etree.SubElement(root, "resultatFiscal")
            etree.SubElement(resultatFiscal, "identifiantFiscal").text=str(record.fy_n_id.company_id.partner_id.id_fisc)
            etree.SubElement(resultatFiscal, "exerciceFiscalDu").text=str(record.fy_n_id.date_start)
            etree.SubElement(resultatFiscal, "exerciceFiscalAu").text=str(record.fy_n_id.date_end)
            groupeValeursTableau = etree.SubElement(root,"groupeValeursTableau")

            table_dict = {}

            for table in record.report_id.rapport_ids:
                if table.report_id.code_edi:
                    groupeValeurs = False
                    extraFieldvaleurs = False
                    if table_dict.get(table.report_id.code_edi,False):
                        if table_dict.get(table.report_id.code_edi,False).get('value',False):
                            groupeValeurs = table_dict[table.report_id.code_edi]['value']
                        if table_dict.get(table.report_id.code_edi,False).get('extra',False):
                            extraFieldvaleurs = table_dict[table.report_id.code_edi]['extra']
                    if table.report_id.edi_python:

                        if not groupeValeurs:
                            ValeursTableau = etree.SubElement(groupeValeursTableau,"ValeursTableau")
                            tableau = etree.SubElement(ValeursTableau, "tableau")
                            etree.SubElement(tableau, "id").text = str(table.report_id.code_edi)
                        localdict = {
                            'cr': self.env.cr,
                            'uid': self.env.uid,
                            'env': self.env,
                            'ex_n': ex_n,
                            'ex_n_1': ex_n_1,
                            'groupeValeurs': groupeValeurs,
                            'etree':etree,
                            'fields': fields,
                            'datetime': datetime,
                            'result': None,
                        }
                        safe_eval(table.report_id.edi_python.name, localdict, mode="exec", nocopy=True)
                        for elem in localdict["result"][0]:
                            if localdict["result"][0][elem]:
                                if not groupeValeurs:
                                    groupeValeurs = etree.SubElement(ValeursTableau, "groupeValeurs")
                                ValeurCellule = etree.SubElement(groupeValeurs, "ValeurCellule")
                                Cellule = etree.SubElement(ValeurCellule, "cellule")
                                etree.SubElement(Cellule, "codeEdi").text = str(elem)
                                etree.SubElement(ValeurCellule, "valeur").text = str(localdict["result"][0][elem])
                        for tab_elem in localdict["result"][1]:
                            line = 1
                            for elem_line in tab_elem:
                                if not elem_line == 'line' and tab_elem[elem_line]:
                                    if not groupeValeurs:
                                        groupeValeurs = etree.SubElement(ValeursTableau, "groupeValeurs")
                                    ValeurCellule = etree.SubElement(groupeValeurs, "ValeurCellule")
                                    Cellule = etree.SubElement(ValeurCellule, "cellule")
                                    etree.SubElement(Cellule, "codeEdi").text = str(elem_line)
                                    if type(tab_elem[elem_line]).__name__ == 'unicode':
                                        etree.SubElement(ValeurCellule, "valeur").text = tab_elem[elem_line]
                                    else:
                                        etree.SubElement(ValeurCellule, "valeur").text = str(tab_elem[elem_line])
                                    print(tab_elem,"tab_elem")
                                    etree.SubElement(ValeurCellule, "numeroLigne").text = str(line)
                                    line += 1
                    else:
                        for line in table.report_id.line_ids:
                            if line.excel_formula_cells_ids and line.code_edi > 0 and not line.is_extra_field:
                                value = line.with_context(ex_n=ex_n, ex_n_1=ex_n_1).get_cell_value()[0]
                                if isinstance(value, int) or isinstance(value, float):
                                    if value:
                                        if not groupeValeurs:
                                            ValeursTableau = etree.SubElement(groupeValeursTableau, "ValeursTableau")
                                            tableau = etree.SubElement(ValeursTableau, "tableau")
                                            etree.SubElement(tableau, "id").text = str(table.report_id.code_edi)
                                            groupeValeurs = etree.SubElement(ValeursTableau, "groupeValeurs")
                                        ValeurCellule = etree.SubElement(groupeValeurs, "ValeurCellule")
                                        Cellule = etree.SubElement(ValeurCellule, "cellule")
                                        etree.SubElement(Cellule, "codeEdi").text = str(line.code_edi)
                                        etree.SubElement(ValeurCellule, "valeur").text = str(value)
                            if line.computation_mode == 'compute' and (not line.is_matrix) and line.code_edi > 0 and not line.is_extra_field:
                                value = line.with_context(ex_n=ex_n,ex_n_1=ex_n_1).get_cell_value()[0]
                                if isinstance(value, int) or isinstance(value, float):
                                    if value:
                                        if not groupeValeurs:
                                            ValeursTableau = etree.SubElement(groupeValeursTableau, "ValeursTableau")
                                            tableau = etree.SubElement(ValeursTableau, "tableau")
                                            etree.SubElement(tableau, "id").text = str(table.report_id.code_edi)
                                            groupeValeurs = etree.SubElement(ValeursTableau, "groupeValeurs")
                                        ValeurCellule= etree.SubElement(groupeValeurs,"ValeurCellule")
                                        Cellule= etree.SubElement(ValeurCellule,"cellule")
                                        etree.SubElement(Cellule,"codeEdi").text=str(line.code_edi)
                                        etree.SubElement(ValeurCellule, "valeur").text=str(value)
                            if line.computation_mode == 'compute' and line.is_matrix:
                                data_table = line.with_context(ex_n=ex_n,ex_n_1=ex_n_1).get_cell_value()[0]
                                numeroLigne = 1
                                code_edi_list = {}
                                second_code_edi_list = {}
                                if type(data_table) == type(list()):
                                    for edi_line in line.code_edi_ids:
                                        code_edi_list[edi_line.field] = edi_line.code_edi
                                        second_code_edi_list[edi_line.field] = edi_line.secend_code_edi
                                    for table_line in data_table:
                                        for elem in table_line:
                                            code_edi = 0
                                            if code_edi_list.get(elem, False):
                                                code_edi = code_edi_list[elem]
                                            if line.report_id.code_edi == 27 and table_line["type"] == "b" and second_code_edi_list.get(elem, False):
                                                code_edi = second_code_edi_list[elem]
                                            if code_edi > 0 and table_line[elem]:
                                                if not groupeValeurs:
                                                    ValeursTableau = etree.SubElement(groupeValeursTableau,
                                                                                      "ValeursTableau")
                                                    tableau = etree.SubElement(ValeursTableau, "tableau")
                                                    etree.SubElement(tableau, "id").text = str(table.report_id.code_edi)
                                                    groupeValeurs = etree.SubElement(ValeursTableau, "groupeValeurs")
                                                ValeurCellule = etree.SubElement(groupeValeurs, "ValeurCellule")
                                                Cellule = etree.SubElement(ValeurCellule, "cellule")
                                                etree.SubElement(Cellule, "codeEdi").text = str(code_edi)
                                                if type(table_line[elem]).__name__ == 'unicode':
                                                    etree.SubElement(ValeurCellule, "valeur").text = table_line[elem]
                                                else:
                                                    etree.SubElement(ValeurCellule, "valeur").text = str(table_line[elem])
                                                etree.SubElement(ValeurCellule, "numeroLigne").text = str(numeroLigne)
                                        numeroLigne += 1
                                    for sum_cell in line.sum_ids:
                                        if sum_cell.type == 'field' and sum_cell.code_edi > 0:
                                            value = str(line.with_context(ex_n=ex_n,ex_n_1=ex_n_1).get_cell_sum_value(sum_cell.value)[0])
                                            if value:
                                                if not groupeValeurs:
                                                    ValeursTableau = etree.SubElement(groupeValeursTableau,
                                                                                      "ValeursTableau")
                                                    tableau = etree.SubElement(ValeursTableau, "tableau")
                                                    etree.SubElement(tableau, "id").text = str(table.report_id.code_edi)
                                                    groupeValeurs = etree.SubElement(ValeursTableau, "groupeValeurs")
                                                ValeurCellule = etree.SubElement(groupeValeurs, "ValeurCellule")
                                                Cellule = etree.SubElement(ValeurCellule, "cellule")
                                                etree.SubElement(Cellule, "codeEdi").text = str(sum_cell.code_edi)
                                                etree.SubElement(ValeurCellule, "valeur").text = value
                            if line.is_extra_field:
                                extra_value = str(line.with_context(ex_n=ex_n,ex_n_1=ex_n_1).get_cell_value()[0])
                                if line.code_edi > 0 and extra_value:
                                    if not extraFieldvaleurs:
                                        if not groupeValeurs:
                                            ValeursTableau = etree.SubElement(groupeValeursTableau, "ValeursTableau")
                                            tableau = etree.SubElement(ValeursTableau, "tableau")
                                            etree.SubElement(tableau, "id").text = str(table.report_id.code_edi)
                                            extraFieldvaleurs = etree.SubElement(ValeursTableau, "extraFieldvaleurs")
                                        else:
                                            extraFieldvaleurs = etree.SubElement(ValeursTableau, "extraFieldvaleurs")
                                    ExtraFieldValeur = etree.SubElement(extraFieldvaleurs, "ExtraFieldValeur")
                                    extraField  = etree.SubElement(ExtraFieldValeur, "extraField")
                                    etree.SubElement(extraField, "code").text = str(line.code_edi)
                                    etree.SubElement(ExtraFieldValeur, "valeur").text = extra_value
                    if not table_dict.get(table.report_id.code_edi, False):
                        table_dict[table.report_id.code_edi] = {'value': groupeValeurs, 'extra': extraFieldvaleurs}
            tree = etree.ElementTree(root)

            for valTab in root.iter('ValeursTableau'):
                if len(valTab.findall('groupeValeurs')) < 1:
                    valTab.getparent().remove(valTab)
                else:
                    if len(valTab.findall('extraFieldvaleurs')) < 1:
                        valTab.append(lxml.etree.XML("<extraFieldvaleurs></extraFieldvaleurs>"))
            file = open(os.path.join(directory, 'simple_is.xml'), 'w')
            file.write((etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")).decode("utf-8"))
            file.close()
            zf = zipfile.ZipFile(os.path.join(directory, 'simple_is.zip'), mode='w')
            try:
                zf.write(os.path.join(directory, 'simple_is.xml'), arcname='simple_is.xml')
            finally:
                zf.close()
            xml_file = base64.encodestring(open(os.path.join(directory, 'simple_is.zip'), 'rb').read())

            filename = record.env.user.company_id.name
            extension = 'zip'
            name = "%s.%s" % (filename, extension)
            record.write({'xml_file': xml_file, 'name': name})

            os.remove(os.path.join(directory, 'simple_is.zip'))
            os.remove(os.path.join(directory, 'simple_is.xml'))

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'report.engin.print',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': record.id,
                'views': [(False, 'form')],
                'target': 'new',
            }

