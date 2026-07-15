from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestCrmLeadSourceMedium(TransactionCase):

    def test_source_id_is_required(self):
        medium = self.env.ref("utm.utm_medium_website")
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self.env["crm.lead"].create({
                "name": "No Source Lead",
                "medium_id": medium.id,
            })

    def test_medium_id_is_required(self):
        source = self.env.ref("utm.utm_source_search_engine")
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self.env["crm.lead"].create({
                "name": "No Medium Lead",
                "source_id": source.id,
            })
