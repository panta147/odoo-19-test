{
    'name': "Bank CRM - Escalation Notifications",
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': "SLA breach detection and Email/SMS/In-App escalation dispatch",
    'description': """Generic SLA/TAT breach detection and Email/SMS/In-App escalation dispatch
engine, configured per pipeline stage rather than duplicated in each
pipeline module. Reads escalation thresholds from the SLA mixin defined in
crm_base and drives the per-product escalation matrices defined across
FRS Sections 10-13 (e.g. SME Loan's 7-day / 16-hour / 8-hour tiers).""",
    'author': 'Amnil Technologies',
    'website': '',
    'license': 'OPL-1',
    'depends': ['crm_base'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
