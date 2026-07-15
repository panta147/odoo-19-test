from odoo import fields, models


class CrmProduct(models.Model):
    _inherit = "crm.product"

    # FRS §10 only distinguishes "fixed deposit" from every other Account
    # Opening product ("Term (applicable for fixed deposit)") without naming
    # an exhaustive product catalog or code list - a boolean here avoids
    # inventing product codes the FRS never gave (see docs/account_opening.md
    # §6, same category of gap as crm_retail's unspecified seed codes).
    is_fixed_deposit = fields.Boolean(string="Is Fixed Deposit Product")
