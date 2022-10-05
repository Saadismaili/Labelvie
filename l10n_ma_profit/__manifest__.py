# pylint: disable=missing-docstring, manifest-required-author
{
    'name': 'Morocco - Accounting - Profit Company',
    'author': 'CORE B.P.O',
    'category': 'Localization',
    'description': """
    This is the base module to manage the accounting chart for Morocco.
    """,
    'website': 'http://www.core-bpo.com',
    'version': '13.0.1.0.0',
    'license': 'OPL-1',
    'depends': ['account'],
    'data': [
        # 'data/account_chart_template.xml',
        # 'data/account.account.template.csv',
        # 'data/account_chart_template_assign.xml',
    ],
    'demo': [
        'demo/account_account.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
