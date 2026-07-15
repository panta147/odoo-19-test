from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCrmAccountOpeningStages(TransactionCase):

    def test_five_stages_seeded(self):
        stage_xmlids = [
            "crm_account_opening.stage_enquiry",
            "crm_account_opening.stage_document_collection",
            "crm_account_opening.stage_account_opening_in_process",
            "crm_account_opening.stage_closed_won",
            "crm_account_opening.stage_closed_lost",
        ]
        stages = [self.env.ref(xmlid) for xmlid in stage_xmlids]

        self.assertEqual(len(stages), 5)
        self.assertTrue(all(stage._name == "crm.stage" for stage in stages))

    def test_closed_won_stage_is_won(self):
        stage = self.env.ref("crm_account_opening.stage_closed_won")
        self.assertTrue(stage.is_won)

    def test_closed_lost_stage_is_not_won(self):
        stage = self.env.ref("crm_account_opening.stage_closed_lost")
        self.assertFalse(stage.is_won)
