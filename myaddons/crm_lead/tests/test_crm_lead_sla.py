from datetime import timedelta

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo import fields


@tagged("post_install", "-at_install")
class TestCrmLeadSla(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id

    def _base_vals(self, **extra):
        vals = {"name": "Lead", "source_id": self.source_id}
        vals.update(extra)
        return vals

    def test_digital_lead_gets_sla_deadline_from_configured_hours(self):
        self.env["ir.config_parameter"].sudo().set_param("crm_base.sla_hours.digital", "2")
        digital_medium = self.env.ref("utm.utm_medium_website")

        before = fields.Datetime.now()
        lead = self.env["crm.lead"].create(self._base_vals(medium_id=digital_medium.id))
        after = fields.Datetime.now()

        self.assertTrue(before + timedelta(hours=2) <= lead.sla_deadline <= after + timedelta(hours=2))

    def test_offline_lead_gets_sla_deadline_from_configured_hours(self):
        self.env["ir.config_parameter"].sudo().set_param("crm_base.sla_hours.offline", "24")
        offline_medium = self.env.ref("utm.utm_medium_phone")

        before = fields.Datetime.now()
        lead = self.env["crm.lead"].create(self._base_vals(medium_id=offline_medium.id))
        after = fields.Datetime.now()

        self.assertTrue(before + timedelta(hours=24) <= lead.sla_deadline <= after + timedelta(hours=24))

    def test_lead_with_no_sla_config_gets_no_deadline(self):
        # crm_base.sla_hours.digital is deliberately unset in this test - the
        # mixin must not guess a default, per CLAUDE.md's "never invent business
        # rules" / "ask when unclear" and the explicit 2026-07-13 scoping decision.
        digital_medium = self.env.ref("utm.utm_medium_website")

        lead = self.env["crm.lead"].create(self._base_vals(medium_id=digital_medium.id))

        self.assertFalse(lead.sla_deadline)

    def test_lead_with_sla_deadline_schedules_followup_activity(self):
        self.env["ir.config_parameter"].sudo().set_param("crm_base.sla_hours.digital", "2")
        digital_medium = self.env.ref("utm.utm_medium_website")

        lead = self.env["crm.lead"].create(self._base_vals(medium_id=digital_medium.id))

        self.assertTrue(lead.activity_ids)
        self.assertEqual(lead.activity_ids[:1].date_deadline, lead.sla_deadline.date())

    def test_lead_with_no_sla_config_schedules_no_activity(self):
        digital_medium = self.env.ref("utm.utm_medium_website")

        lead = self.env["crm.lead"].create(self._base_vals(medium_id=digital_medium.id))

        self.assertFalse(lead.activity_ids)
