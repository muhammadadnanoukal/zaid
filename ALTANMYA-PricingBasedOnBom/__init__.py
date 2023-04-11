from . import models
from odoo import api, fields, SUPERUSER_ID


def _set_route_type(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    mf = env['stock.route'].sudo().search([('name', 'ilike', 'Manufacture')], limit=1)
    mf.write({'type': 'mf'})
    deliver = env['stock.route'].sudo().search([('name', 'ilike', 'Deliver')], limit=1)
    deliver.write({'type': 'deliver'})
