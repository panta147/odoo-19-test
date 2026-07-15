from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged("post_install", "-at_install")
class TestCrmLeadTransfer(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def _base_vals(self, **extra):
        vals = {
            "name": "Lead",
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        }
        vals.update(extra)
        return vals

    def test_requesting_transfer_sets_pending_state_without_changing_company(self):
        original_company = self.env.user.company_id
        target = self.env["res.company"].create({"name": "Biratnagar Branch"})
        lead = self.env["crm.lead"].create(self._base_vals())

        lead.action_request_transfer(target.id)

        self.assertEqual(lead.transfer_state, "pending")
        self.assertEqual(lead.transfer_target_company_id, target)
        self.assertEqual(lead.company_id, original_company)

    def test_approve_transfer_by_target_branch_manager_applies_company(self):
        bm_group = self.env.ref("crm_data.group_bank_branch_manager")
        target = self.env["res.company"].create({"name": "Butwal Branch"})
        branch_manager = self.env["res.users"].create({
            "name": "Butwal BM",
            "login": "butwal.bm@example.com",
            "company_id": target.id,
            "company_ids": [(4, target.id)],
            "group_ids": [
                (4, bm_group.id),
                (4, self.env.ref("base.group_user").id),
                (4, self.env.ref("sales_team.group_sale_salesman").id),
            ],
        })
        lead = self.env["crm.lead"].create(self._base_vals())
        lead.action_request_transfer(target.id)

        lead.with_user(branch_manager).action_approve_transfer()

        self.assertEqual(lead.company_id, target)
        self.assertFalse(lead.transfer_state)

    def test_approve_transfer_by_non_branch_manager_blocked(self):
        target = self.env["res.company"].create({"name": "Ghorahi Branch"})
        non_manager = self.env["res.users"].create({
            "name": "Regular Salesperson",
            "login": "regular.rm@example.com",
            "company_id": target.id,
            "company_ids": [(4, target.id)],
            "group_ids": [
                (4, self.env.ref("base.group_user").id),
                (4, self.env.ref("sales_team.group_sale_salesman").id),
            ],
        })
        lead = self.env["crm.lead"].create(self._base_vals())
        lead.action_request_transfer(target.id)

        with self.assertRaises(UserError):
            lead.with_user(non_manager).action_approve_transfer()

    def test_reject_transfer_clears_pending_state_without_changing_company(self):
        bm_group = self.env.ref("crm_data.group_bank_branch_manager")
        original_company = self.env.user.company_id
        target = self.env["res.company"].create({"name": "Nepalgunj Branch"})
        branch_manager = self.env["res.users"].create({
            "name": "Nepalgunj BM",
            "login": "nepalgunj.bm@example.com",
            "company_id": target.id,
            "company_ids": [(4, target.id)],
            "group_ids": [
                (4, bm_group.id),
                (4, self.env.ref("base.group_user").id),
                (4, self.env.ref("sales_team.group_sale_salesman").id),
            ],
        })
        lead = self.env["crm.lead"].create(self._base_vals())
        lead.action_request_transfer(target.id)

        lead.with_user(branch_manager).action_reject_transfer()

        self.assertEqual(lead.transfer_state, "rejected")
        self.assertEqual(lead.company_id, original_company)

    def test_requesting_transfer_to_inaccessible_company_blocked(self):
        # res.company.create() auto-grants the creating user access to the new
        # company (native Odoo behavior) - explicitly revoke it here to simulate
        # a branch this user genuinely doesn't have access to.
        target = self.env["res.company"].create({"name": "Dharan Branch"})
        self.env.user.write({"company_ids": [(3, target.id)]})
        lead = self.env["crm.lead"].create(self._base_vals())

        with self.assertRaises(UserError):
            lead.action_request_transfer(target.id)
