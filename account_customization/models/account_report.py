from odoo import api, fields, models, tools, _

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_accounts = None

    @api.model
    def _get_filter_accounts(self):
        return self.env['account.account'].with_context(active_test=False).search([
            ('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id])
        ], order="company_id, name")

    def _init_filter_accounts(self, options, previous_options=None):
        if self.filter_accounts is None:
            return

        previous_company = False
        if previous_options and previous_options.get('accounts'):
            account_map = dict((opt['id'], opt['selected']) for opt in previous_options['accounts'] if
                               opt['id'] != 'divider' and 'selected' in opt)
        else:
            account_map = {}
        options['accounts'] = []

        group_header_displayed = False
        default_group_ids = []
        for ac in self._get_filter_accounts():
            if ac.company_id != previous_company:
                options['accounts'].append({'id': 'divider', 'name': ac.company_id.name})
                previous_company = ac.company_id
            options['accounts'].append({
                'id': ac.id,
                'name': ac.name,
                'code': ac.code,
                # 'type': 'ac.type',
                'selected': account_map.get(ac.id, ac.id in default_group_ids),
            })

    @api.model
    def _get_options_accounts(self, options):
        return [
            account for account in options.get('accounts', []) if
            not account['id'] in ('divider', 'group') and account['selected']
        ]

    @api.model
    def _get_options_accounts_domain(self, options):
        selected_accounts = self._get_options_accounts(options)
        return selected_accounts and [('account_id', 'in', [ac['id'] for ac in selected_accounts])] or []


    @api.model
    def _get_options_domain(self, options):
        # OVERRIDE
        domain = super(AccountReport, self)._get_options_domain(options)
        domain += self._get_options_accounts_domain(options)
        return domain

class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger"

    filter_accounts = True
