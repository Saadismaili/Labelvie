# pylint: disable=missing-docstring, manifest-required-author
{
    'name': "Account Morocco Reports",
    'summary': "Account Morocco Reports Updates",
    'author': 'Osisoftware',
    'website': 'http://www.osisoftware.ma',
    'category': 'account',
    'version': '13.0.1.0.0',
    'license': 'OPL-1',
    'depends': [
        'account',
        'account_accountant',
        'account_reports',
        'date_range',
        'account_disallowed_expenses',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/date_range.xml',
        'views/passage_data.xml',
        'views/account_move.xml',
        'views/assets_group.xml',
        'views/equity_group.xml',
        'views/profit_group.xml',
        'views/esg_tfr_group.xml',
        'views/esg_caf_group.xml',
        'views/detail_cpc_group.xml',
        'views/loss_group.xml',
        'views/passage.xml',
        'views/partner_share.xml',
        'views/account_account.xml',
        'views/menuitem.xml',
        'templates/morocco_template.xml',
        'report/account_report_assets.xml',
        'report/account_report_equity.xml',
        'report/account_report_profit.xml',
        'report/partner_share_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_morocco_reports/static/src/scss/account_reports.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
