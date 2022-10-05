# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, api, fields, _
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class financial_xlsx(models.AbstractModel):
    _name = 'report.financial.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, repports):
        all_partners, lst_account = [], []
        repports.onchange_date_search()
        cr = self.env.cr
        company = repports.company_id
        sheet = workbook.add_worksheet('Financial report')
        bold = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'bold': True})
        title = workbook.add_format({'bold': True, 'bg_color': 'gray'})
        body = workbook.add_format()
        number = workbook.add_format()
        number.set_num_format('# ##0.00')
        number_somme = workbook.add_format({'bold': True, 'bg_color': 'gray'})
        number_somme.set_num_format('# ##0.00')
        if repports.account_ids:
            account_ids = repports.account_ids

        else:
            account_ids = self.env['account.account'].search([])
        if repports.partner_ids:
            all_partners = repports.partner_ids.mapped('id')

        else:
            cr.execute(
                "SELECT distinct partner_id FROM account_move_line as l "
                "INNER JOIN account_account a on a.id = l.account_id "
                "where l.date <= %s  and l.date >= %s   AND (a.code LIKE '3421%%' OR a.code LIKE '4411%%')"
                " AND a.company_id = %s",
                (repports.date_to, repports.date_from, company.id))
            partner_ids = cr.fetchall()
            for partner in partner_ids:
                all_partners.append(partner[0])
        cr = self.env.cr
        if repports.target_report == 'gl':
            sheet.write(0, 0, 'Grand livre', bold)
            sheet.write(0, 5, company.name, bold)
            sheet.write(2, 3, 'Du  :', bold)
            sheet.write(2, 4, repports.date_from, date_format)
            sheet.write(2, 5, 'Au  :', bold)
            sheet.write(2, 6, repports.date_to, date_format)
            # sheet.write(2, 6, datetime.strftime(repports.date_to, DF), bold)
            if repports.target_accounts == 'partners':
                sheet.set_column(0, 0, 10)
                sheet.set_column(1, 1, 15)
                sheet.set_column(2, 2, 25)
                sheet.set_column(3, 3, 7)
                sheet.set_column(4, 4, 30)
                sheet.set_column(5, 5, 15)
                sheet.set_column(6, 6, 7)
                sheet.set_column(7, 7, 13)
                sheet.set_column(8, 8, 13)
                sheet.set_column(9, 9, 13)
                row = 5
                sheet.write(row, 0, 'Partenaire', title)
                sheet.write(row, 1, 'Code compte', title)
                sheet.write(row, 2, u'Libellé compte', title)
                sheet.write(row, 3, 'Journal', title)
                sheet.write(row, 4, u'Libellé', title)
                sheet.write(row, 5, 'Date', title)
                sheet.write(row, 6, u'Pièce comptable', title)
                sheet.write(row, 7, u'Équivalent', title)
                sheet.write(row, 8, u'Débit', title)
                sheet.write(row, 9, u'Crédit', title)
                sheet.write(row, 10, u'Cumul', title)
                row = 6
                for partner_id in self.env['res.partner'].browse(all_partners):
                    movelines_query = "SELECT a.code AS codecompte, a.name AS libcompte, j.code AS journal," \
                                      " l.date AS date, m.id AS piece, l.ref AS libelle, l.debit AS debit," \
                                      " l.credit AS credit, l.full_reconcile_id as equivalent," \
                                      " m.name as move FROM account_move_line as l " \
                                      "INNER JOIN account_move m on m.id = l.move_id " \
                                      "INNER JOIN account_account a on a.id = l.account_id " \
                                      "INNER JOIN res_partner r on r.id = l.partner_id " \
                                      "INNER JOIN account_journal j on j.id = l.journal_id " \
                                      "WHERE j.type != 'situation' AND l.date <= %s  " \
                                      "AND l.date >= %s  AND r.id = %s AND (a.code LIKE '3421%%' OR a.code LIKE '4411%%')" \
                                      "AND a.company_id = %s"
                    if repports.target_move == 'posted':
                        movelines_query += " AND  m.state = 'posted'"
                    if repports.customers and repports.suppliers:
                        movelines_query += " AND  a.internal_type in ('receivable', 'payable') "
                    elif repports.customers:
                        movelines_query += " AND  a.internal_type = 'receivable' "
                    elif repports.suppliers:
                        movelines_query += " AND  a.internal_type = 'payable' "

                    cr.execute(movelines_query, (repports.date_to, repports.date_from, partner_id.id, company.id))
                    movelines = cr.fetchall()
                    an_query = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                               "FROM account_move_line as l INNER JOIN account_move m on m.id = l.move_id " \
                               "INNER JOIN account_account a on a.id = l.account_id " \
                               "INNER JOIN res_partner r on r.id = l.partner_id " \
                               "INNER JOIN account_journal j on j.id = l.journal_id " \
                               "WHERE j.type = 'situation' AND l.date = %s AND r.id = %s " \
                               "AND (a.code LIKE '3421%%' OR a.code LIKE '4411%%')" \
                               "AND a.company_id = %s"
                    if repports.target_move == 'posted':
                        an_query += " AND  m.state = 'posted'"
                    if repports.customers and repports.suppliers:
                        an_query += " AND  a.internal_type in ('receivable', 'payable') "
                    elif repports.customers:
                        an_query += " AND  a.internal_type = 'receivable' "
                    elif repports.suppliers:
                        an_query += " AND  a.internal_type = 'payable' "
                    cr.execute(an_query, (repports.date_range_exercice_id.date_start, partner_id.id, company.id))
                    an = cr.fetchall()
                    solde_query = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                                  "FROM account_move_line as l INNER JOIN account_move m on m.id = l.move_id " \
                                  "INNER JOIN account_account a on a.id = l.account_id " \
                                  "INNER JOIN res_partner r on r.id = l.partner_id " \
                                  "INNER JOIN account_journal j on j.id = l.journal_id " \
                                  "WHERE j.type != 'situation'AND l.date <= %s " \
                                  "AND l.date >= %s AND r.id = %s AND (a.code LIKE '3421%%' OR a.code LIKE '4411%%')" \
                                  "AND a.company_id = %s"
                    if repports.target_move == 'posted':
                        solde_query += " AND  m.state = 'posted'"
                    if repports.customers and repports.suppliers:
                        solde_query += " AND  a.internal_type in ('receivable', 'payable') "
                    elif repports.customers:
                        solde_query += " AND  a.internal_type = 'receivable' "
                    elif repports.suppliers:
                        solde_query += " AND  a.internal_type = 'payable' "
                    cr.execute(solde_query, (repports.date_to, repports.date_from, partner_id.id, company.id))
                    solde = cr.fetchall()
                    # ne pas afficher les comptes sans aucun mouvement
                    if not an[0][0] and not an[0][1] and not movelines:
                        continue

                    debit_anv = an[0][0] and an[0][0] or 0
                    credit_anv = an[0][1] and an[0][1] or 0
                    solde_anv = debit_anv - credit_anv

                    sheet.write(row, 0, partner_id.name, body)
                    sheet.write(row, 4, 'AN', body)
                    sheet.write(row, 8, debit_anv, number)
                    sheet.write(row, 9, credit_anv, number)
                    sheet.write(row, 10, solde_anv, number)
                    row += 1
                    # le detail des mouvements des comptes dans le Grand Livre
                    cumul = solde_anv
                    for MoveLine in movelines:
                        date = MoveLine[3]
                        # piece = MoveLine[8]
                        piece = MoveLine[9]
                        equivalent = self.env['account.full.reconcile'].browse(MoveLine[8])
                        journal = MoveLine[2]
                        libelle = MoveLine[5]
                        compte_code = MoveLine[0]
                        compte_libelle = MoveLine[1]
                        debit = MoveLine[6] or 0.0
                        credit = MoveLine[7] or 0.0
                        cumul += debit - credit
                        sheet.write(row, 1, compte_code, body)
                        sheet.write(row, 2, compte_libelle, body)
                        sheet.write(row, 3, journal, body)
                        sheet.write(row, 4, libelle, body)
                        sheet.write(row, 5, date, date_format)
                        sheet.write(row, 6, piece, body)
                        sheet.write(row, 7, equivalent.name if equivalent else '', body)
                        sheet.write(row, 8, debit, number)
                        sheet.write(row, 9, credit, number)
                        sheet.write(row, 10, cumul, number)
                        row += 1
                    an_debit = an[0][0] and an[0][0] or 0
                    an_credit = an[0][1] and an[0][1] or 0
                    somme_debit = an_debit + (solde[0][0] and solde[0][0] or 0)
                    somme_credit = an_credit + (solde[0][1] and solde[0][1] or 0)
                    sheet.write(row, 7, 'Total :', title)
                    sheet.write(row, 8, somme_debit, number_somme)
                    sheet.write(row, 9, somme_credit, number_somme)

                    row += 1

                    if somme_debit >= somme_credit:
                        sheet.write(row, 7, 'Solde :', title)
                        sheet.write(row, 8, somme_debit - somme_credit, number_somme)
                        sheet.write(row, 9, 0, number_somme)
                    else:
                        sheet.write(row, 7, 'Solde :', title)
                        sheet.write(row, 8, 0, number_somme)
                        sheet.write(row, 9, somme_credit - somme_debit, number_somme)
                    row += 1
                # sheet.write_formula(row, 1, '=SUM(B7:B' + str(row) + ')', title)
                # sheet.write_formula(row, 2, "=SUM(C7:C" + str(row) + ")", title)
                # sheet.write_formula(row, 3, "=SUM(D7:D" + str(row) + ")", title)
                # sheet.write_formula(row, 4, "=SUM(E7:E" + str(row) + ")", title)
                # sheet.write_formula(row, 5, "=SUM(F7:F" + str(row) + ")", title)
                # sheet.write_formula(row, 6, "=SUM(G7:G" + str(row) + ")", title)
            else:
                sheet.set_column(0, 0, 15)
                sheet.set_column(1, 1, 25)
                sheet.set_column(2, 2, 7)
                sheet.set_column(3, 3, 30)
                sheet.set_column(4, 4, 15)
                sheet.set_column(5, 5, 7)
                sheet.set_column(6, 6, 13)
                sheet.set_column(7, 7, 13)
                sheet.set_column(8, 8, 13)
                row = 5
                sheet.write(row, 0, 'Code compte', title)
                sheet.write(row, 1, 'Libelle compte', title)
                sheet.write(row, 2, 'Partenaire', title)
                sheet.write(row, 3, 'Journal', title)
                sheet.write(row, 4, 'Libelle', title)
                sheet.write(row, 5, 'Date', title)
                sheet.write(row, 6, u'Pièce comptable', title)
                sheet.write(row, 7, u'Débit', title)
                sheet.write(row, 8, u'Crédit', title)
                sheet.write(row, 9, 'Cumul', title)
                row = 6
                for account_id in account_ids:
                    movelines_query = "SELECT a.code AS codecompte, a.name AS libcompte, j.code AS journal,  " \
                                      "l.date AS date, m.id AS piece, l.ref AS libelle, l.debit AS debit," \
                                      " l.credit AS credit, m.name as move, " \
                                      "p.name as partner " \
                                      "FROM account_move_line as l " \
                                      "INNER JOIN account_move m on m.id = l.move_id " \
                                      "INNER JOIN account_account a on a.id = l.account_id " \
                                      "INNER JOIN account_journal j on j.id = l.journal_id " \
                                      "LEFT JOIN res_partner p on p.id = l.partner_id " \
                                      "WHERE j.type != 'situation' AND l.date <= %s  AND l.date >= %s  AND a.id = %s" \
                                      "AND a.company_id = %s"

                    if repports.target_move == 'posted':
                        movelines_query += " AND  m.state = 'posted'"
                    movelines_query += "ORDER BY l.date"
                    cr.execute(movelines_query, (repports.date_to, repports.date_from, account_id.id, company.id))
                    movelines = cr.fetchall()
                    if repports.date_from != repports.date_range_exercice_id.date_start:
                        movelines_cheval_query = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                                                 "FROM account_move_line as l " \
                                                 "INNER JOIN account_move m on m.id = l.move_id " \
                                                 "INNER JOIN account_account a on a.id = l.account_id " \
                                                 "INNER JOIN account_journal j on j.id = l.journal_id " \
                                                 "WHERE j.type != 'situation' AND l.date < %s  AND l.date >= %s  AND a.id = %s" \
                                                 "AND a.company_id = %s"
                        if repports.target_move == 'posted':
                            movelines_cheval_query += " AND  m.state = 'posted'"
                        cr.execute(movelines_cheval_query, (
                        repports.date_from, repports.date_range_exercice_id.date_start, account_id.id, company.id))
                        movelines_cheval = cr.fetchall()
                    # ANV
                    cr.execute(
                        "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit "
                        "FROM account_move_line as l "
                        "INNER JOIN account_move m on m.id = l.move_id "
                        "INNER JOIN account_account a on a.id = l.account_id "
                        "INNER JOIN account_journal j on j.id = l.journal_id "
                        "WHERE j.type = 'situation' AND l.date = %s AND a.id = %s"
                        "AND a.company_id = %s",
                        (repports.date_range_exercice_id.date_start, account_id.id, company.id))
                    an = cr.fetchall()
                    # SOlde
                    sold_query = """SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit 
                        FROM account_move_line as l 
                        INNER JOIN account_move m on m.id = l.move_id 
                        INNER JOIN account_account a on a.id = l.account_id 
                        INNER JOIN account_journal j on j.id = l.journal_id 
                        WHERE j.type != 'situation'AND l.date <= %s AND l.date >= %s AND a.id = %s
                        AND a.company_id = %s"""
                    if repports.target_move == 'posted':
                        sold_query += " AND  m.state = 'posted'"

                    cr.execute(sold_query, (repports.date_to, repports.date_from, account_id.id, company.id))
                    solde = cr.fetchall()

                    # ne pas afficher les comptes sans aucun mouvement
                    if not an[0][0] and not an[0][1] and not movelines:
                        continue

                    anv_debit = an[0][0] and an[0][0] or 0
                    anv_credit = an[0][1] and an[0][1] or 0
                    if repports.date_from != repports.date_range_exercice_id.date_start:
                        anv_debit = anv_debit + (movelines_cheval and movelines_cheval[0][0] or 0)
                        anv_credit = anv_credit + (movelines_cheval and movelines_cheval[0][1] or 0)
                    anv_solde = anv_debit - anv_credit

                    sheet.write(row, 0, account_id.code, body)
                    sheet.write(row, 1, account_id.name, body)
                    sheet.write(row, 3, 'AN', body)
                    sheet.write(row, 7, anv_debit, number)
                    sheet.write(row, 8, anv_credit, number)
                    sheet.write(row, 9, anv_solde or 0, number)
                    row += 1

                    cumul = anv_solde

                    for MoveLine in movelines:
                        date = MoveLine[3]
                        piece = MoveLine[8]
                        journal = MoveLine[2]
                        libelle = MoveLine[5]
                        compte_code = MoveLine[0]
                        compte_libelle = MoveLine[1]
                        partner = MoveLine[9] or ''

                        debit = MoveLine[6] or 0.0
                        credit = MoveLine[7] or 0.0
                        cumul += debit - credit
                        sheet.write(row, 0, compte_code, body)
                        sheet.write(row, 1, compte_libelle, body)
                        sheet.write(row, 2, partner, body)
                        sheet.write(row, 3, journal, body)
                        sheet.write(row, 4, libelle, body)
                        sheet.write(row, 5, date, date_format)
                        sheet.write(row, 6, piece, body)
                        sheet.write(row, 7, debit, number)
                        sheet.write(row, 8, credit, number)
                        sheet.write(row, 9, cumul, number)
                        row += 1

                    somme_debit = anv_debit + (solde[0][0] and solde[0][0] or 0)
                    somme_credit = anv_credit + (solde[0][1] and solde[0][1] or 0)
                    sheet.write(row, 6, 'Total :', title)
                    sheet.write(row, 7, somme_debit, number_somme)
                    sheet.write(row, 8, somme_credit, number_somme)
                    row += 1
                    if somme_debit >= somme_credit:
                        sheet.write(row, 6, 'Solde :', title)
                        sheet.write(row, 7, somme_debit - somme_credit, number_somme)
                        sheet.write(row, 8, 0, number_somme)
                    else:
                        sheet.write(row, 6, 'Solde :', title)
                        sheet.write(row, 7, 0, number_somme)
                        sheet.write(row, 8, somme_credit - somme_debit, number_somme)
                    row += 1
        # Balance
        else:
            sheet.write(0, 0, 'Balance', bold)
            sheet.write(0, 5, company.name, bold)
            sheet.write(2, 3, 'Du  :', bold)
            sheet.write(2, 4, repports.date_from, date_format)
            sheet.write(2, 5, 'Au  :', bold)
            sheet.write(2, 6, repports.date_to, date_format)
            if repports.target_accounts == 'partners':
                sheet.set_column(0, 0, 13)
                sheet.set_column(1, 1, 13)
                sheet.set_column(2, 2, 13)
                sheet.set_column(3, 3, 13)
                sheet.set_column(4, 4, 13)
                sheet.set_column(5, 5, 13)
                sheet.set_column(6, 6, 13)
                row = 5
                sheet.write(row, 0, u'Partenaire', title)
                sheet.write(row, 1, u'Débit initial', title)
                sheet.write(row, 2, u'Crédit initial', title)
                sheet.write(row, 3, u'Débit', title)
                sheet.write(row, 4, u'Crédit', title)
                sheet.write(row, 5, u'Débit final', title)
                sheet.write(row, 6, u'Crédit final', title)
                row = 6
                for partner_id in self.env['res.partner'].browse(all_partners):
                    movelines_query = "SELECT a.code AS codecompte, a.name AS libcompte, j.code AS journal, l.date AS date," \
                                      "l.ref AS libelle, l.debit AS debit, l.credit AS credit " \
                                      "FROM account_move_line as l INNER JOIN account_move m on m.id = l.move_id " \
                                      " INNER JOIN account_account a on a.id = l.account_id " \
                                      "INNER JOIN " \
                                      "res_partner r on r.id = l.partner_id " \
                                      "INNER JOIN account_journal j on j.id = l.journal_id " \
                                      "WHERE j.type != 'situation'AND l.date <= %s  AND l.date >= %s  " \
                                      "AND r.id = %s " \
                                      "AND a.company_id = %s"
                    if repports.target_move == 'posted':
                        movelines_query += " AND  m.state = 'posted'"
                    if repports.customers and repports.suppliers:
                        movelines_query += " AND  a.internal_type in ('receivable', 'payable') "
                    elif repports.customers:
                        movelines_query += " AND  a.internal_type = 'receivable' "
                    elif repports.suppliers:
                        movelines_query += " AND  a.internal_type = 'payable' "
                    cr.execute(movelines_query, (repports.date_to, repports.date_from, partner_id.id, company.id))
                    movelines = cr.fetchall()
                    an_query = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                               "FROM account_move_line as l INNER JOIN account_move m on m.id = l.move_id " \
                               "INNER JOIN account_account a on a.id = l.account_id " \
                               "INNER JOIN res_partner r on r.id = l.partner_id " \
                               "INNER JOIN account_journal j on j.id = l.journal_id " \
                               "WHERE j.type = 'situation' AND l.date = %s AND r.id = %s " \
                               "AND a.company_id = %s"
                    # "AND (a.code LIKE '3421%%' OR a.code LIKE '4411%%')" \
                    #            "AND a.company_id = %s"

                    if repports.target_move == 'posted':
                        an_query += " AND  m.state = 'posted'"
                    if repports.customers and repports.suppliers:
                        an_query += " AND  a.internal_type in ('receivable', 'payable') "
                    elif repports.customers:
                        an_query += " AND  a.internal_type = 'receivable' "
                    elif repports.suppliers:
                        an_query += " AND  a.internal_type = 'payable' "
                    cr.execute(an_query, (repports.date_range_exercice_id.date_start, partner_id.id, company.id))
                    an = cr.fetchall()
                    solde_query = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                                  "FROM account_move_line as l " \
                                  "INNER JOIN account_move m on m.id = l.move_id " \
                                  "INNER JOIN account_account a on a.id = l.account_id " \
                                  "INNER JOIN res_partner r on r.id = l.partner_id " \
                                  "INNER JOIN account_journal j on j.id = l.journal_id " \
                                  "WHERE j.type != 'situation'AND l.date <= %s AND l.date >= %s " \
                                  "AND r.id = %s " \
                                  "AND a.company_id = %s"
                    # "AND r.id = %s AND (a.code LIKE '3421%%' OR a.code LIKE '4411%%')" \
                    #               "AND a.company_id = %s"
                    #
                    if repports.target_move == 'posted':
                        solde_query += " AND  m.state = 'posted'"
                    if repports.customers and repports.suppliers:
                        solde_query += " AND  a.internal_type in ('receivable', 'payable') "
                    elif repports.customers:
                        solde_query += " AND  a.internal_type = 'receivable' "
                    elif repports.suppliers:
                        solde_query += " AND  a.internal_type = 'payable' "
                    cr.execute(solde_query, (repports.date_to, repports.date_from, partner_id.id, company.id))
                    solde = cr.fetchall()

                    # ne pas afficher les comptes sans aucun mouvement
                    if not an[0][0] and not an[0][1] and not movelines:
                        continue
                    an_debit = an[0][0] and an[0][0] or 0
                    an_credit = an[0][1] and an[0][1] or 0
                    somme_debit = solde[0][0] and solde[0][0] or 0
                    somme_credit = solde[0][1] and solde[0][1] or 0

                    sheet.write(row, 0, partner_id.name, number)
                    sheet.write(row, 1, an_debit, number)
                    sheet.write(row, 2, an_credit, number)
                    sheet.write(row, 3, somme_debit, number)
                    sheet.write(row, 4, somme_credit, number)
                    sheet.write(row, 5,
                                somme_debit + an_debit - somme_credit - an_credit if somme_debit + an_debit > somme_credit + an_credit else 0,
                                number)
                    sheet.write(row, 6,
                                -somme_debit - an_debit + somme_credit + an_credit if somme_debit + an_debit < somme_credit + an_credit else 0,
                                number)

                    row += 1
            else:
                sheet.set_column(0, 0, 15)
                sheet.set_column(1, 1, 25)
                sheet.set_column(2, 2, 13)
                sheet.set_column(3, 3, 13)
                sheet.set_column(4, 4, 13)
                sheet.set_column(5, 5, 13)
                sheet.set_column(6, 6, 13)
                sheet.set_column(7, 7, 13)
                row = 5
                sheet.write(row, 0, 'Code compte', title)
                sheet.write(row, 1, u'Libellé Compte', title)
                if repports.partenaire_detail:
                    sheet.write(row, 1, u'Libellé Compte/ partenaire', title)
                sheet.write(row, 2, u'Débit initial', title)
                sheet.write(row, 3, u'Crédit initial', title)
                sheet.write(row, 4, u'Débit', title)
                sheet.write(row, 5, u'Crédit', title)
                sheet.write(row, 6, u'Débit final', title)
                sheet.write(row, 7, u'Crédit final', title)
                row = 6
                for account_id in account_ids:
                    movelines_req = "SELECT a.code AS codecompte, a.name AS libcompte, j.code AS journal, l.date AS date," \
                                    " l.ref AS libelle, l.debit AS debit, l.credit AS credit " \
                                    "FROM account_move_line as l " \
                                    "INNER JOIN account_move m on m.id = l.move_id " \
                                    "INNER JOIN account_journal j on j.id = l.journal_id " \
                                    "INNER JOIN account_account a on a.id = l.account_id " \
                                    "WHERE j.type != 'situation' AND l.date <= %s  AND l.date >= %s  AND l.account_id = %s" \
                                    "AND a.company_id = %s"

                    if repports.target_move == 'posted':
                        movelines_req += " AND m.state = 'posted'"
                    cr.execute(movelines_req,
                               (repports.date_to, repports.date_from, account_id.id, company.id))
                    movelines = cr.fetchall()
                    an_req = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                             "FROM account_move_line as l INNER JOIN account_move m on m.id = l.move_id " \
                             "INNER JOIN account_journal j on j.id = l.journal_id " \
                             "INNER JOIN account_account a on a.id = l.account_id " \
                             "WHERE j.type = 'situation' AND l.date = %s AND a.id = %s" \
                             "AND a.company_id = %s"
                    if repports.target_move == 'posted':
                        an_req += " AND m.state = 'posted'"

                    cr.execute(an_req,
                               (repports.date_range_exercice_id.date_start, account_id.id, company.id))
                    an = cr.fetchall()
                    solde_req = "SELECT SUM(l.debit) AS debit, SUM(l.credit) AS credit" \
                                " FROM account_move_line as l " \
                                "INNER JOIN account_move m on m.id = l.move_id " \
                                "INNER JOIN account_journal j on j.id = l.journal_id " \
                                "INNER JOIN account_account a on a.id = l.account_id " \
                                "WHERE j.type != 'situation'AND l.date <= %s AND l.date >= %s AND l.account_id = %s" \
                                "AND a.company_id = %s"
                    if repports.target_move == 'posted':
                        solde_req += " AND m.state = 'posted'"
                    cr.execute(solde_req,
                               (repports.date_to, repports.date_from, account_id.id, company.id))
                    solde = cr.fetchall()

                    if not an[0][0] and not an[0][1] and not movelines:
                        continue
                    an_debit = an[0][0] and an[0][0] or 0
                    an_credit = an[0][1] and an[0][1] or 0
                    somme_debit = solde[0][0] and solde[0][0] or 0
                    somme_credit = solde[0][1] and solde[0][1] or 0

                    sheet.write(row, 0, account_id.code, body)
                    sheet.write(row, 1, account_id.name, body)
                    sheet.write(row, 2, an_debit, number)
                    sheet.write(row, 3, an_credit, number)
                    sheet.write(row, 4, somme_debit, number)
                    sheet.write(row, 5, somme_credit, number)
                    sheet.write(row, 6,
                                somme_debit + an_debit - somme_credit - an_credit if somme_debit + an_debit > somme_credit + an_credit else 0,
                                number)
                    sheet.write(row, 7,
                                -somme_debit - an_debit + somme_credit + an_credit if somme_debit + an_debit < somme_credit + an_credit else 0,
                                number)
                    row += 1
                    if repports.partenaire_detail:
                        if account_id.internal_type in ('receivable', 'payable'):
                            accounts_partners = []
                            cr.execute(
                                "SELECT distinct partner_id FROM account_move_line as l "
                                "INNER JOIN account_account a on a.id = l.account_id "
                                " where a.id = %s "
                                " and a.company_id = %s", (account_id.id, company.id,))
                            accounts_partners_ids = cr.fetchall()
                            for partner in accounts_partners_ids:
                                accounts_partners.append(partner[0])
                            if None in accounts_partners:
                                movelines_query = "SELECT a.code AS codecompte, a.name AS libcompte, j.code AS journal, l.date AS date," \
                                                  "l.ref AS libelle, l.debit AS debit, l.credit AS credit " \
                                                  "FROM account_move_line as l " \
                                                  "INNER JOIN account_move m on m.id = l.move_id " \
                                                  " INNER JOIN " \
                                                  "account_account a on a.id = l.account_id " \
                                                  "INNER JOIN account_journal j on j.id = l.journal_id " \
                                                  "WHERE j.type != 'situation' AND l.date <= %s  AND l.date >= %s  " \
                                                  "AND l.partner_id is null AND a.id = %s " \
                                                  "AND a.company_id = %s"
                                if repports.target_move == 'posted':
                                    movelines_query += " AND  m.state = 'posted'"
                                cr.execute(movelines_query,
                                           (
                                               repports.date_to, repports.date_from, account_id.id,
                                               company.id))
                                movelines = cr.fetchall()
                                an_query = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                                           "FROM account_move_line as l INNER JOIN account_move m on m.id = l.move_id " \
                                           "INNER JOIN account_account a on a.id = l.account_id " \
                                           "INNER JOIN account_journal j on j.id = l.journal_id " \
                                           "WHERE j.type = 'situation' AND l.date = %s AND l.partner_id is null " \
                                           "AND a.id = %s " \
                                           "AND a.company_id = %s"
                                if repports.target_move == 'posted':
                                    an_query += " AND  m.state = 'posted'"
                                cr.execute(an_query,
                                           (repports.date_range_exercice_id.date_start, account_id.id,
                                            company.id))
                                an = cr.fetchall()
                                solde_query = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                                              "FROM account_move_line as l " \
                                              "INNER JOIN account_move m on m.id = l.move_id " \
                                              "INNER JOIN account_account a on a.id = l.account_id " \
                                              "INNER JOIN account_journal j on j.id = l.journal_id " \
                                              "WHERE j.type != 'situation'AND l.date <= %s AND l.date >= %s " \
                                              "AND l.partner_id is null AND a.id = %s " \
                                              "AND a.company_id = %s"
                                if repports.target_move == 'posted':
                                    solde_query += " AND  m.state = 'posted'"
                                cr.execute(solde_query, (
                                    repports.date_to, repports.date_from, account_id.id, company.id))
                                solde = cr.fetchall()

                                # ne pas afficher les comptes sans aucun mouvement
                                if not an[0][0] and not an[0][1] and not movelines:
                                    continue
                                an_debit = an[0][0] and an[0][0] or 0
                                an_credit = an[0][1] and an[0][1] or 0
                                somme_debit = solde[0][0] and solde[0][0] or 0
                                somme_credit = solde[0][1] and solde[0][1] or 0
                                sheet.write(row, 1,  'Indéfini', number)
                                sheet.write(row, 2, an_debit, number)
                                sheet.write(row, 3, an_credit, number)
                                sheet.write(row, 4, somme_debit, number)
                                sheet.write(row, 5, somme_credit, number)
                                sheet.write(row, 6,
                                            somme_debit + an_debit - somme_credit - an_credit if somme_debit + an_debit > somme_credit + an_credit else 0,
                                            number)
                                sheet.write(row, 7,
                                            -somme_debit - an_debit + somme_credit + an_credit if somme_debit + an_debit < somme_credit + an_credit else 0,
                                            number)

                                row += 1

                            for partner_id in accounts_partners:

                                movelines_query = "SELECT a.code AS codecompte, a.name AS libcompte, j.code AS journal, l.date AS date," \
                                                  "l.ref AS libelle, l.debit AS debit, l.credit AS credit " \
                                                  "FROM account_move_line as l " \
                                                  "INNER JOIN account_move m on m.id = l.move_id " \
                                                  " INNER JOIN " \
                                                  "account_account a on a.id = l.account_id " \
                                                  "INNER JOIN " \
                                                  "res_partner r on r.id = l.partner_id " \
                                                  "INNER JOIN account_journal j on j.id = l.journal_id " \
                                                  "WHERE j.type != 'situation'AND l.date <= %s  AND l.date >= %s  " \
                                                  "AND r.id = %s AND a.id = %s " \
                                                  "AND a.company_id = %s"
                                if repports.target_move == 'posted':
                                    movelines_query += " AND  m.state = 'posted'"
                                cr.execute(movelines_query,
                                           (
                                           repports.date_to, repports.date_from, partner_id, account_id.id, company.id))
                                movelines = cr.fetchall()
                                an_query = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                                           "FROM account_move_line as l INNER JOIN account_move m on m.id = l.move_id " \
                                           "INNER JOIN account_account a on a.id = l.account_id " \
                                           "INNER JOIN res_partner r on r.id = l.partner_id " \
                                           "INNER JOIN account_journal j on j.id = l.journal_id " \
                                           "WHERE j.type = 'situation' AND l.date = %s AND r.id = %s " \
                                           "AND a.id = %s " \
                                           "AND a.company_id = %s"
                                if repports.target_move == 'posted':
                                    an_query += " AND  m.state = 'posted'"
                                cr.execute(an_query,
                                           (repports.date_range_exercice_id.date_start, partner_id, account_id.id,
                                            company.id))
                                an = cr.fetchall()
                                solde_query = "SELECT ROUND(SUM(l.debit),2) AS debit, ROUND(SUM(l.credit),2) AS credit " \
                                              "FROM account_move_line as l " \
                                              "INNER JOIN account_move m on m.id = l.move_id " \
                                              "INNER JOIN account_account a on a.id = l.account_id " \
                                              "INNER JOIN res_partner r on r.id = l.partner_id " \
                                              "INNER JOIN account_journal j on j.id = l.journal_id " \
                                              "WHERE j.type != 'situation'AND l.date <= %s AND l.date >= %s " \
                                              "AND r.id = %s AND a.id = %s " \
                                              "AND a.company_id = %s"
                                if repports.target_move == 'posted':
                                    solde_query += " AND  m.state = 'posted'"
                                cr.execute(solde_query, (
                                repports.date_to, repports.date_from, partner_id, account_id.id, company.id))
                                solde = cr.fetchall()


                                if partner_id:
                                    partner = self.env['res.partner'].browse(partner_id)

                                # ne pas afficher les comptes sans aucun mouvement
                                if not an[0][0] and not an[0][1] and not movelines:
                                    continue
                                an_debit = an[0][0] and an[0][0] or 0
                                an_credit = an[0][1] and an[0][1] or 0
                                somme_debit = solde[0][0] and solde[0][0] or 0
                                somme_credit = solde[0][1] and solde[0][1] or 0
                                sheet.write(row, 1, partner.name or 'Indéfini', number)
                                sheet.write(row, 2, an_debit, number)
                                sheet.write(row, 3, an_credit, number)
                                sheet.write(row, 4, somme_debit, number)
                                sheet.write(row, 5, somme_credit, number)
                                sheet.write(row, 6,
                                            somme_debit + an_debit - somme_credit - an_credit if somme_debit + an_debit > somme_credit + an_credit else 0,
                                            number)
                                sheet.write(row, 7,
                                            -somme_debit - an_debit + somme_credit + an_credit if somme_debit + an_debit < somme_credit + an_credit else 0,
                                            number)

                                row += 1
                if not repports.partenaire_detail:
                    sheet.write_formula(row, 2, '=SUM(C7:C' + str(row) + ')', title)
                    sheet.write_formula(row, 3, "=SUM(D7:D" + str(row) + ")", title)
                    sheet.write_formula(row, 4, "=SUM(E7:E" + str(row) + ")", title)
                    sheet.write_formula(row, 5, "=SUM(F7:F" + str(row) + ")", title)
                    sheet.write_formula(row, 6, "=SUM(G7:G" + str(row) + ")", title)
                    sheet.write_formula(row, 7, "=SUM(H7:H" + str(row) + ")", title)

        return workbook
#
# financial_xlsx('report.financial.report.gl.xlsx',
#              'financial.report')
#
# financial_xlsx('report.financial.report.balance.xlsx',
#              'financial.report')
