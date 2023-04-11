import logging
_logger = logging.getLogger(__name__)
from collections import defaultdict

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import float_compare, OrderedSet

class StockRule(models.Model):
    _inherit = 'stock.rule'

    # @api.model
    # def _run_manufacture(self, procurements):
    #     productions_values_by_company = defaultdict(list)
    #     i = 0
    #     for procurement, rule in procurements:
    #         if float_compare(procurement.product_qty, 0, precision_rounding=procurement.product_uom.rounding) <= 0:
    #             # If procurement contains negative quantity, don't create a MO that would be for a negative value.
    #             continue
    #         bom_ids = self.env['sale.order'].search([('name', '=', procurement.origin)]).order_line.mo_bom_id
    #         bom_ids_with_type = self.env['mrp.bom'].browse(bom_ids.ids).filtered(lambda bom: bom.type == 'normal')
    #         print('i', i)
    #         print('bom_ids', bom_ids)
    #         print('bom_ids_with_type', bom_ids_with_type)
    #         if len(bom_ids) == len(bom_ids_with_type):
    #             bom = \
    #             rule._get_matching_bom(procurement.product_id, procurement.company_id, procurement.values, bom_ids_with_type[i])[i]
    #             i += 1
    #             print('bom_manuf', bom)
    #         else:
    #             bom = \
    #                 rule._get_matching_bom(procurement.product_id, procurement.company_id, procurement.values)
    #             print('bom', bom)
    #
    #         productions_values_by_company[procurement.company_id.id].append(rule._prepare_mo_vals(*procurement, bom))
    #
    #     for company_id, productions_values in productions_values_by_company.items():
    #         # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
    #         productions = self.env['mrp.production'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(
    #             productions_values)
    #         productions.filtered(lambda p: (not p.orderpoint_id and p.move_raw_ids) or \
    #                                        (
    #                                                    p.move_dest_ids.procure_method != 'make_to_order' and not p.move_raw_ids and not p.workorder_ids)).action_confirm()
    #
    #         for production in productions:
    #             origin_production = production.move_dest_ids and production.move_dest_ids[
    #                 0].raw_material_production_id or False
    #             orderpoint = production.orderpoint_id
    #             if orderpoint and orderpoint.create_uid.id == SUPERUSER_ID and orderpoint.trigger == 'manual':
    #                 production.message_post(
    #                     body=_('This production order has been created from Replenishment Report.'),
    #                     message_type='comment',
    #                     subtype_xmlid='mail.mt_note')
    #             elif orderpoint:
    #                 production.message_post_with_view(
    #                     'mail.message_origin_link',
    #                     values={'self': production, 'origin': orderpoint},
    #                     subtype_id=self.env.ref('mail.mt_note').id)
    #             elif origin_production:
    #                 production.message_post_with_view(
    #                     'mail.message_origin_link',
    #                     values={'self': production, 'origin': origin_production},
    #                     subtype_id=self.env.ref('mail.mt_note').id)
    #     return True
    #
    # def _get_matching_bom(self, product_id, company_id, values, bom_ids=False):
    #     if values.get('bom_id', False):
    #         return values['bom_id']
    #     if bom_ids:
    #         return self.env['mrp.bom']._bom_find(product_id, picking_type=self.picking_type_id, bom_type='normal', company_id=company_id.id, bom_ids=bom_ids)[product_id]
    #     else:
    #         return self.env['mrp.bom']._bom_find(product_id, picking_type=self.picking_type_id, bom_type='normal',
    #                                              company_id=company_id.id)[product_id]