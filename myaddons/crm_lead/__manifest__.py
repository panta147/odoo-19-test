{
    'name': "Bank CRM - Lead Management",
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': "Base lead capture per FRS Use Case LM-001, shared across all product pipelines",
    'description': """Extends crm.lead with the base Lead Capture fields and rules common to all
four product pipelines (FRS Section 9, Use Case LM-001):
- Channel capture (Digital / Offline / Referral) and Source & Medium tagging.
- Customer Type/Status, Product Interested, Referred By, Staff ID.
- Duplicate-lead detection and auto-assignment to branch/RM.
- Bulk upload via standard Odoo Excel/CSV template.

Product-pipeline-specific stages and fields live in crm_account_opening,
crm_transaction, crm_retail and crm_sme, all of which depend on
this module rather than duplicating base lead logic.""",
    'author': 'Amnil Technologies',
    'website': '',
    'license': 'OPL-1',
    'depends': ['crm_base', 'crm_contact', 'generic_field_rules', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/utm_medium_data.xml',
        'data/crm_duplicate_check_field_data.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
}
