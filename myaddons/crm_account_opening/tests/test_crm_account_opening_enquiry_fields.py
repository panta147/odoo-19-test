from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestCrmAccountOpeningEnquiryFields(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def _base_vals(self, **extra):
        vals = {"name": "Lead", "source_id": self.source_id, "medium_id": self.medium_id}
        vals.update(extra)
        return vals

    def test_enquiry_fields_roundtrip(self):
        product = self.env["crm.product"].create({
            "code": "AC-SAVINGS",
            "name": "Savings Account",
            "product_family": "account_opening",
        })
        lead = self.env["crm.lead"].create(self._base_vals(
            product_interested_id=product.id,
            expected_initial_deposit=25000.0,
            expected_account_opening_date="2026-08-01",
        ))

        self.assertEqual(lead.expected_initial_deposit, 25000.0)
        self.assertEqual(str(lead.expected_account_opening_date), "2026-08-01")

    def test_fixed_deposit_product_requires_deposit_term(self):
        fd_product = self.env["crm.product"].create({
            "code": "AC-FD",
            "name": "Fixed Deposit Account",
            "product_family": "account_opening",
            "is_fixed_deposit": True,
        })
        with self.assertRaises(ValidationError):
            self.env["crm.lead"].create(self._base_vals(product_interested_id=fd_product.id))

    def test_fixed_deposit_product_with_term_succeeds(self):
        fd_product = self.env["crm.product"].create({
            "code": "AC-FD2",
            "name": "Fixed Deposit Account",
            "product_family": "account_opening",
            "is_fixed_deposit": True,
        })
        lead = self.env["crm.lead"].create(self._base_vals(
            product_interested_id=fd_product.id, deposit_term=12,
        ))
        self.assertEqual(lead.deposit_term, 12)

    def test_non_fixed_deposit_product_does_not_require_deposit_term(self):
        savings_product = self.env["crm.product"].create({
            "code": "AC-SAVINGS2",
            "name": "Savings Account",
            "product_family": "account_opening",
        })
        lead = self.env["crm.lead"].create(self._base_vals(product_interested_id=savings_product.id))
        self.assertTrue(lead)
