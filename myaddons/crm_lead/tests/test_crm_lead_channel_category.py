from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmLeadChannelCategory(TransactionCase):

    def test_website_medium_is_digital(self):
        website = self.env.ref("utm.utm_medium_website")
        self.assertEqual(website.channel_category, "digital")

    def test_email_medium_is_digital(self):
        email = self.env.ref("utm.utm_medium_email")
        self.assertEqual(email.channel_category, "digital")

    def test_phone_medium_is_offline(self):
        phone = self.env.ref("utm.utm_medium_phone")
        self.assertEqual(phone.channel_category, "offline")

    def test_staff_referral_medium_is_referral(self):
        staff_referral = self.env.ref("crm_lead.utm_medium_staff_referral")
        self.assertEqual(staff_referral.channel_category, "referral")
