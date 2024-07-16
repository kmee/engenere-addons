# Copyright (C) 2023-Today - Engenere (<https://engenere.one>).
# @author Antônio S. Pereira Neto <neto@engenere.one>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Import Declaration Management",
    "summary": "Managing Brazilian Import Declarations",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "Engenere, KMEE, Odoo Community Association (OCA)",
    "maintainers": ["antoniospneto", "felipemotter", "mileo"],
    "website": "https://github.com/OCA/l10n-brazil",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "depends": [
        "l10n_br_nfe",
        "l10n_br_account",
    ],
    "demo": [
        "demo/l10n_br_trade_import_declaration_values.xml",
        "demo/l10n_br_trade_import_declaration_line.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        #
        "wizards/l10n_br_trade_import_declaration_wizard.xml",
        #
        "views/menu.xml",
        #
        "views/import_declaration_other_costs.xml",
        "views/import_declaration_values.xml",
        "views/import_declaration_view.xml",
        "views/import_declaration_line_view.xml",
        "views/import_addition_view.xml",
        #
        "views/account_move_view.xml",
        "views/nfe_adi_view.xml",
        "views/nfe_di_view.xml",
        "views/nfe_document_view.xml",
        "views/res_currency_view.xml",
        #
        "data/res_currency_data.xml",
    ],
    "installable": True,
    "external_dependencies": {
        "python": ["xsdata"],
    },
}
