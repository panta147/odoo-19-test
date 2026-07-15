from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmLeadFields(TransactionCase):

    def test_lead_detail_fields_roundtrip(self):
        partner = self.env["res.partner"].create({
            "name": "Nirmala Adhikari",
            "citizenship_number": "15-06-75-03333",
        })
        product = self.env["crm.product"].create({
            "code": "RL-HOME",
            "name": "Home Loan",
            "product_family": "retail_lending",
        })
        company = self.env["res.company"].create({"name": "Test Branch"})
        referrer = self.env["res.partner"].create({"name": "Existing Customer"})

        lead = self.env["crm.lead"].create({
            "name": "Nirmala Adhikari - Enquiry",
            "partner_id": partner.id,
            "customer_type": "individual",
            "customer_status": "existing_customer",
            "product_interested_id": product.id,
            "preferred_company_id": company.id,
            "referred_by_id": referrer.id,
            "staff_id": "STF-001",
            "account_number": "1900123456",
            "nature_of_business": "Retail Trading",
            "annual_turnover": 500000.0,
            "years_of_operation": 5,
            "requested_loan_amount": 2500000.0,
            "purpose": "term_loan_against_fixed_assets",
            "source_id": self.env.ref("utm.utm_source_search_engine").id,
            "medium_id": self.env.ref("utm.utm_medium_website").id,
        })

        self.assertEqual(lead.customer_type, "individual")
        self.assertEqual(lead.customer_status, "existing_customer")
        self.assertEqual(lead.product_interested_id, product)
        self.assertEqual(lead.preferred_company_id, company)
        self.assertEqual(lead.referred_by_id, referrer)
        self.assertEqual(lead.staff_id, "STF-001")
        self.assertEqual(lead.account_number, "1900123456")
        self.assertEqual(lead.nature_of_business, "Retail Trading")
        self.assertEqual(lead.annual_turnover, 500000.0)
        self.assertEqual(lead.years_of_operation, 5)
        self.assertEqual(lead.requested_loan_amount, 2500000.0)
        self.assertEqual(lead.purpose, "term_loan_against_fixed_assets")
