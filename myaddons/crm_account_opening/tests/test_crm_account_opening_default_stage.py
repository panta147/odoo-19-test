from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmAccountOpeningDefaultStage(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def test_new_account_opening_lead_defaults_to_enquiry_stage(self):
        product = self.env["crm.product"].create({
            "code": "AC-DEFAULT-STAGE-TEST",
            "name": "Savings Account",
            "product_family": "account_opening",
        })

        lead = self.env["crm.lead"].create({
            "name": "Lead",
            "source_id": self.source_id,
            "medium_id": self.medium_id,
            "product_interested_id": product.id,
        })

        self.assertEqual(lead.stage_id, self.env.ref("crm_account_opening.stage_enquiry"))
