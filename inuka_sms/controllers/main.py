# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class SMSPushNotification(http.Controller):

    @http.route('/sms/push-notifications/', type="http", auth="public", csrf=False)
    def sms_push_notification(self, *args, **kwargs):
        print ('>>>', args, kwargs,request)
        return 'Done'

