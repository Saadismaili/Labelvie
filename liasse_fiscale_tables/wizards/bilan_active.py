from odoo import models, fields, api

class OpenAcademyXlsxReport(models.AbstractModel):
    _name = 'report.openacademy.openacademy_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        domain = [('state', '!=', 'cancel')]
        if data.get('date_from'):
            domain.append(('course_date', '>=', data.get('date_from')))
        if data.get('date_to'):
            domain.append(('course_date', '<=', data.get('date_to')))
        if data.get('course_ids'):
            domain.append(('id', 'in', data.get('course_ids')))
        if data.get('responsible_id'):
            domain.append(('responsible_id', '=', data.get('responsible_id')))

        sheet = workbook.add_worksheet('OpenAcademy Report')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#fffbed', 'border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 20, 'bg_color': '#f2eee4', 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})

        sheet.merge_range('A1:F1', 'OpenAcademy Report', title)

        courses = self.env['openacademy.course'].search(domain)
        row = 3
        col = 0

        # Header row
        sheet.set_column(0, 5, 18)
        sheet.write(row, col, 'Session Name', header_row_style)
        sheet.write(row, col+1, 'Start date', header_row_style)
        sheet.write(row, col+2, 'Duration', header_row_style)
        sheet.write(row, col+3, 'No. of seats', header_row_style)
        sheet.write(row, col+4, 'Instructor', header_row_style)
        sheet.write(row, col+5, 'Attendees', header_row_style)
        row += 2
        for course in courses:
            if course.session_ids:
                sheet.merge_range(f"A{row}:F{row}", course.course_name, bold)
            for session in course.session_ids:
                sheet.write(row, col, session.name)
                sheet.write(row, col+1, session.start_date)
                sheet.write(row, col+2, session.duration)
                sheet.write(row, col+3, session.seats)
                sheet.write(row, col+4, session.instructor_id.name)
                sheet.write(row, col+5, session.number_of_attendees())
                row += 1
            if course.session_ids:
                row += 1