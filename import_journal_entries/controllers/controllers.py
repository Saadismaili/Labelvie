# -*- coding: utf-8 -*-
# from odoo import http


# class ImportJournalEntries(http.Controller):
#     @http.route('/import_journal_entries/import_journal_entries', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_journal_entries/import_journal_entries/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_journal_entries.listing', {
#             'root': '/import_journal_entries/import_journal_entries',
#             'objects': http.request.env['import_journal_entries.import_journal_entries'].search([]),
#         })

#     @http.route('/import_journal_entries/import_journal_entries/objects/<model("import_journal_entries.import_journal_entries"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_journal_entries.object', {
#             'object': obj
#         })
