# -*- coding: utf-8 -*-
{
    'name': "imm_stock",
    'summary': """
    Organize the stock by zones and minimal quantity of product in the
    stock operations.
    """,

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'sale_stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_location.xml',
        'views/stock_picking.xml',
        'views/product_location_quant.xml',
        'views/templates.xml',
        'views/stock_zone.xml',
        'views/stock_warehouse.xml',
        'wizard/distribute_order.xml',
        'report/line_order.xml',
        'report/pick_report.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
