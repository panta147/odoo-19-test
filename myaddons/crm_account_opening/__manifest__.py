{
    'name': "Bank CRM - Account Opening",
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': "Account Opening pipeline: Enquiry -> Document Collection -> Account Opening in Process -> Closed (FRS Section 10)",
    'description': """Account Opening pipeline (FRS Section 10, Use Cases LM-AC-001 to LM-AC-004):
Enquiry -> Document Collection -> Account Opening in Process -> Closed (Won/Lost).
Integrates with KYCMS (document/KYC status) and AOS (account creation,
Account Number & CIF stamp-back). AOS/KYCMS-sourced fields are read-only.""",
    'author': 'Amnil Technologies',
    'website': '',
    'license': 'OPL-1',
    'depends': ['crm_lead', 'crm_api'],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
}
