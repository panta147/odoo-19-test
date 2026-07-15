{
    'name': "Bank CRM - Transaction Banking",
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': "Transaction Banking pipeline for Individual & Corporate products (FRS Section 11)",
    'description': """Transaction Banking pipeline (FRS Section 11, Use Cases LM-TC-001 to LM-TC-005):
Enquiry -> (New Customer) Account Opening -> Document Collection ->
Conversion In Progress -> Closed.

Covers Individual products (Credit Card, BNPL, Virtual Credit Card, Prepaid
Card, Locker, Debit Card) and Corporate products (Payment Gateway, Onelink,
POS, QR, BNPL Merchant, Corporate Pay, Nabil Corporate Net, Creditor/NPI
Enlisting), routed to ProcessMaker or NBank depending on product.""",
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
