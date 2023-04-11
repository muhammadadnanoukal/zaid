import logging
from odoo import api, fields, models, _
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    customize = fields.Boolean(string='Customize Products')
    estimated_installation_date_total = fields.Float(string="Estimated Installation Days", store=True, tracking=4,
                                                     readonly=True, compute='_compute_installation_amounts')

    def update_prices_from_bom(self):
        self.ensure_one()
        lines_to_update = []
        for line in self.order_line:
            lines_to_update.append((1, line.id, {'price_unit': line.mo_bom_id.total_amount}))
        self.update({'order_line': lines_to_update})
        # self.show_update_price_unit = False
        self.message_post(body=_("Product prices have been recomputed according to each bom selected"))

    @api.depends('order_line.total_installation_date_1')
    def _compute_installation_amounts(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            order.estimated_installation_date_total = sum(order_lines.mapped('total_installation_date_1'))

    def _action_confirm(self):
        self.order_line._action_launch_stock_rule()
        for order in self:
            if any(expense_policy not in [False, 'no'] for expense_policy in
                   order.order_line.mapped('product_id.expense_policy')):
                if not order.analytic_account_id:
                    order._create_analytic_account()
        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    mo_bom_id = fields.Many2one('mrp.bom', 'Components')

    @api.onchange('mo_bom_id')
    def _onchange_mo_bom_id(self):
        if self.mo_bom_id.type == 'phantom':
            self.route_id = self.env['stock.route'].search([('type', '=', 'deliver')], limit=1).id
        elif self.mo_bom_id.type == 'normal':
            self.route_id = self.env['stock.route'].search([('type', '=', 'mf')], limit=1).id

    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', related="order_id.pricelist_id", store=True,
                                   readonly=False)
    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)

    # price_unit = fields.Float('Unit Price', required=True, related="mo_bom_id.total_amount", store=True)
    testing_price = fields.Float("customize price", related="mo_bom_id.total_amount")
    estimated_installation_date_from_mrp = fields.Float(related="mo_bom_id.bom_line_ids.estimated_installation_date")
    total_installation_date_1 = fields.Float('Total Installation Days',
                                             store=True, compute='_compute_estimated_installation_date_total')

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'mo_bom_id')
    def _compute_price_unit(self):
        for line in self:
            if line.mo_bom_id:
                line.price_unit = line.mo_bom_id.total_amount
            else:
                # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
                # manually edited
                if line.qty_invoiced > 0:
                    continue
                if not line.product_uom or not line.product_id or not line.order_id.pricelist_id:
                    line.price_unit = 0.0
                else:
                    price = line.with_company(line.company_id)._get_display_price()
                    line.price_unit = line.product_id._get_tax_included_unit_price(
                        line.company_id,
                        line.order_id.currency_id,
                        line.order_id.date_order,
                        'sale',
                        fiscal_position=line.order_id.fiscal_position_id,
                        product_price_unit=price,
                        product_currency=line.currency_id
                    )

    @api.depends('product_uom_qty', 'mo_bom_id', 'estimated_installation_date_from_mrp')
    def _compute_estimated_installation_date_total(self):
        for rec in self:
            rec.total_installation_date_1 = rec.mo_bom_id.total_installation_date
            rec.total_installation_date_1 = rec.total_installation_date_1 * rec.product_uom_qty

    @api.onchange('product_template_id', 'mo_bom_id')
    def onchange_product_template_id(self):
        res = {}
        for line in self:
            res['domain'] = {
                'mo_bom_id': ['|', ('product_tmpl_id', '=', line.product_template_id.id), (
                    'byproduct_ids.product_id.product_tmpl_id', '=', line.product_template_id.id)]
            }
            return res
