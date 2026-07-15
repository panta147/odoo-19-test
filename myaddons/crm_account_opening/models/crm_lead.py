import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    _LOCK_ONCE_SET_FIELDS = ("kycms_crm_id", "aos_crm_id")
    _SYNC_ONLY_FIELDS = (
        "kycms_status", "aos_status", "aos_account_number", "aos_cif_id",
        "aos_rejection_reason",
    )

    expected_initial_deposit = fields.Monetary(
        string="Expected Initial Deposit", currency_field="company_currency",
    )
    expected_account_opening_date = fields.Date(string="Expected Account Opening Date")
    deposit_term = fields.Integer(string="Term (months)")

    kycms_crm_id = fields.Char(string="KYCMS CRM ID")
    kycms_status = fields.Selection(
        [("sent", "Sent"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        string="KYCMS Status", readonly=True,
    )

    aos_crm_id = fields.Char(string="AOS CRM ID")
    aos_status = fields.Selection(
        [("sent", "Sent"), ("approved", "Approved"), ("rejected", "Rejected")],
        string="AOS Status", readonly=True,
    )
    aos_account_number = fields.Char(string="AOS Account Number", readonly=True)
    aos_cif_id = fields.Char(string="AOS CIF ID", readonly=True)
    aos_rejection_reason = fields.Text(string="AOS Rejection Reason", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_deposit_term_mandatory(vals)
            self._default_stage_to_enquiry(vals)
        return super().create(vals_list)

    def _default_stage_to_enquiry(self, vals):
        """Native crm.lead._stage_find() picks the globally lowest
        (sequence, id) crm.stage whose team_ids is empty or matches the
        lead's team - across every installed pipeline, not just this one.
        Since this pipeline's stages deliberately have no team_ids (see
        data/crm_stage_data.xml), that native lookup can hand a brand-new
        Account Opening lead a stage that belongs to a completely different
        pipeline (or native demo data), violating the FRS's own "Opportunity
        created in Enquiry stage" postcondition (LM-AC-001). Found via live
        manual testing, not assumed - see feedback-odoo19-gotchas memory.
        """
        if vals.get("stage_id"):
            return
        product_id = vals.get("product_interested_id")
        if not product_id:
            return
        product = self.env["crm.product"].browse(product_id)
        if product.product_family == "account_opening":
            vals["stage_id"] = self.env.ref("crm_account_opening.stage_enquiry").id

    def write(self, vals):
        for field_name in self._LOCK_ONCE_SET_FIELDS:
            if field_name in vals:
                for lead in self:
                    if lead[field_name] and lead[field_name] != vals[field_name]:
                        raise ValidationError(self.env._(
                            "%(field)s cannot be changed once set.",
                            field=self._fields[field_name].string,
                        ))
        # AOS/KYCMS-sourced fields: readonly=True on the field definition only
        # affects default view rendering, NOT actual write access - confirmed
        # empirically, not assumed (see feedback-odoo19-gotchas memory). These
        # values must only ever come from the future crm_api callback layer
        # (docs/account_opening.md §3.9, "non-editable in CRM" - a repeated,
        # explicit FRS requirement), so a direct write is blocked unless the
        # caller is this module's own stub-callback methods (which set the
        # crm_api_sync context flag), mirroring the exact pattern
        # docs/retail_lending.md §4 already proposes for the same situation.
        if any(f in vals for f in self._SYNC_ONLY_FIELDS) and not self.env.context.get(
            "crm_api_sync"
        ):
            raise UserError(self.env._(
                "AOS/KYCMS-sourced fields can only be updated by the integration sync, not edited directly."
            ))
        return super().write(vals)

    def _apply_kycms_status_update(self, status):
        """Stub for the future crm_api KYCMS callback (LM-AC-002/§3.8) - not yet
        wired to a real HTTP endpoint, but this is the method that callback will
        eventually invoke once crm_api is built."""
        self.ensure_one()
        self.with_context(crm_api_sync=True).write({"kycms_status": status})
        _logger.info(
            "crm_account_opening lead_id=%s operation=kycms_status_update status=%s",
            self.id, status,
        )
        if status == "accepted":
            self.stage_id = self.env.ref(
                "crm_account_opening.stage_account_opening_in_process"
            ).id
            _logger.info(
                "crm_account_opening lead_id=%s operation=stage_advance stage=account_opening_in_process",
                self.id,
            )

    def _is_closed(self):
        self.ensure_one()
        return self.stage_id in (
            self.env.ref("crm_account_opening.stage_closed_won"),
            self.env.ref("crm_account_opening.stage_closed_lost"),
        )

    def _apply_aos_approval(self, account_number, cif_id):
        """Stub for the future crm_api AOS Approval callback (LM-AC-003/§3.10).

        A duplicate/late callback must not alter an already-closed lead -
        AOS/network retries can resend a callback after CRM has already
        acted on the first one (docs/account_opening.md doesn't specify this
        idempotency requirement explicitly, but the QA test-case spreadsheet
        test_cases_LM-AC-003.xlsx TC-LM-AC-003-06 does, and it's a real gap
        without this guard - confirmed via a failing test, not assumed).
        """
        self.ensure_one()
        if self._is_closed():
            _logger.info(
                "crm_account_opening lead_id=%s operation=aos_approval ignored=already_closed",
                self.id,
            )
            return
        self.with_context(crm_api_sync=True).write({
            "aos_status": "approved",
            "aos_account_number": account_number,
            "aos_cif_id": cif_id,
        })
        # Never log account_number/cif_id themselves - Sensitive Banking Data
        # per CLAUDE.md Logging Rules; the operation + lead_id is enough for
        # an audit trail without exposing the actual banking data.
        _logger.info(
            "crm_account_opening lead_id=%s operation=aos_approval -> stage=closed_won",
            self.id,
        )
        self.stage_id = self.env.ref("crm_account_opening.stage_closed_won").id

    def _apply_aos_rejection(self, reason):
        """Stub for the future crm_api AOS Rejection callback (LM-AC-003/§3.11).

        Maps AOS's free-text rejection reason onto crm.lost.reason by
        find-or-create on the exact text - a concrete resolution of the
        gap docs/account_opening.md §6 item 5 flags as undecided (fixed
        lookup table vs. auto-create per distinct text); auto-create was
        chosen since AOS's real reason vocabulary is not yet known.

        Also ignores a duplicate/late callback on an already-closed lead -
        see _apply_aos_approval's docstring for why.
        """
        self.ensure_one()
        if self._is_closed():
            _logger.info(
                "crm_account_opening lead_id=%s operation=aos_rejection ignored=already_closed",
                self.id,
            )
            return
        lost_reason = self.env["crm.lost.reason"].search([("name", "=", reason)], limit=1)
        if not lost_reason:
            lost_reason = self.env["crm.lost.reason"].create({"name": reason})
        self.with_context(crm_api_sync=True).write({
            "aos_status": "rejected",
            "aos_rejection_reason": reason,
            "lost_reason_id": lost_reason.id,
        })
        _logger.info(
            "crm_account_opening lead_id=%s operation=aos_rejection -> stage=closed_lost",
            self.id,
        )
        self.stage_id = self.env.ref("crm_account_opening.stage_closed_lost").id

    def _check_deposit_term_mandatory(self, vals):
        product_id = vals.get("product_interested_id")
        if not product_id:
            return
        product = self.env["crm.product"].browse(product_id)
        if product.is_fixed_deposit and not vals.get("deposit_term"):
            raise ValidationError(
                self.env._("Term (months) is mandatory for fixed-deposit products.")
            )
