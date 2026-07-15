from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmLeadTransferWizard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def test_wizard_confirm_requests_transfer_on_lead(self):
        target = self.env["res.company"].create({"name": "Itahari Branch"})
        lead = self.env["crm.lead"].create({
            "name": "Lead",
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        wizard = self.env["crm.lead.transfer.wizard"].create({
            "lead_id": lead.id,
            "target_company_id": target.id,
        })
        wizard.action_confirm()

        self.assertEqual(lead.transfer_state, "pending")
        self.assertEqual(lead.transfer_target_company_id, target)
