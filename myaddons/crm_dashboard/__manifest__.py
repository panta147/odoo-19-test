{
    'name': "Bank CRM - Dashboard & Reporting",
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': "Reporting and dashboards across all pipelines (FRS Project Scope - Reporting and Dashboarding)",
    'description': """Cross-pipeline reporting and dashboards (FRS Project Scope). Read-only
aggregation layer over Account Opening, Transaction Banking, Retail Lending
and SME Loan pipelines; intentionally the only module allowed to depend on
all four product pipelines at once.""",
    'author': 'Amnil Technologies',
    'website': '',
    'license': 'OPL-1',
    'depends': ['crm_account_opening', 'crm_transaction', 'crm_retail', 'crm_sme'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
