# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'ALTANMYA-PricingBasedOnBom',
    'version': '1.0',
    'summary': 'ALTANMYA-Bikar',
    'author': 'ALTANMYA - TECHNOLOGY SOLUTIONS',
    'company': 'ALTANMYA - TECHNOLOGY SOLUTIONS Part of ALTANMYA GROUP',
    'website': "http://tech.altanmya.net",
    'category': 'Manufacturing/Manufacturing',
    'depends': ['mrp', 'sale', 'stock', 'sale_mrp'],
    'description': "Bikar MRP Extension",
    'data': [
        # 'views/mrp_bom_views.xml',
        'views/munf_mrp_bom_views.xml',
        'views/sale_order_views.xml',
        'views/product_views.xml',
        'views/mrp_production_inherit_views.xml',
        'views/stock_route_views.xml',
    ],
    'post_init_hook': '_set_route_type',
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3'
}
