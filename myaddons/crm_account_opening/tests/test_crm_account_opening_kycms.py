from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestCrmAccountOpeningKycms(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def _create_lead(self, **extra):
        vals = {"name": "Lead", "source_id": self.source_id, "medium_id": self.medium_id}
        vals.update(extra)
        return self.env["crm.lead"].create(vals)

    def test_kycms_crm_id_can_be_set(self):
        lead = self._create_lead()

        lead.write({"kycms_crm_id": "KYCMS-000123"})

        self.assertEqual(lead.kycms_crm_id, "KYCMS-000123")

    def test_kycms_crm_id_locked_once_set(self):
        lead = self._create_lead(kycms_crm_id="KYCMS-000123")

        with self.assertRaises(ValidationError):
            lead.write({"kycms_crm_id": "KYCMS-000999"})

    def test_kycms_accepted_status_advances_to_account_opening_in_process(self):
        lead = self._create_lead(
            stage_id=self.env.ref("crm_account_opening.stage_document_collection").id,
            kycms_crm_id="KYCMS-000123",
        )

        lead._apply_kycms_status_update("accepted")

        self.assertEqual(lead.kycms_status, "accepted")
        self.assertEqual(
            lead.stage_id, self.env.ref("crm_account_opening.stage_account_opening_in_process")
        )

    def test_kycms_sent_status_does_not_advance_stage(self):
        doc_collection = self.env.ref("crm_account_opening.stage_document_collection")
        lead = self._create_lead(stage_id=doc_collection.id, kycms_crm_id="KYCMS-000123")

        lead._apply_kycms_status_update("sent")

        self.assertEqual(lead.kycms_status, "sent")
        self.assertEqual(lead.stage_id, doc_collection)
