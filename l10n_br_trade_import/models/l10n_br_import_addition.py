# Copyright (C) 2022-Today - Engenere (<https://engenere.one>).
# @author Antônio S. Pereira Neto <neto@engenere.one>
# Copyright (C) 2024-Today - KMEE (<https://kmee.com.br>).
# @author Luis Felipe Miléo <mileo@kmee.com.br>

from odoo import api, fields, models


class ImportAddition(models.Model):
    _name = "l10n_br_trade_import.addition"
    _description = "Import Addition"
    _rec_name = "addition_number"

    @api.depends("value_ids")
    def _compute_totals(self):
        for record in self:
            record.amount_addition_deduction = sum(
                line.amount_currency for line in record.value_ids
            )
            record.amount_addition_deduction_brl = sum(
                line.amount_brl for line in record.value_ids
            )

    import_declaration_id = fields.Many2one(
        comodel_name="l10n_br_trade_import.declaration",
        string="Import Declaration",
        required=True,
        ondelete="cascade",
    )

    is_imported = fields.Boolean(
        related="import_declaration_id.is_imported",
    )

    import_declaration_number = fields.Char(
        string="DI Number",
        related="import_declaration_id.document_number",
        help="Number of Import Declaration",
    )

    import_declaration_date = fields.Date(
        string="DI Date",
        related="import_declaration_id.document_date",
        help="Date of Import Declaration",
    )

    addition_number = fields.Char(
        string="Number", required=True, help="Number of Import Addition"
    )

    manufacturer_id = fields.Many2one(
        comodel_name="res.partner",
        # required=True,
        help="Foreign Manufacturer",
    )

    deduction_value = fields.Float(
        string="Deducao", help="Discount value of the DI item - Addition"
    )

    add_value = fields.Float(
        string="Acrescimo", help="Add value of the DI item - Addition"
    )

    drawback = fields.Char(string="Drawback", help="Drawback concession act number")

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

    line_ids = fields.One2many(
        comodel_name="l10n_br_trade_import.declaration.line",
        inverse_name="import_addition_id",
        string="Lines",
    )

    value_ids = fields.One2many(
        comodel_name="l10n_br_trade_import.declaration.values",
        inverse_name="import_addition_id",
        string="Values",
    )

    amount_addition_deduction = fields.Monetary(
        string="Addition/Deduction",
        currency_field="trade_currency_id",
        compute="_compute_totals",
    )

    amount_addition_deduction_brl = fields.Monetary(
        string="Addition/Deduction",
        currency_field="company_currency_id",
        compute="_compute_totals",
    )

    def inverse_amount_addition_deuction(self):
        for record in self:
            for line in record.line_ids:

                avg_cost = record.import_declaration_id.amount_other_costs_brl * (
                    line.amount_brl_subtotal / record.amount_brl
                )

                line.average_addition_deduction = record.amount_addition_deduction * (
                    line.amount_subtotal / record.amount_currency
                )
                line.unit_addition_deduction = (
                    line.average_addition_deduction / line.product_qty
                )

                line.average_addition_deduction_brl = (
                    abs(
                        record.amount_addition_deduction_brl
                        * (
                            line.amount_brl_subtotal
                            / record.import_declaration_id.amount_reais
                        )
                    )
                    + avg_cost
                )

                line.unit_addition_deduction_brl = (
                    record.amount_addition_deduction_brl
                    * (line.amount_brl_subtotal / record.amount_brl)
                ) / line.product_qty
