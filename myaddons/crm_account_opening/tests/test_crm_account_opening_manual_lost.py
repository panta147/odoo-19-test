from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged("post_install", "-at_install")
class TestCrmAccountOpeningManualLost(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def _create_lead(self, **extra):
        vals = {"name": "Lead", "source_id": self.source_id, "medium_id": self.medium_id}
        vals.update(extra)
        return self.env["crm.lead"].create(vals)

    def test_manual_lost_without_reason_blocked(self):
        # crm_lead enforces the mandatory-lost-reason rule project-wide
        # (see test_crm_lead_lost_reason_mandatory.py) - this just confirms
        # crm_account_opening leads inherit that enforcement unchanged.
        lead = self._create_lead()

        with self.assertRaises(UserError):
            lead.action_set_lost()

    def test_manual_lost_with_reason_succeeds(self):
        reason = self.env["crm.lost.reason"].create({"name": "Customer withdrew"})
        lead = self._create_lead(
            stage_id=self.env.ref("crm_account_opening.stage_enquiry").id,
        )

        lead.action_set_lost(lost_reason_id=reason.id)

        self.assertFalse(lead.active)
        self.assertEqual(lead.lost_reason_id, reason)
