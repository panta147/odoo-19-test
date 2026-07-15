from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmAccountOpeningStageAdvance(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def test_manual_advance_to_document_collection(self):
        lead = self.env["crm.lead"].create({
            "name": "Lead",
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })
        doc_collection = self.env.ref("crm_account_opening.stage_document_collection")

        lead.write({"stage_id": doc_collection.id})

        self.assertEqual(lead.stage_id, doc_collection)
