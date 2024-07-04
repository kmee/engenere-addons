# Copyright 2024 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class L10n_br_trade_importDeclarationWizard(models.TransientModel):

    _name = "l10n_br_trade_import.declaration.wizard"

    declaration_file = fields.Binary()

    def doit(self):
        result_ids = []

        for wizard in self:
            declaration = self.env['l10n_br_trade_import.declaration'].create({
                'declaration_file': wizard.declaration_file,
            })
            declaration.import_declaration()
            result_ids.append(declaration.id)
        action = {
            "type": "ir.actions.act_window",
            "name": "Import Declaration",
            "res_model": "l10n_br_trade_import.declaration",
            "domain": [("id", "=", result_ids)],
            "view_mode": "form,tree",
        }
        return action
