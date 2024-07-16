# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class L10n_br_trade_importDeclarationOther_costs(models.Model):

    _name = "l10n_br_trade_import.declaration.other_costs"
    _description = "L10n_br_trade_import Declaration Other Costs"

    def _compute_amount_other(self):
        for record in self:
            if record.is_rated:
                record.amount_other = record.amount
            else:
                record.amount_other = 0

    import_declaration_id = fields.Many2one(
        comodel_name="l10n_br_trade_import.declaration",
        string="Import Declaration",
        required=True,
        ondelete="cascade",
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency", related="import_declaration_id.company_currency_id"
    )

    name = fields.Char(string="Name", required=True)

    amount = fields.Monetary(string="Amount", required=True)

    is_rated = fields.Boolean(string="Is Allocation")

    amount_other = fields.Monetary(
        string="Amount Other", computed="_compute_amount_other"
    )
