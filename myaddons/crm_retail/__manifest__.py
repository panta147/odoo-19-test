{
    'name': "Bank CRM - Retail Lending",
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': "Retail Lending pipeline: Home/Auto/Personal/FD-backed/Education Loans (FRS Section 12)",
    'description': """Retail Lending pipeline (FRS Section 12, Use Cases LM-RL-001 to LM-RL-005):
Enquiry -> Application Submitted -> Processing/Approval -> Disbursement ->
Closed.

Product-specific enquiry fields for Home Loan, Auto Loan, Personal Loan,
Loan Against Fixed Deposit, and Education Loan. LOS is authoritative for
all credit decisioning; LOS-sourced fields are read-only in CRM.""",
    'author': 'Amnil Technologies',
    'website': '',
    'license': 'OPL-1',
    'depends': ['crm_lead', 'crm_api'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
