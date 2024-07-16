# Copyright (C) 2022-Today - Engenere (<https://engenere.one>).
# @author Antônio S. Pereira Neto <neto@engenere.one>
# Copyright (C) 2024-Today - KMEE (<https://kmee.com.br>).
# @author Luis Felipe Miléo <mileo@kmee.com.br>

import base64
import re
from datetime import datetime

from xsdata.formats.dataclass.parsers import XmlParser

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form

from ..utils.lista_declaracoes import ListaDeclaracoes

READONLY_STATES = {
    "open": [("readonly", True)],
    "cancelled": [("readonly", True)],
    "locked": [("readonly", True)],
}


class ImportDeclaration(models.Model):
    _name = "l10n_br_trade_import.declaration"

    _description = "Import Declaration"
    _rec_name = "document_number"
    _order = "document_date desc, document_number desc, id desc"

    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def _default_fiscal_operation(self):
        # return self.env.company.import_declaration_fiscal_operation_id
        return self.env.ref("l10n_br_fiscal.fo_compras")

    @api.model
    def _fiscal_operation_domain(self):
        domain = [("state", "=", "approved")]
        return domain

    fiscal_operation_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.operation",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_default_fiscal_operation,
        domain=lambda self: self._fiscal_operation_domain(),
    )

    document_number = fields.Char(states=READONLY_STATES, help="Document Nº")

    document_date = fields.Date(
        states=READONLY_STATES,
        string="Registration Date",
    )

    # Local de desembaraço Aduaneiro
    customs_clearance_location = fields.Char(
        states=READONLY_STATES, help="Customs Clearance Location"
    )

    # Estado onde ocorreu o Desembaraço Aduaneiro
    customs_clearance_state_id = fields.Many2one(
        string="Custom Clearance Stage",
        comodel_name="res.country.state",
        states=READONLY_STATES,
        domain=[("country_id.code", "=", "BR")],
    )

    # Data do Desembaraço Aduaneiro
    customs_clearance_date = fields.Date(
        states=READONLY_STATES, help="Customs Clearance Date"
    )

    # Via de transporte internacional informada na Declaração
    # de Importação (DI)
    transportation_type = fields.Selection(
        selection=[
            ("maritime", "Maritime"),
            ("fluvial", "Fluvial"),
            ("lacustrine", "Lacustrine"),
            ("aerial", "Aerial"),
            ("postal", "Postal"),
            ("rail", "Rail"),
            ("road", "Road"),
            ("conduit", "Conduct/Transmission Network"),
            ("own_means", "Own Means"),
            ("fict_in_out", "Fictitious In/Out"),
            ("courier", "Courier"),
            ("in_hands", "In hands"),
            ("towing", "By towing."),
        ],
        states=READONLY_STATES,
        string="Transport Route",
        help="International transport route reported in the Import Declaration (DI)",
    )

    # Valor da AFRMM - Adicional ao Frete para Renovação da
    # Marinha Mercante
    afrmm_value = fields.Monetary(
        string="AFRMM",
        help="Additional Freight for Merchant Navy Renewal",
        currency_field="company_currency_id",
    )

    # Forma de importação quanto a intermediação
    intermediary_type = fields.Selection(
        selection=[
            ("conta_propria", "Conta Própria"),
            ("conta_ordem", "Conta e Ordem"),
            ("encomenda", "Encomenda"),
        ],
        states=READONLY_STATES,
        string="Intermediation",
        help="Form of import regarding intermediation",
    )

    # Parceiro adquirente ou encomendante
    third_party_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Acquirer or the Orderer",
        help="Acquirer or the Orderer Partner.\n"
        "Required when intermediation is 'Conta e Ordem' or 'Encomenda'",
    )

    # Exportador
    exporting_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Exporting Partner",
    )

    is_imported = fields.Boolean(
        string="Is Imported",
        readonly=True,
    )

    declaration_file = fields.Binary(
        string="Imported File",
        attachment=True,
    )

    account_move_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        readonly=True,
        ondelete="restrict",
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("open", "Open"),
            ("locked", "Loked"),
            ("canceled", "Canceled"),
        ],
        default="draft",
        required=True,
        copy=False,
        tracking=True,
    )

    amount_currency = fields.Monetary(
        string="Amount (Trade Currency)",
        currency_field="trade_currency_id",
    )

    amount_reais = fields.Monetary(
        string="Amount (BRL)",
        currency_field="company_currency_id",
    )

    trade_currency_id = fields.Many2one(
        "res.currency",
    )

    currency_rate = fields.Float(
        digits=(12, 6),
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )

    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )

    freight_currency_id = fields.Many2one(
        "res.currency",
    )

    amount_freight = fields.Monetary(
        currency_field="freight_currency_id",
    )

    amount_freight_brl = fields.Monetary(
        currency_field="company_currency_id",
    )

    insurance_currency_id = fields.Many2one(
        "res.currency",
    )

    amount_insurance = fields.Monetary(
        currency_field="insurance_currency_id",
    )

    amount_insurance_brl = fields.Monetary(
        currency_field="company_currency_id",
    )

    other_costs_currency_id = fields.Many2one(
        "res.currency",
    )

    amount_other_costs = fields.Monetary(
        currency_field="other_costs_currency_id",
    )

    amount_other_costs_brl = fields.Monetary(
        currency_field="company_currency_id",
    )

    additional_information = fields.Text()

    addition_ids = fields.One2many(
        comodel_name="l10n_br_trade_import.addition",
        inverse_name="import_declaration_id",
        string="Additions",
    )

    line_ids = fields.One2many(
        comodel_name="l10n_br_trade_import.declaration.line",
        inverse_name="import_declaration_id",
        string="Product Lines",
    )

    value_ids = fields.One2many(
        comodel_name="l10n_br_trade_import.declaration.values",
        inverse_name="import_declaration_id",
        string="Values",
    )

    other_costs_ids = fields.One2many(
        comodel_name="l10n_br_trade_import.declaration.other_costs",
        inverse_name="import_declaration_id",
    )

    @api.constrains("intermediary_type", "third_party_partner_id")
    def _check_third_party_partner_id(self):
        for di in self:
            if (
                di.intermediary_type in ["conta_ordem", "encomenda"]
                and not di.third_party_partner_id
            ):
                raise UserError(
                    _(
                        "When the intermediation is 'Conta e Ordem' or 'Encomenda' "
                        "you must provide the Acquirer or Orderer's information"
                    )
                )

    @api.constrains("transportation_type", "afrmm_value")
    def _check_AFRMM_value(self):
        for di in self:
            if di.transportation_type == "maritime" and di.afrmm_value == 0:
                raise UserError(
                    _(
                        "When the international transport route is 'Maritime'\n"
                        "You must inform the AFRMM value."
                    )
                )

    def action_confirm(self):
        self.write({"state": "open"})

    def action_generate_invoice(self):
        self.ensure_one()
        if self.state != "open":
            raise UserError(_("Only open declarations can generate invoices."))
        self._generate_invoice()

    def action_back2draft(self):
        self.write({"state": "draft"})

    def action_cancel(self):
        self.write({"state": "canceled"})

    def button_compute_average(self):
        for record in self:
            for line in record.addition_ids:
                line.inverse_amount_addition_deuction()

    def _generate_invoice(self):
        move_form = Form(
            self.env["account.move"].with_context(
                default_move_type="in_invoice",
                account_predictive_bills_disable_prediction=True,
            )
        )
        move_form.invoice_date = fields.Date.today()
        move_form.date = move_form.invoice_date
        move_form.partner_id = self.exporting_partner_id
        # move_form.currency_id =

        # extra BR fiscal params:
        move_form.document_type_id = self.env.ref("l10n_br_fiscal.document_55")
        move_form.document_serie_id = self.env.ref("l10n_br_fiscal.document_55_serie_1")
        move_form.issuer = "company"
        move_form.fiscal_operation_id = self.fiscal_operation_id

        for addition in self.addition_ids:
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = addition.product_id
                line_form.quantity = addition.product_qty
                line_form.import_addition_ids.add(addition)

        invoice = move_form.save()
        self.write({"account_move_id": invoice.id, "state": "locked"})

    def import_declaration(self, declaration_file):
        file_content = base64.b64decode(declaration_file)
        # try:

        xml_data = file_content.decode("utf-8")
        # Create an XML parser
        parser = XmlParser()
        # Parse XML data into data class
        declaration_list = parser.from_string(xml_data, ListaDeclaracoes)
        vals = self._parse_declaration(declaration_list)
        vals["declaration_file"] = declaration_file
        return self.create(vals)

        # except Exception:
        #     raise UserError(_("Invalid XML file"))

    def _prepare_addition_vals(self, adicao):
        declaration_lines = []

        trade_currency_id = self.env["res.currency"].search(
            [("siscomex_code", "=", adicao.condicao_venda_moeda_codigo)],
            limit=1,
        )
        amount_reais = int(adicao.condicao_venda_valor_reais) / 100
        amount_currency = int(adicao.condicao_venda_valor_moeda) / 100
        if amount_currency and amount_reais:
            currency_rate = amount_reais / amount_currency
        else:
            currency_rate = 0

        vals = {
            "amount_brl": amount_reais,
            "amount_currency": amount_currency,
            "currency_rate": currency_rate,
            "trade_currency_id": trade_currency_id.id if trade_currency_id else False,
            "addition_number": adicao.numero_adicao,
        }

        if adicao.fabricante_nome:
            manufacturer_id = self.env["res.partner"].search(
                [("name", "=", adicao.fabricante_nome)]
            )
            if not manufacturer_id:
                manufacturer_id = self.env["res.partner"].create(
                    {
                        "name": adicao.fabricante_nome,
                        "legal_name": adicao.fabricante_nome,
                        "street_number": adicao.fabricante_numero,
                        "street": adicao.fabricante_logradouro,
                        "city": adicao.fabricante_cidade,
                    }
                )
            vals.update(
                {
                    "manufacturer_id": manufacturer_id.id,
                }
            )

        acrescimo_deducao = []

        if type(adicao.acrescimo) == list or type(adicao.deducao) == list:
            raise NotImplementedError

        # for acrescimo in adicao.acrescimo:
        if adicao.acrescimo:
            trade_currency_id = self.env["res.currency"].search(
                [("siscomex_code", "=", adicao.acrescimo.moeda_negociada_codigo)],
                limit=1,
            )
            amount_reais = int(adicao.acrescimo.valor_reais) / 100
            amount_currency = int(adicao.acrescimo.valor_moeda_negociada) / 100
            if amount_currency and amount_reais:
                currency_rate = amount_reais / amount_currency
            else:
                currency_rate = 0

            acrescimo_deducao.append(
                {
                    "amount_brl": amount_reais,
                    "codigo": adicao.acrescimo.codigo_acrescimo,
                    "denominacao": adicao.acrescimo.denominacao,
                    "amount_currency": amount_currency,
                    "currency_rate": currency_rate,
                    "trade_currency_id": trade_currency_id.id
                    if trade_currency_id
                    else False,
                }
            )
        # for deducao in adicao.deducao:
        if adicao.deducao:
            trade_currency_id = self.env["res.currency"].search(
                [("siscomex_code", "=", adicao.deducao.moeda_negociada_codigo)],
                limit=1,
            )
            amount_reais = int(adicao.deducao.valor_reais) / 100
            amount_currency = int(adicao.deducao.valor_moeda_negociada) / 100
            if amount_currency and amount_reais:
                currency_rate = amount_reais / amount_currency
            else:
                currency_rate = 0

            acrescimo_deducao.append(
                {
                    "amount_brl": amount_reais * -1,
                    "codigo": adicao.deducao.codigo_deducao,
                    "denominacao": adicao.deducao.denominacao,
                    "amount_currency": amount_currency * -1,
                    "currency_rate": currency_rate,
                    "trade_currency_id": trade_currency_id.id
                    if trade_currency_id
                    else False,
                }
            )

        if acrescimo_deducao:
            vals["value_ids"] = [(0, 0, x) for x in acrescimo_deducao]

        for mercadoria in adicao.mercadoria:
            declaration_lines.append(
                {
                    "addtion_sequence": int(mercadoria.numero_sequencial_item),
                    "product_description": mercadoria.descricao_mercadoria,
                    "product_qty": int(mercadoria.quantidade) / 100000,
                    "product_uom": mercadoria.unidade_medida,
                    "price_unit": int(mercadoria.valor_unitario) / 10000000,
                }
            )
        if declaration_lines:
            vals["line_ids"] = [(0, 0, x) for x in declaration_lines]
        return vals

    def _demonstrativo_calculo(self, text):
        # Regex para capturar os dados do DEMONSTRATIVO DE CALCULOS
        pattern = re.compile(r"DEMONSTRATIVO DE CALCULOS:\n(.*?)(?:\n\n|$)", re.DOTALL)
        match = pattern.search(text)

        # Se encontrar uma correspondência, extrai os cálculos
        if match:
            calc_text = match.group(1)

            # Regex para capturar os itens e valores
            item_pattern = re.compile(r"([A-Z\s\.\-\(\)]+)\.+: R\$ ([\d\.,]+)")
            calculations = {}

            for item in item_pattern.findall(calc_text):
                if len(item) == 2:  # Verifica se há exatamente dois grupos capturados
                    nome, valor = item
                    calculations[nome.strip()] = float(
                        valor.replace(".", "").replace(",", ".")
                    )

            # Exibir o dicionário com os cálculos
            print(calculations)
        else:
            print("Nenhum dado encontrado no DEMONSTRATIVO DE CALCULOS.")

    def _sum_siscomex(self, text):
        # Expressão regular para encontrar as taxas SISCOMEX
        padrao = r"TAXA SISCOMEX\.+: R\$ (\d+,\d{2})"

        # Encontrar todas as ocorrências
        taxas = re.findall(padrao, text)

        # Converter as taxas para float e somá-las
        soma = sum(float(taxa.replace(",", ".")) for taxa in taxas)

        return soma or 0

    def _parse_declaration(self, declaracoes):
        if declaracoes.declaracao_importacao:

            addition_lines = []

            for adicao in declaracoes.declaracao_importacao.adicao:
                addition_lines.append(self._prepare_addition_vals(adicao))

            document_date = datetime.strptime(
                str(declaracoes.declaracao_importacao.data_registro), "%Y%m%d"
            ).date()

            insurance_currency_id = self.env["res.currency"].search(
                [
                    (
                        "siscomex_code",
                        "=",
                        declaracoes.declaracao_importacao.seguro_moeda_negociada_codigo,
                    )
                ],
                limit=1,
            )
            freight_currency_id = self.env["res.currency"].search(
                [
                    (
                        "siscomex_code",
                        "=",
                        declaracoes.declaracao_importacao.frete_moeda_negociada_codigo,
                    )
                ],
                limit=1,
            )

            vals = {
                "document_number": declaracoes.declaracao_importacao.numero_di,
                "document_date": document_date,
                "is_imported": True,
                "addition_ids": [(0, 0, x) for x in addition_lines],
                "amount_reais": int(
                    declaracoes.declaracao_importacao.local_embarque_total_reais
                )
                / 100,
                "amount_currency": int(
                    declaracoes.declaracao_importacao.local_embarque_total_dolares
                )
                / 100,
                "additional_information": (
                    declaracoes.declaracao_importacao.informacao_complementar
                ),
                "amount_freight_brl": int(
                    declaracoes.declaracao_importacao.frete_total_reais
                )
                / 100,
                "amount_freight": int(
                    declaracoes.declaracao_importacao.frete_total_moeda
                )
                / 100,
                "amount_insurance": int(
                    declaracoes.declaracao_importacao.seguro_total_moeda_negociada
                )
                / 100,
                "amount_insurance_brl": int(
                    declaracoes.declaracao_importacao.seguro_total_reais
                )
                / 100,
                "insurance_currency_id": insurance_currency_id.id
                if insurance_currency_id
                else False,
                "freight_currency_id": freight_currency_id.id
                if freight_currency_id
                else False,
                "amount_other_costs_brl": self._sum_siscomex(
                    declaracoes.declaracao_importacao.informacao_complementar
                ),
            }

            return vals
