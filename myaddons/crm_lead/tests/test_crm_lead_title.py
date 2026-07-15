from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmLeadTitle(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def test_title_auto_suggested_from_partner_and_product(self):
        partner = self.env["res.partner"].create({"name": "Suresh Maharjan"})
        product = self.env["crm.product"].create({
            "code": "TC-CC-DOM",
            "name": "Credit Card - Domestic",
            "product_family": "transaction_banking",
        })

        lead = self.env["crm.lead"].create({
            "partner_id": partner.id,
            "product_interested_id": product.id,
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        self.assertEqual(lead.name, "Suresh Maharjan – Credit Card - Domestic Enquiry")

    def test_title_falls_back_to_partner_only_when_no_product(self):
        partner = self.env["res.partner"].create({"name": "Anita Shrestha"})

        lead = self.env["crm.lead"].create({
            "partner_id": partner.id,
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        self.assertEqual(lead.name, "Anita Shrestha Enquiry")

    def test_title_falls_back_to_product_only_when_no_partner(self):
        product = self.env["crm.product"].create({
            "code": "RL-AUTO",
            "name": "Auto Loan",
            "product_family": "retail_lending",
        })

        lead = self.env["crm.lead"].create({
            "product_interested_id": product.id,
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        self.assertEqual(lead.name, "Auto Loan Enquiry")

    def test_title_falls_back_to_generic_when_neither_set(self):
        lead = self.env["crm.lead"].create({
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        self.assertEqual(lead.name, "New Enquiry")
