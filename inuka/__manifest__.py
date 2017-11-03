# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inuka',
    'version': '1.0',
    'category': 'Purchases',
    'sequence': 60,
    'summary': 'Inuka',
    'description': "",
    'website': 'https://www.odoo.com/',
    'depends': ['purchase', 'account_invoicing'],
    'data': [
        'views/purchase_views.xml',
        'views/account_invoice_views.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
