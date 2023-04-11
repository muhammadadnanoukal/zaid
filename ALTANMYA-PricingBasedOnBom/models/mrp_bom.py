import traceback

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv.expression import AND
from odoo.tools import float_round
from collections import defaultdict


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=False)
    code = fields.Char('Reference')
    pricing_type_square = fields.Boolean('Square Meter', default=True, )
    pricing_type_component = fields.Boolean('Component', default=False, )
    total_installation_date = fields.Float('Total Installation Days', compute='_compute_installation_amount',
                                           store=True, tracking=True)

    @api.model
    def _bom_find(self, products, picking_type=None, company_id=False, bom_type=False, bom_ids=False):
        if not bom_ids:
            return super(MrpBom, self)._bom_find(products, picking_type, company_id, bom_type)
        else:
            bom_by_product = defaultdict(list)
            products = products.filtered(lambda p: p.type != 'service')
            if not products:
                return bom_by_product
            domain = self._bom_find_domain(products, picking_type=picking_type, company_id=company_id,
                                           bom_type=bom_type)
            # Performance optimization, allow usage of limit and avoid the for loop `bom.product_tmpl_id.product_variant_ids`
            if len(products) == 1:
                bom = self.search(domain, order='sequence, product_id, id')
                if bom:
                    bom_by_product[products] = bom
                return bom_by_product

            boms = self.search(domain, order='sequence, product_id, id')
            products_ids = set(products.ids)
            for bom in boms:
                products_implies = bom.product_id or bom.product_tmpl_id.product_variant_ids
                for product in products_implies:
                    if product.id in products_ids:
                        bom_by_product[product].append(bom)
            return bom_by_product

    @api.depends('bom_line_ids.estimated_installation_date')
    def _compute_installation_amount(self):
        for rec in self:
            rec.total_installation_date = sum(rec.bom_line_ids.mapped('estimated_installation_date'))

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.product_uom_id = self.product_tmpl_id.uom_id.id
            if self.product_id.product_tmpl_id != self.product_tmpl_id:
                self.product_id = False
            self.bom_line_ids.bom_product_template_attribute_value_ids = False
            self.operation_ids.bom_product_template_attribute_value_ids = False
            self.byproduct_ids.bom_product_template_attribute_value_ids = False

            domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
            if self.id.origin:
                domain.append(('id', '!=', self.id.origin))
        if self._context.get('default_name', False):
            self.code = self._context['default_name']

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        for line in self.bom_line_ids:
            if line.product_id:
                line.price_unit = line.compute_price_unit()

    total_amount = fields.Float('Total Amount', compute='_compute_amount', store=True, tracking=True)

    @api.depends('bom_line_ids.price_unit', 'bom_line_ids.product_qty', 'bom_line_ids.price_subtotal')
    def _compute_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.bom_line_ids.mapped('price_subtotal'))


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    last_price = fields.Float(string='Last Price')
    estimated_installation_date = fields.Float(string='Estimated Installation Days', readonly=True, store=True, )
    attachments_count = fields.Integer(string='Attachment Count', compute='_compute_attachments_count')

    @api.onchange('product_id', 'bom_id.pricing_type_component')
    def set_product_domain(self):
        product_ids = self.env['product.product'].search(['|', '&',
                                                          ('pricing_type_component_tmpl', '=', True),
                                                          ('pricing_type_component_tmpl', '=',
                                                           self.bom_id.pricing_type_component),
                                                          '&',
                                                          ('pricing_type_square_tmpl', '=', True),
                                                          ('pricing_type_square_tmpl', '=',
                                                           self.bom_id.pricing_type_square)]).ids
        res = {}
        if self.bom_id.type in ['assembled', 'custom_price']:
            res['domain'] = {'product_id': [('id', 'in', product_ids),
                                            '|',
                                            ('company_id', '=', False),
                                            ('company_id', '=', self.company_id.id)]}
            return res
        else:
            res['domain'] = {'product_id': ['|',
                                            ('company_id', '=', False),
                                            ('company_id', '=', self.company_id.id)]}
            return res

    @api.onchange('product_id', 'product_qty', 'self.product_id.product_tmpl_id.estimated_installation_date_tmpl')
    def _compute_installation_date(self):
        res = self.product_id.product_tmpl_id.estimated_installation_date_tmpl * self.product_qty
        self.estimated_installation_date = res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # Compute Last Price
            self._cr.execute(
                'SELECT price FROM product_supplierinfo WHERE product_tmpl_id = {} ORDER BY id DESC LIMIT 1'.format(
                    self.product_id.product_tmpl_id.id)
            )
            _res = self._cr.dictfetchall()
            if _res is not None and len(_res) != 0:
                self.last_price = _res[0].get('price')
            else:
                self.last_price = 0
            # Compute Price Unit
            self.price_unit = self.compute_price_unit()

    def compute_price_unit(self):
        price_unit = 0.0
        from_pricelist = self.env['product.pricelist.item'].search(
            [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
             ('pricelist_id', '=', self.bom_id.pricelist_id.id)], limit=1)
        if not from_pricelist:
            from_template = self.env['product.template'].search([('id', '=', self.product_id.product_tmpl_id.id)],
                                                                limit=1)
            if from_template:
                price_unit = from_template.list_price
        else:
            price_unit = from_pricelist.fixed_price

        return price_unit

    price_unit = fields.Float('Unit Price', required=True, default=0.0)
    price_subtotal = fields.Float('Subtotal', compute='_compute_price_subtotal', default=0.0)

    @api.depends('price_unit', 'product_qty')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.price_unit * line.product_qty

    check_field = fields.Boolean('Check', compute='get_user')

    @api.depends('price_unit')
    def get_user(self):
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            self.check_field = False
        else:
            self.check_field = True
