from odoo import api, fields, models, tools, _

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_account = None

    ####################################################
    # OPTIONS: accounts
    ####################################################

    def _init_filter_account(self, options, previous_options=None):
        if not self.filter_account:
            return

        options['account'] = True
        options['account_ids'] = previous_options and previous_options.get('account_ids') or []
        selected_account_ids = [int(account) for account in options['account_ids']]
        selected_accounts = selected_account_ids and self.env['account.account'].browse(selected_account_ids) or self.env['account.account']
        options['selected_account_ids'] = selected_accounts.mapped('name')

    @api.model
    def _get_options_account_domain(self, options):
        domain = []
        if options.get('account_ids'):
            account_ids = [int(account) for account in options['account_ids']]
            domain.append(('account_id', 'in', account_ids))
        return domain

    @api.model
    def _get_options_domain(self, options):
        # OVERRIDE
        domain = super(AccountReport, self)._get_options_domain(options)
        domain += self._get_options_account_domain(options)
        return domain


    def _set_context(self, options):
        #OVERRIDE
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('account_ids'):
            ctx['account_ids'] = self.env['account.account'].browse([int(account) for account in options['account_ids']])
        return ctx

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)
        self = self.with_context(self._set_context(options)) # For multicompany, when allowed companies are changed by options (such as aggregare_tax_unit)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in (options.get('partner_categories') or [])]

        if options.get('account'):
            options['selected_account_ids'] = [self.env['account.account'].browse(int(account)).name for account in options['account_ids']]

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        if options.get('journals'):
            journals_selected = set(journal['id'] for journal in options['journals'] if journal.get('selected'))
            for journal_group in self.env['account.journal.group'].search([('company_id', '=', self.env.company.id)]):
                if journals_selected and journals_selected == set(self._get_filter_journals().ids) - set(journal_group.excluded_journal_ids.ids):
                    options['name_journal_group'] = journal_group.name
                    break

        report_manager = self._get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons_in_sequence(options),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view']._render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info


class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger"
    filter_account = True


class ReportAccountFinancialReport(models.Model):

    _inherit = "account.financial.html.report"
    filter_account = True
