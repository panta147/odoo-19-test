from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged("post_install", "-at_install")
class TestCrmAccountOpeningFieldProtection(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def _create_lead(self, **extra):
        vals = {"name": "Lead", "source_id": self.source_id, "medium_id": self.medium_id}
        vals.update(extra)
        return self.env["crm.lead"].create(vals)

    def test_direct_write_to_aos_account_number_blocked(self):
        lead = self._create_lead()

        with self.assertRaises(UserError):
            lead.write({"aos_account_number": "HACKED-123456"})

    def test_direct_write_to_kycms_status_blocked(self):
        lead = self._create_lead()

        with self.assertRaises(UserError):
            lead.write({"kycms_status": "accepted"})

    def test_stub_callback_methods_can_still_write_via_sync_context(self):
        lead = self._create_lead(aos_crm_id="AOS-000123")

        # The stub methods themselves must still work - they are the one
        # legitimate writer of these fields until crm_api's real callback
        # replaces them.
        lead._apply_aos_approval(account_number="1900123456", cif_id="CIF00456789")

        self.assertEqual(lead.aos_account_number, "1900123456")
