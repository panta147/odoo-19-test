{
    'name': "Bank CRM - Integration API",
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': "Integration layer for CBS/AOS/LOS/KYCMS/ProcessMaker/NBank REST/JSON touchpoints (FRS Section 15)",
    'description': """Generic REST/JSON contract, authentication and logging shared by all
inbound bank-system integrations (FRS Section 15 - System Integration
Touchpoints): CBS, AOS, LOS, KYCMS, ProcessMaker, NBank, Website/nBank/
Social Media lead ingestion, and the daily batch/cron callback.

Pipeline modules (crm_account_opening/transaction/retail/sme) implement their
own endpoints on top of the base contract exposed here rather than each
re-implementing auth/logging/error-handling. Integration failures raise
alerts to the CRM Admin role.""",
    'author': 'Amnil Technologies',
    'website': '',
    'license': 'OPL-1',
    'depends': ['crm_lead'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
