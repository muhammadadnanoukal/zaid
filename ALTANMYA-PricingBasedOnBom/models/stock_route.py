# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.tools.sql import column_exists, create_column


class StockRoute(models.Model):
    _inherit = "stock.route"
    type = fields.Selection(
        selection=[
            ('deliver', "Deliver"),
            ('mf', "Manufacture"),
        ],
        string="Type",
        default=False)