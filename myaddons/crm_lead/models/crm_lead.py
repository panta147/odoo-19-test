from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class CrmLead(models.Model):
    _inherit = ["crm.lead", "crm.duplicate.detection.mixin", "crm.sla.mixin"]

    # Duplicate-check fields are no longer a hardcoded tuple here - they're
    # admin-configurable via crm.duplicate.check.field (Bank CRM > Configuration
    # > Duplicate Detection Fields), seeded to match prior behavior in
    # data/crm_duplicate_check_field_data.xml. See docs/duplicate_detection.md.

    _staff_referral_medium_xmlid = "crm_lead.utm_medium_staff_referral"

    source_id = fields.Many2one(required=True, ondelete="restrict")
    medium_id = fields.Many2one(required=True, ondelete="restrict")

    citizenship_number = fields.Char(
        compute="_compute_citizenship_number", inverse="_inverse_citizenship_number",
        store=True, readonly=False,
    )
    national_id_number = fields.Char(
        string="National ID (NID) Number",
        compute="_compute_national_id_number", inverse="_inverse_national_id_number",
        store=True, readonly=False,
    )
    passport_number = fields.Char(
        compute="_compute_passport_number", inverse="_inverse_passport_number",
        store=True, readonly=False,
    )
    vat = fields.Char(
        string="PAN / VAT Number",
        compute="_compute_vat", inverse="_inverse_vat",
        store=True, readonly=False,
    )

    transfer_target_company_id = fields.Many2one(
        "res.company", string="Transfer Target Branch", readonly=True,
    )
    transfer_requested_by_id = fields.Many2one(
        "res.users", string="Transfer Requested By", readonly=True,
    )
    transfer_state = fields.Selection(
        [("pending", "Pending Approval"), ("rejected", "Rejected")],
        string="Transfer Status", readonly=True,
    )

    sla_deadline = fields.Datetime(string="Follow-up SLA Deadline", readonly=True)

    def _get_channel_category(self, vals):
        medium_id = vals.get("medium_id")
        if not medium_id:
            return False
        return self.env["utm.medium"].browse(medium_id).channel_category

    def action_set_lost(self, **additional_values):
        # Native crm.lead.action_set_lost() does NOT itself enforce
        # lost_reason_id - confirmed against source, not assumed (see
        # feedback-odoo19-gotchas memory). FRS requires "Lost reason is
        # mandatory; system blocks closure without a reason" across every
        # pipeline's Closed use case, so this shared base layer enforces it
        # once for all four pipelines rather than each repeating the check.
        lost_reason_id = additional_values.get("lost_reason_id")
        for lead in self:
            if not (lost_reason_id or lead.lost_reason_id):
                raise UserError(
                    self.env._("A lost reason is mandatory when marking a lead as Lost.")
                )
        return super().action_set_lost(**additional_values)

    def action_request_transfer(self, target_company_id):
        target_company = self.env["res.company"].browse(target_company_id)
        if target_company not in self.env.user.company_ids:
            raise UserError(
                self.env._("You can only transfer a lead to a branch you have access to.")
            )
        for lead in self:
            lead.write({
                "transfer_target_company_id": target_company.id,
                "transfer_requested_by_id": self.env.user.id,
                "transfer_state": "pending",
            })

    def action_approve_transfer(self):
        for lead in self:
            # A target-branch Branch Manager approving a transfer is, by definition,
            # approving a lead still owned by a *different* company they have no
            # ordinary visibility into (native multi-company record rules would
            # otherwise block them from even reading it) - sudo() is scoped to
            # exactly this record/method, not the whole model, per this project's
            # sudo rule (CLAUDE.md Security Rules: "never sudo entire methods").
            lead_sudo = lead.sudo()
            target = lead_sudo.transfer_target_company_id
            if not target:
                raise UserError(self.env._("This lead has no pending transfer request."))
            if self.env.user not in target._get_branch_managers():
                raise UserError(self.env._(
                    "Only a Branch Manager of the target branch can approve this transfer."
                ))
            lead_sudo.write({
                "company_id": target.id,
                "transfer_target_company_id": False,
                "transfer_requested_by_id": False,
                "transfer_state": False,
            })
            lead_sudo._assign_team_matching_company()

    def action_reject_transfer(self):
        for lead in self:
            # Same cross-branch-visibility reasoning as action_approve_transfer.
            lead_sudo = lead.sudo()
            target = lead_sudo.transfer_target_company_id
            if not target:
                raise UserError(self.env._("This lead has no pending transfer request."))
            if self.env.user not in target._get_branch_managers():
                raise UserError(self.env._(
                    "Only a Branch Manager of the target branch can reject this transfer."
                ))
            lead_sudo.write({"transfer_state": "rejected"})

    customer_type = fields.Selection(
        [("individual", "Individual"), ("corporate", "Corporate")],
    )
    customer_status = fields.Selection(
        [("new_customer", "New Customer"), ("existing_customer", "Existing Customer")],
    )
    product_interested_id = fields.Many2one("crm.product", string="Product Interested")
    preferred_company_id = fields.Many2one("res.company", string="Preferred Branch")
    referred_by_id = fields.Many2one("res.partner", string="Referred By")
    staff_id = fields.Char(string="Staff ID")
    account_number = fields.Char(string="Account Number")
    nature_of_business = fields.Char(string="Nature of Business")
    annual_turnover = fields.Monetary(string="Annual Turnover", currency_field="company_currency")
    years_of_operation = fields.Integer(string="Years of Operation")
    requested_loan_amount = fields.Monetary(
        string="Requested Loan Amount", currency_field="company_currency"
    )
    purpose = fields.Selection(
        [
            ("fluctuating_working_capital", "Fluctuating Working Capital"),
            ("permanent_working_capital", "Permanent Working Capital"),
            ("term_loan_against_fixed_assets", "Term Loan Against Fixed Assets"),
        ],
        string="Loan Purpose",
    )

    @api.model_create_multi
    def create(self, vals_list):
        duplicates = []
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self._suggest_lead_title(vals)
            self._check_conditional_mandatory_fields(vals)
            duplicates.append(self._check_duplicate_record(vals))
            if not vals.get("sla_deadline"):
                deadline = self._get_sla_deadline(self._get_channel_category(vals))
                if deadline:
                    vals["sla_deadline"] = deadline
        records = super().create(vals_list)
        for record, duplicate in zip(records, duplicates):
            record._log_duplicate_override(duplicate)
        records._assign_team_matching_company()
        for record in records:
            if record.sla_deadline:
                record.activity_schedule(date_deadline=record.sla_deadline.date())
        return records

    def _assign_team_matching_company(self):
        """Branch (company_id) takes priority over native per-user team membership
        for this project's auto-assignment rule. See docs/lead.md §3.3."""
        for lead in self:
            if not lead.company_id:
                continue
            team = self.env["crm.team"].search([("company_id", "=", lead.company_id.id)], limit=1)
            if team and lead.team_id != team:
                lead.team_id = team.id

    _CONDITIONAL_MANDATORY_TRIGGER_FIELDS = (
        "customer_type", "nature_of_business", "annual_turnover", "years_of_operation",
        "customer_status", "account_number", "medium_id", "staff_id",
    )

    def write(self, vals):
        if any(f in vals for f in self._CONDITIONAL_MANDATORY_TRIGGER_FIELDS):
            for lead in self:
                lead._check_conditional_mandatory_fields(vals, existing=lead)
        duplicate_check_fields = self._get_duplicate_check_fields()
        if any(f in vals for f in duplicate_check_fields):
            for lead in self:
                check_values = {f: vals.get(f, lead[f]) for f in duplicate_check_fields}
                lead._check_duplicate_record(check_values, exclude_id=lead.id)
        return super().write(vals)

    def _check_conditional_mandatory_fields(self, vals, existing=None):
        def get(field):
            if field in vals:
                return vals[field]
            if existing is None:
                return False
            value = existing[field]
            return value.id if isinstance(value, models.BaseModel) else value

        if get("customer_type") == "corporate" and not get("nature_of_business"):
            raise ValidationError(
                self.env._("Nature of Business is mandatory for Corporate customers.")
            )
        if get("customer_type") == "corporate" and not get("annual_turnover"):
            raise ValidationError(
                self.env._("Annual Turnover is mandatory for Corporate customers.")
            )
        if get("customer_type") == "corporate" and not get("years_of_operation"):
            raise ValidationError(
                self.env._("Years of Operation is mandatory for Corporate customers.")
            )
        if get("customer_status") == "existing_customer" and not get("account_number"):
            raise ValidationError(
                self.env._("Account Number is mandatory for Existing Customer leads.")
            )
        staff_referral_medium = self.env.ref(
            self._staff_referral_medium_xmlid, raise_if_not_found=False
        )
        if (
            staff_referral_medium
            and get("medium_id") == staff_referral_medium.id
            and not get("staff_id")
        ):
            raise ValidationError(
                self.env._("Staff ID is mandatory when Lead Medium is Staff Referral.")
            )

    def _suggest_lead_title(self, vals):
        partner_name = False
        if vals.get("partner_id"):
            partner_name = self.env["res.partner"].browse(vals["partner_id"]).name
        product_name = False
        if vals.get("product_interested_id"):
            product_name = self.env["crm.product"].browse(vals["product_interested_id"]).name
        if partner_name and product_name:
            return f"{partner_name} – {product_name} Enquiry"
        if partner_name:
            return f"{partner_name} Enquiry"
        if product_name:
            return f"{product_name} Enquiry"
        return self.env._("New Enquiry")

    def _get_partner_field_update(self, field_name, force_void=True):
        """Mirror of native crm.lead._get_partner_email_update/_get_partner_phone_update,
        generalized to any partner-synced field. See docs/lead.md §2.2."""
        self.ensure_one()
        if not self.partner_id:
            return False
        lead_value = self[field_name]
        partner_value = self.partner_id[field_name]
        if (force_void or lead_value) and lead_value != partner_value:
            return True
        return False

    def _sync_compute_from_partner(self, field_name):
        for lead in self:
            partner_value = lead.partner_id[field_name]
            if partner_value and lead._get_partner_field_update(field_name):
                lead[field_name] = partner_value

    def _sync_inverse_to_partner(self, field_name):
        for lead in self:
            if lead._get_partner_field_update(field_name, force_void=False):
                lead.partner_id[field_name] = lead[field_name]

    @api.depends("partner_id.citizenship_number")
    def _compute_citizenship_number(self):
        self._sync_compute_from_partner("citizenship_number")

    def _inverse_citizenship_number(self):
        self._sync_inverse_to_partner("citizenship_number")

    @api.depends("partner_id.national_id_number")
    def _compute_national_id_number(self):
        self._sync_compute_from_partner("national_id_number")

    def _inverse_national_id_number(self):
        self._sync_inverse_to_partner("national_id_number")

    @api.depends("partner_id.passport_number")
    def _compute_passport_number(self):
        self._sync_compute_from_partner("passport_number")

    def _inverse_passport_number(self):
        self._sync_inverse_to_partner("passport_number")

    @api.depends("partner_id.vat")
    def _compute_vat(self):
        self._sync_compute_from_partner("vat")

    def _inverse_vat(self):
        self._sync_inverse_to_partner("vat")
