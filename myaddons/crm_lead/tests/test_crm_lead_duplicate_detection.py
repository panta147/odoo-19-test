from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged("post_install", "-at_install")
class TestCrmLeadDuplicateDetection(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id
        # Narrow active duplicate-check fields to just citizenship_number so
        # these tests exercise a single-field AND-set deterministically,
        # regardless of how many fields ship active by default in the seed
        # data (matching is now AND-across-active-fields, not OR-any-match -
        # see crm_contact/tests/test_duplicate_detection.py for the
        # multi-field scenario this affects).
        configs = cls.env["crm.duplicate.check.field"].search([
            ("res_model_id.model", "=", "crm.lead"),
        ])
        configs.write({"active": False})
        cls.citizenship_config = configs.filtered(lambda c: c.field_id.name == "citizenship_number")
        cls.citizenship_config.active = True

    def _base_vals(self, **extra):
        vals = {
            "name": "Lead",
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        }
        vals.update(extra)
        return vals

    def test_duplicate_citizenship_number_blocked(self):
        self.env["crm.lead"].create(self._base_vals(
            citizenship_number="16-07-76-04444",
        ))
        with self.assertRaises(UserError):
            self.env["crm.lead"].create(self._base_vals(
                citizenship_number="16-07-76-04444",
            ))

    def test_duplicate_override_with_justification_succeeds_and_logs(self):
        self.env["crm.lead"].create(self._base_vals(
            citizenship_number="17-08-77-05555",
        ))
        second = self.env["crm.lead"].with_context(
            force_duplicate_contact=True,
            duplicate_override_justification="Different customer, shared household ID typo confirmed by RM.",
        ).create(self._base_vals(
            citizenship_number="17-08-77-05555",
        ))

        self.assertTrue(second)
        self.assertTrue(any(
            "Justification" in (msg.body or "") for msg in second.message_ids
        ))

    def test_write_creating_duplicate_citizenship_number_blocked(self):
        self.env["crm.lead"].create(self._base_vals(
            citizenship_number="18-09-78-06666",
        ))
        other = self.env["crm.lead"].create(self._base_vals())

        with self.assertRaises(UserError):
            other.write({"citizenship_number": "18-09-78-06666"})

    def test_deactivating_config_field_stops_checking_it(self):
        # Proves the field list is genuinely dynamic (admin-configurable via
        # crm.duplicate.check.field), not just refactored plumbing around a
        # still-hardcoded list.
        citizenship_config = self.env["crm.duplicate.check.field"].search([
            ("res_model_id.model", "=", "crm.lead"),
            ("field_id.name", "=", "citizenship_number"),
        ])
        self.assertTrue(citizenship_config, "Expected the seeded citizenship_number config row to exist")
        citizenship_config.active = False

        self.env["crm.lead"].create(self._base_vals(citizenship_number="19-10-79-07777"))
        second = self.env["crm.lead"].create(self._base_vals(citizenship_number="19-10-79-07777"))
        self.assertTrue(second.id)
