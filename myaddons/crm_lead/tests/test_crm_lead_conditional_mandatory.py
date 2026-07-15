from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestCrmLeadConditionalMandatory(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def _base_vals(self, **extra):
        vals = {
            "name": "Corporate Lead",
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        }
        vals.update(extra)
        return vals

    def test_corporate_lead_requires_nature_of_business(self):
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].create(self._base_vals(
                customer_type="corporate",
                annual_turnover=500000.0,
                years_of_operation=5,
            ))

    def test_corporate_lead_requires_annual_turnover(self):
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].create(self._base_vals(
                customer_type="corporate",
                nature_of_business="Trading",
                years_of_operation=5,
            ))

    def test_corporate_lead_requires_years_of_operation(self):
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].create(self._base_vals(
                customer_type="corporate",
                nature_of_business="Trading",
                annual_turnover=500000.0,
            ))

    def test_corporate_lead_with_all_fields_succeeds(self):
        lead = self.env["crm.lead"].create(self._base_vals(
            customer_type="corporate",
            nature_of_business="Trading",
            annual_turnover=500000.0,
            years_of_operation=5,
        ))
        self.assertTrue(lead)

    def test_existing_customer_requires_account_number(self):
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].create(self._base_vals(
                customer_status="existing_customer",
            ))

    def test_existing_customer_with_account_number_succeeds(self):
        lead = self.env["crm.lead"].create(self._base_vals(
            customer_status="existing_customer",
            account_number="1900123456",
        ))
        self.assertTrue(lead)

    def test_staff_referral_medium_requires_staff_id(self):
        staff_referral_medium = self.env.ref("crm_lead.utm_medium_staff_referral")
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].create(self._base_vals(
                medium_id=staff_referral_medium.id,
            ))

    def test_staff_referral_medium_with_staff_id_succeeds(self):
        staff_referral_medium = self.env.ref("crm_lead.utm_medium_staff_referral")
        lead = self.env["crm.lead"].create(self._base_vals(
            medium_id=staff_referral_medium.id,
            staff_id="STF-001",
        ))
        self.assertTrue(lead)

    def test_write_to_corporate_without_nature_of_business_fails(self):
        lead = self.env["crm.lead"].create(self._base_vals())
        with self.assertRaises(ValidationError):
            lead.write({"customer_type": "corporate"})

    def test_blanking_staff_id_on_existing_staff_referral_lead_fails(self):
        staff_referral_medium = self.env.ref("crm_lead.utm_medium_staff_referral")
        lead = self.env["crm.lead"].create(self._base_vals(
            medium_id=staff_referral_medium.id,
            staff_id="STF-001",
        ))
        with self.assertRaises(ValidationError):
            lead.write({"staff_id": False})
