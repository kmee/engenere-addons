# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class L10nBrTradeImportDeclarationLine(models.Model):

    _name = "l10n_br_trade_import.declaration.line"
    _description = "L10n_br_trade_import Declaration Line"

    @api.depends("product_qty", "price_unit", "currency_rate", "import_addition_id")
    def _compute_totals(self):
        for line in self:
            line.amount_subtotal = line.product_qty * line.price_unit
            line.price_unit_brl = line.price_unit * line.currency_rate
            line.amount_brl_subtotal = (
                line.product_qty * line.price_unit * line.currency_rate
            )
            line.final_price_unit = line.price_unit + line.unit_addition_deduction
            line.final_price_unit_brl = (
                line.price_unit_brl + line.unit_addition_deduction_brl
            )

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

    is_imported = fields.Boolean(
        related="import_addition_id.is_imported",
    )

    import_declaration_number = fields.Char(
        string="DI Number",
        related="import_addition_id.import_declaration_number",
        help="Number of Import Declaration",
    )

    import_declaration_date = fields.Date(
        string="DI Date",
        related="import_addition_id.import_declaration_date",
        help="Date of Import Declaration",
    )

    addition_number = fields.Char(
        string="Number",
        help="Number of Import Addition",
        related="import_addition_id.addition_number",
    )

    addtion_sequence = fields.Integer(
        string="Sequence",
        required=True,
        help="Sequential number of the item within the Addition",
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )

    product_description = fields.Char()

    product_qty = fields.Float(digits=(14, 8))

    product_uom = fields.Char()

    price_unit = fields.Monetary(
        digits=(14, 8),
        currency_field="trade_currency_id",
    )

    price_unit_brl = fields.Monetary(
        digits=(14, 8),
        currency_field="company_currency_id",
        compute="_compute_totals",
    )

    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")

    company_currency_id = fields.Many2one(
        "res.currency",
        related="import_addition_id.company_currency_id",
    )

    trade_currency_id = fields.Many2one(
        "res.currency",
        related="import_addition_id.trade_currency_id",
    )

    currency_rate = fields.Float(
        digits=(12, 8),
        related="import_addition_id.currency_rate",
    )

    amount_subtotal = fields.Monetary(
        string="Subtotal",
        digits=(14, 8),
        currency_field="trade_currency_id",
        compute="_compute_totals",
    )

    amount_brl_subtotal = fields.Monetary(
        string="Subtotal",
        digits=(14, 8),
        currency_field="company_currency_id",
        compute="_compute_totals",
    )

    average_addition_deduction = fields.Monetary(
        string="Add/Dec",
        digits=(14, 8),
        currency_field="trade_currency_id",
    )

    average_addition_deduction_brl = fields.Monetary(
        string="Add/Dec",
        digits=(14, 8),
        currency_field="company_currency_id",
    )

    unit_addition_deduction = fields.Monetary(
        string="Add/Dec",
        digits=(14, 8),
        currency_field="trade_currency_id",
    )

    unit_addition_deduction_brl = fields.Monetary(
        string="Add/Dec",
        digits=(14, 8),
        currency_field="company_currency_id",
    )

    final_price_unit = fields.Monetary(
        string="Subtotal",
        digits=(14, 8),
        currency_field="trade_currency_id",
        compute="_compute_totals",
    )

    final_price_unit_brl = fields.Monetary(
        string="Total",
        digits=(14, 8),
        currency_field="company_currency_id",
        compute="_compute_totals",
    )
