# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class L10n_br_trade_importDeclarationValues(models.Model):

    _name = "l10n_br_trade_import.declaration.values"
    _description = "Declaration Values"

    import_addition_id = fields.Many2one(
        comodel_name="l10n_br_trade_import.addition",
        string="Import Addition",
        required=True,
        ondelete="cascade",
    )

    import_declaration_id = fields.Many2one(
        comodel_name="l10n_br_trade_import.declaration",
        string="Import Declaration",
        related="import_addition_id.import_declaration_id",
    )

    company_currency_id = fields.Many2one(
        related="import_declaration_id.company_currency_id",
    )

    trade_currency_id = fields.Many2one(
        "res.currency",
    )

    currency_rate = fields.Float(
        digits=(12, 6),
    )

    amount_currency = fields.Monetary(
        string="Amount (Trade Currency)",
        currency_field="trade_currency_id",
    )

    amount_brl = fields.Monetary(
        string="Amount (BRL)",
        currency_field="company_currency_id",
    )

    codigo = fields.Char()
    denominacao = fields.Char()
