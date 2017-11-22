# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class mygateController(http.Controller):
    @http.route(['/payment/mygate/return', '/payment/mygate/cancel', '/payment/mygate/error'], type='http', auth='public', csrf=False)
    def payu_return(self, **post):
        """ mygate."""
        _logger.info(
            'mygate: entering form_feedback with post data %s', pprint.pformat(post))
        return_url = '/'
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'mygate')
        return werkzeug.utils.redirect(return_url)
