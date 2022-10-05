# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'Morocco - Accounting - Reporting - Profit Company',
    'author': 'CORE B.P.O',
    'category': 'Localization',
    'description': """
    This is the base module to view the chart for Morocco in legal reports.
    """,
    'website': 'http://www.core-bpo.com',
    'version': '13.0.1.0.0',
    'license': 'OPL-1',
    'depends': [
        'l10n_ma_profit',
        'account_morocco_reports',
    ],
    'data': [
        'data/assets_group.xml',
        'data/assets_line.xml',
        'data/equity_group.xml',
        'data/equity_line.xml',
        'data/profit_group.xml',
        'data/profit_line.xml',
        'data/loss_group.xml',
        'data/loss_line.xml',
        'data/passage_group.xml',
        'data/passage_line.xml',
        'data/disallowed_expense.xml',
        'data/esg_tfr_group.xml',
        'data/esg_caf_group.xml',
        'data/detail_cpc_group.xml',
        'data/detail_cpc_2.xml',
        'data/esg_tfr_line.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
