from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmLeadAutoAssignment(TransactionCase):

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

    def test_user_id_defaults_to_creating_user(self):
        lead = self.env["crm.lead"].create(self._base_vals())

        self.assertEqual(lead.user_id, self.env.user)

    def test_company_id_defaults_to_creating_users_company(self):
        lead = self.env["crm.lead"].create(self._base_vals())

        self.assertEqual(lead.company_id, self.env.user.company_id)

    def test_team_id_defaults_to_team_matching_lead_company(self):
        branch = self.env["res.company"].create({"name": "Pokhara Branch"})
        branch_team = self.env["crm.team"].create({
            "name": "Pokhara Branch Team",
            "company_id": branch.id,
        })

        lead = self.env["crm.lead"].create(self._base_vals(company_id=branch.id))

        self.assertEqual(lead.team_id, branch_team)
