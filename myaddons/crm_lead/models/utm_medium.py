from odoo import fields, models


class UtmMedium(models.Model):
    _inherit = "utm.medium"

    channel_category = fields.Selection(
        [("digital", "Digital"), ("offline", "Offline"), ("referral", "Referral")],
        string="FRS Channel Category",
    )
