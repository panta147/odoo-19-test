{
    'name': "Bank CRM - SME Loan",
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': "SME Loan pipeline with LOS-driven multi-level approval chain (FRS Section 13)",
    'description': """SME Loan pipeline (FRS Section 13, Use Cases LM-SME-001 to LM-SME-010):
Enquiry -> Application Submitted -> Credit Assessment -> Approval Chain ->
Disbursement -> Closed.

Enquiry-stage prospect is classified Hot/Warm/Cold. The internal multi-level
approval hierarchy (e.g. Branch -> Credit -> Regional -> Head Office) is
driven entirely by LOS; CRM only visualizes current level and history via
crm.sme.approval.log. LOS/credit-assessment-sourced fields are read-only in
CRM. Escalation matrix applies via crm_notification.""",
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
