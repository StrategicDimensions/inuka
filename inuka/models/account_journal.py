# -*- coding: utf-8 -*-

from odoo import api, models


class AccountJournal(models.Model):
    _inherit = "account.journal"


    @api.multi
    def import_master_statement(self):
        """return action to import bank/cash statements. This button should be called only on journals with type =='bank'"""
        action_name = 'action_master_account_bank_statement_import'
        [action] = self.env.ref('inuka.%s' % action_name).read()
        # Note: this drops action['context'], which is a dict stored as a string, which is not easy to update
        action.update({'context': (u"{'journal_id': " + str(self.id) + u"}")})
        return action
