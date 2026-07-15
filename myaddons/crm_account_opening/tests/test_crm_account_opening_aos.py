from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestCrmAccountOpeningAos(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def _create_lead(self, **extra):
        vals = {"name": "Lead", "source_id": self.source_id, "medium_id": self.medium_id}
        vals.update(extra)
        return self.env["crm.lead"].create(vals)

    def test_aos_crm_id_can_be_set(self):
        lead = self._create_lead()

        lead.write({"aos_crm_id": "AOS-000123"})

        self.assertEqual(lead.aos_crm_id, "AOS-000123")

    def test_aos_crm_id_locked_once_set(self):
        lead = self._create_lead(aos_crm_id="AOS-000123")

        with self.assertRaises(ValidationError):
            lead.write({"aos_crm_id": "AOS-000999"})

    def test_aos_approval_advances_to_closed_won(self):
        lead = self._create_lead(
            stage_id=self.env.ref(
                "crm_account_opening.stage_account_opening_in_process"
            ).id,
            aos_crm_id="AOS-000123",
        )

        lead._apply_aos_approval(account_number="1900123456", cif_id="CIF00456789")

        self.assertEqual(lead.aos_status, "approved")
        self.assertEqual(lead.aos_account_number, "1900123456")
        self.assertEqual(lead.aos_cif_id, "CIF00456789")
        self.assertEqual(
            lead.stage_id, self.env.ref("crm_account_opening.stage_closed_won")
        )

    def test_aos_rejection_advances_to_closed_lost(self):
        lead = self._create_lead(
            stage_id=self.env.ref(
                "crm_account_opening.stage_account_opening_in_process"
            ).id,
            aos_crm_id="AOS-000123",
        )

        lead._apply_aos_rejection("KYC documents insufficient")

        self.assertEqual(lead.aos_status, "rejected")
        self.assertEqual(lead.aos_rejection_reason, "KYC documents insufficient")
        self.assertEqual(
            lead.stage_id, self.env.ref("crm_account_opening.stage_closed_lost")
        )
        self.assertEqual(lead.lost_reason_id.name, "KYC documents insufficient")

    def test_duplicate_aos_approval_callback_does_not_alter_already_closed_lead(self):
        lead = self._create_lead(
            stage_id=self.env.ref(
                "crm_account_opening.stage_account_opening_in_process"
            ).id,
            aos_crm_id="AOS-000123",
        )
        lead._apply_aos_approval(account_number="1900123456", cif_id="CIF00456789")

        # Late/duplicate callback for the same lead, already closed - must be
        # a no-op, not silently overwrite the already-recorded outcome.
        lead._apply_aos_rejection("Late duplicate rejection")

        self.assertEqual(lead.aos_status, "approved")
        self.assertEqual(lead.aos_account_number, "1900123456")
        self.assertEqual(
            lead.stage_id, self.env.ref("crm_account_opening.stage_closed_won")
        )
