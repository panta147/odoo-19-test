from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmLeadPartnerSync(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source_id = cls.env.ref("utm.utm_source_search_engine").id
        cls.medium_id = cls.env.ref("utm.utm_medium_website").id

    def test_citizenship_number_synced_from_partner_on_create(self):
        partner = self.env["res.partner"].create({
            "name": "Ram Bahadur Thapa",
            "citizenship_number": "12-01-70-01234",
        })
        lead = self.env["crm.lead"].create({
            "name": "Ram Bahadur Thapa - Enquiry",
            "partner_id": partner.id,
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        self.assertEqual(lead.citizenship_number, "12-01-70-01234")

    def test_editing_lead_citizenship_number_pushes_to_partner(self):
        partner = self.env["res.partner"].create({
            "name": "Sita Gurung",
            "citizenship_number": "10-02-71-05678",
        })
        lead = self.env["crm.lead"].create({
            "name": "Sita Gurung - Enquiry",
            "partner_id": partner.id,
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        lead.write({"citizenship_number": "10-02-71-09999"})

        self.assertEqual(partner.citizenship_number, "10-02-71-09999")

    def test_blanking_lead_citizenship_number_does_not_blank_partner(self):
        partner = self.env["res.partner"].create({
            "name": "Hari Prasad Koirala",
            "citizenship_number": "11-03-72-04321",
        })
        lead = self.env["crm.lead"].create({
            "name": "Hari Prasad Koirala - Enquiry",
            "partner_id": partner.id,
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        lead.write({"citizenship_number": False})

        self.assertEqual(partner.citizenship_number, "11-03-72-04321")

    def test_national_id_number_synced_from_partner_on_create(self):
        partner = self.env["res.partner"].create({
            "name": "Gita Sharma",
            "citizenship_number": "13-04-73-01111",
            "national_id_number": "NID-001122",
        })
        lead = self.env["crm.lead"].create({
            "name": "Gita Sharma - Enquiry",
            "partner_id": partner.id,
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        self.assertEqual(lead.national_id_number, "NID-001122")

    def test_passport_number_synced_from_partner_on_create(self):
        partner = self.env["res.partner"].create({
            "name": "Bikash Rai",
            "citizenship_number": "14-05-74-02222",
            "passport_number": "PA1234567",
        })
        lead = self.env["crm.lead"].create({
            "name": "Bikash Rai - Enquiry",
            "partner_id": partner.id,
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        self.assertEqual(lead.passport_number, "PA1234567")

    def test_vat_synced_from_partner_on_create(self):
        partner = self.env["res.partner"].create({
            "name": "Himalayan Traders Pvt Ltd",
            "is_company": True,
            "vat": "301XXXXXXXX",
        })
        lead = self.env["crm.lead"].create({
            "name": "Himalayan Traders - Enquiry",
            "partner_id": partner.id,
            "source_id": self.source_id,
            "medium_id": self.medium_id,
        })

        self.assertEqual(lead.vat, "301XXXXXXXX")
