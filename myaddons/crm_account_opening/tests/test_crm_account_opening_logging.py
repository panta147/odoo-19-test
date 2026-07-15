from unittest.mock import patch

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmAccountOpeningLogging(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def _create_lead(self, **extra):
        vals = {"name": "Lead", "source_id": self.source_id, "medium_id": self.medium_id}
        vals.update(extra)
        return self.env["crm.lead"].create(vals)

    @patch("odoo.addons.crm_account_opening.models.crm_lead._logger")
    def test_kycms_status_update_is_logged(self, mock_logger):
        lead = self._create_lead(kycms_crm_id="KYCMS-000123")

        lead._apply_kycms_status_update("accepted")

        logged = "\n".join(str(call.args) for call in mock_logger.info.call_args_list)
        self.assertIn(str(lead.id), logged)
        self.assertIn("kycms", logged.lower())

    @patch("odoo.addons.crm_account_opening.models.crm_lead._logger")
    def test_aos_approval_is_logged_without_account_number(self, mock_logger):
        lead = self._create_lead(aos_crm_id="AOS-000123")

        lead._apply_aos_approval(account_number="1900123456", cif_id="CIF00456789")

        logged = "\n".join(str(call.args) for call in mock_logger.info.call_args_list)
        self.assertIn(str(lead.id), logged)
        # Sensitive banking data (account number/CIF) must never be logged
        # (CLAUDE.md Logging Rules: "Never log... Sensitive Banking Data").
        self.assertNotIn("1900123456", logged)
        self.assertNotIn("CIF00456789", logged)

    @patch("odoo.addons.crm_account_opening.models.crm_lead._logger")
    def test_aos_rejection_is_logged(self, mock_logger):
        lead = self._create_lead(aos_crm_id="AOS-000123")

        lead._apply_aos_rejection("KYC documents insufficient")

        logged = "\n".join(str(call.args) for call in mock_logger.info.call_args_list)
        self.assertIn(str(lead.id), logged)
