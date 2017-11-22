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
    'depends': ['purchase', 'delivery', 'base_automation', 'sms_frame', 'payment_mygate'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/account_invoice_views.xml',
        'views/res_partner_views.xml',
        'views/sale_views.xml',
        'data/mail_template_data.xml',
        'data/base_automation_data.xml',
        'views/report_invoice_document_inherited_for_pv.xml',
        'views/report_saleorder_document_inherited_for_pv.xml',
        'wizard/account_invoice_validate_view.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
