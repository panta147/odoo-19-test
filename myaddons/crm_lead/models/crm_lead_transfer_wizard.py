from odoo import api, fields, models


class CrmLeadTransferWizard(models.TransientModel):
    _name = "crm.lead.transfer.wizard"
    _description = "Transfer Lead to Another Branch"

    lead_id = fields.Many2one("crm.lead", required=True)
    target_company_id = fields.Many2one(
        "res.company", string="Target Branch", required=True,
        domain=lambda self: [("id", "in", self.env.user.company_ids.ids)],
    )

    def action_confirm(self):
        self.ensure_one()
        self.lead_id.action_request_transfer(self.target_company_id.id)
