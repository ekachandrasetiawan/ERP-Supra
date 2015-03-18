import time
import netsvc
import decimal_precision as dp
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools import float_compare
#untuk penghitungan selisih kurs
class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'
    _columns = {
        'income_currency_exchange_account_id_ar': fields.related(
            'company_id', 'income_currency_exchange_account_id_ar',
            type='many2one',
            relation='account.account',
            string="Gain Exchange Rate Account Receiveble", 
            domain="[('type', '=', 'other')]"),
        'expense_currency_exchange_account_id_ar': fields.related(
            'company_id', 'expense_currency_exchange_account_id_ar',
            type="many2one",
            relation='account.account',
            string="Loss Exchange Rate Account Receiveble",
            domain="[('type', '=', 'other')]"),
        'income_currency_exchange_account_id_ap': fields.related(
            'company_id', 'income_currency_exchange_account_id_ap',
            type='many2one',
            relation='account.account',
            string="Gain Exchange Rate Account Payable", 
            domain="[('type', '=', 'other')]"),
        'expense_currency_exchange_account_id_ap': fields.related(
            'company_id', 'expense_currency_exchange_account_id_ap',
            type="many2one",
            relation='account.account',
            string="Loss Exchange Rate Account Payble",
            domain="[('type', '=', 'other')]"),
    }
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        print "+++++++++++++++++++++++++++++++++++++++++++++++++++=="
        res = super(account_config_settings, self).onchange_company_id(cr, uid, ids, company_id, context=context)
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res['value'].update({'income_currency_exchange_account_id_ar': company.income_currency_exchange_account_id_ar and company.income_currency_exchange_account_id_ar.id or False, 
                                 'expense_currency_exchange_account_id_ar': company.expense_currency_exchange_account_id_ar and company.expense_currency_exchange_account_id_ar.id or False,
                                 'income_currency_exchange_account_id_ap': company.income_currency_exchange_account_id_ap and company.income_currency_exchange_account_id_ap.id or False, 
                                 'expense_currency_exchange_account_id_ap': company.expense_currency_exchange_account_id_ap and company.expense_currency_exchange_account_id_ap.id or False})
        else: 
            res['value'].update({'income_currency_exchange_account_id_ar': False, 
                                 'expense_currency_exchange_account_id_ar': False,
                                 'income_currency_exchange_account_id_ap': False, 
                                 'expense_currency_exchange_account_id_ap': False})
        return res

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'income_currency_exchange_account_id_ar': fields.many2one(
            'account.account',
            string="Gain Exchange Rate Account Receiveble",
            domain="[('type', '=', 'other')]",),
        'expense_currency_exchange_account_id_ar': fields.many2one(
            'account.account',
            string="Loss Exchange Rate Account Receiveble",
            domain="[('type', '=', 'other')]",),
        'income_currency_exchange_account_id_ap': fields.many2one(
            'account.account',
            string="Gain Exchange Rate Account Payable",
            domain="[('type', '=', 'other')]",),
        'expense_currency_exchange_account_id_ap': fields.many2one(
            'account.account',
            string="Loss Exchange Rate Account Payable",
            domain="[('type', '=', 'other')]",),
    }

res_company()

class account_voucher_1(osv.osv):
    _inherit = 'account.voucher'
    
    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_rounding=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_rounding=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = voucher.type in ('payment', 'purchase') and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount

            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    sign = voucher.type in ('payment', 'purchase') and -1 or 1
                    foreign_currency_diff = sign * line.move_line_id.amount_residual_currency + amount_currency

            move_line['amount_currency'] = amount_currency
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                if voucher.type in ('payment','purchase'):
                    exch_lines = self._get_exchange_lines_ap(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                else:
                    exch_lines = self._get_exchange_lines_ar(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)

            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)

        return (tot_line, rec_lst_ids)
    
    def _get_exchange_lines_ap(self, cr, uid, line, move_id, amount_residual, company_currency, current_currency, context=None):
        '''
        Prepare the two lines in company currency due to currency rate difference.

        :param line: browse record of the voucher.line for which we want to create currency rate difference accounting
            entries
        :param move_id: Account move wher the move lines will be.
        :param amount_residual: Amount to be posted.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: the account move line and its counterpart to create, depicted as mapping between fieldname and value
        :rtype: tuple of dict
        '''
        if amount_residual > 0:
            account_id = line.voucher_id.company_id.expense_currency_exchange_account_id_ap
            if not account_id:
                raise osv.except_osv(_('Insufficient Configuration!'),_("You should configure the 'Loss Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
        else:
            account_id = line.voucher_id.company_id.income_currency_exchange_account_id_ap
            if not account_id:
                raise osv.except_osv(_('Insufficient Configuration!'),_("You should configure the 'Gain Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
        # Even if the amount_currency is never filled, we need to pass the foreign currency because otherwise
        # the receivable/payable account may have a secondary currency, which render this field mandatory
        if line.account_id.currency_id:
            account_currency_id = line.account_id.currency_id.id
        else:
            account_currency_id = company_currency <> current_currency and current_currency or False
        move_line = {
            'journal_id': line.voucher_id.journal_id.id,
            'period_id': line.voucher_id.period_id.id,
            'name': _('change')+': '+(line.name or '/'),
            'account_id': line.account_id.id,
            'move_id': move_id,
            'partner_id': line.voucher_id.partner_id.id,
            'currency_id': account_currency_id,
            'amount_currency': 0.0,
            'quantity': 1,
            'credit': amount_residual > 0 and amount_residual or 0.0,
            'debit': amount_residual < 0 and -amount_residual or 0.0,
            'date': line.voucher_id.date,
        }
        move_line_counterpart = {
            'journal_id': line.voucher_id.journal_id.id,
            'period_id': line.voucher_id.period_id.id,
            'name': _('change')+': '+(line.name or '/'),
            'account_id': account_id.id,
            'move_id': move_id,
            'amount_currency': 0.0,
            'partner_id': line.voucher_id.partner_id.id,
            'currency_id': account_currency_id,
            'quantity': 1,
            'debit': amount_residual > 0 and amount_residual or 0.0,
            'credit': amount_residual < 0 and -amount_residual or 0.0,
            'date': line.voucher_id.date,
        }
        return (move_line, move_line_counterpart)
    
    def _get_exchange_lines_ar(self, cr, uid, line, move_id, amount_residual, company_currency, current_currency, context=None):
        '''
        Prepare the two lines in company currency due to currency rate difference.

        :param line: browse record of the voucher.line for which we want to create currency rate difference accounting
            entries
        :param move_id: Account move wher the move lines will be.
        :param amount_residual: Amount to be posted.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: the account move line and its counterpart to create, depicted as mapping between fieldname and value
        :rtype: tuple of dict
        '''
        if amount_residual > 0:
            account_id = line.voucher_id.company_id.expense_currency_exchange_account_id_ar
            if not account_id:
                raise osv.except_osv(_('Insufficient Configuration!'),_("You should configure the 'Loss Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
        else:
            account_id = line.voucher_id.company_id.income_currency_exchange_account_id_ar
            if not account_id:
                raise osv.except_osv(_('Insufficient Configuration!'),_("You should configure the 'Gain Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
        # Even if the amount_currency is never filled, we need to pass the foreign currency because otherwise
        # the receivable/payable account may have a secondary currency, which render this field mandatory
        if line.account_id.currency_id:
            account_currency_id = line.account_id.currency_id.id
        else:
            account_currency_id = company_currency <> current_currency and current_currency or False
        move_line = {
            'journal_id': line.voucher_id.journal_id.id,
            'period_id': line.voucher_id.period_id.id,
            'name': _('change')+': '+(line.name or '/'),
            'account_id': line.account_id.id,
            'move_id': move_id,
            'partner_id': line.voucher_id.partner_id.id,
            'currency_id': account_currency_id,
            'amount_currency': 0.0,
            'quantity': 1,
            'credit': amount_residual > 0 and amount_residual or 0.0,
            'debit': amount_residual < 0 and -amount_residual or 0.0,
            'date': line.voucher_id.date,
        }
        move_line_counterpart = {
            'journal_id': line.voucher_id.journal_id.id,
            'period_id': line.voucher_id.period_id.id,
            'name': _('change')+': '+(line.name or '/'),
            'account_id': account_id.id,
            'move_id': move_id,
            'amount_currency': 0.0,
            'partner_id': line.voucher_id.partner_id.id,
            'currency_id': account_currency_id,
            'quantity': 1,
            'debit': amount_residual > 0 and amount_residual or 0.0,
            'credit': amount_residual < 0 and -amount_residual or 0.0,
            'date': line.voucher_id.date,
        }
        return (move_line, move_line_counterpart)
account_voucher_1()
#end --- untuk penghitungan selisih kurs

class account_bank_statement(osv.osv):

    _inherit = 'account.bank.statement'

    def button_dummy(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        hasil = val.balance_start + sum([x.amount for x in val.line_ids])        
        return self.write(cr, uid, ids, {'balance_end_real': hasil}, context=context)



    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, next_number, context=None):
        voucher_obj = self.pool.get('account.voucher')
        wf_service = netsvc.LocalService("workflow")
        account_move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        bank_st_line_obj = self.pool.get('account.bank.statement.line')
        st_line = bank_st_line_obj.browse(cr, uid, st_line_id, context=context)
        
        
        pos = False
        for a in  st_line.statement_id.move_line_ids:
            if a.amount_currency and st_line.kurs:
                if a.move_id.state == 'posted':
                    pos = True
                    account_move_obj.button_cancel(cr, uid, [a.move_id.id])
                if a.debit:
                    move_line_obj.write(cr, uid, [a.id], {'debit': st_line.kurs*abs(a.amount_currency)})
                elif a.credit:
                    move_line_obj.write(cr, uid, [a.id], {'credit': st_line.kurs*abs(a.amount_currency)})
            if pos:
                pos = False
                account_move_obj.write(cr, uid, [a.move_id.id], {'state': 'posted'})

        if st_line.voucher_id:
            voucher_obj.write(cr, uid, [st_line.voucher_id.id], {'number': next_number}, context=context)
            if st_line.voucher_id.state == 'cancel':
                voucher_obj.action_cancel_draft(cr, uid, [st_line.voucher_id.id], context=context)
            wf_service.trg_validate(uid, 'account.voucher', st_line.voucher_id.id, 'proforma_voucher', cr)

            v = voucher_obj.browse(cr, uid, st_line.voucher_id.id, context=context)
            bank_st_line_obj.write(cr, uid, [st_line_id], {
                'move_ids': [(4, v.move_id.id, False)]
            })

            tobeposted = []
            for x in v.move_ids:
                if x.move_id.state == 'draft':
                    if x.move_id.id not in tobeposted:
                        tobeposted.append(x.move_id.id)
                if x.amount_currency and st_line.kurs:
                    if x.move_id.state == 'posted':
                        account_move_obj.button_cancel(cr, uid, [x.move_id.id])
                    if x.debit:
                        move_line_obj.write(cr, uid, [x.id], {'debit': st_line.kurs*abs(x.amount_currency)})
                    elif x.credit:
                        move_line_obj.write(cr, uid, [x.id], {'credit': st_line.kurs*abs(x.amount_currency)})
                    
            account_move_obj.post(cr, uid, tobeposted)  

            return move_line_obj.write(cr, uid, [x.id for x in v.move_ids], {'statement_id': st_line.statement_id.id}, context=context)
        
        return super(account_bank_statement, self).create_move_from_st_line(cr, uid, st_line.id, company_currency_id, next_number, context=context)

    
account_bank_statement()

class account_bank_statement_line(osv.osv):

    _inherit = 'account.bank.statement.line'
    _columns = {
        'kurs': fields.float('Kurs', digits=(12,2), select=True),
        'code_voucher': fields.char('Cek/Giro/Bank', size=32),
        'method': fields.selection([('cash', 'Cash'), ('cek', 'Cheques'), ('giro', 'Giro'), ('transfer', 'Transfer')], 'Method', select=True),
    }

    _defaults = {
                 'method': 'transfer',
    }        

    def _check_amount(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.voucher_id:
                #diff = obj.voucher_id.amount - abs(obj.amount)
                diff = 0.0
                if not self.pool.get('res.currency').is_zero(cr, uid, obj.statement_id.currency, diff):
                    return False
        return True    
    

    _constraints = [
        (_check_amount, 'The amount of the voucher must be the same amount as the one on the statement line.', ['amount']),
    ]

account_bank_statement_line()


class account_statement_from_invoice_lines(osv.osv_memory):
    _inherit = "account.statement.from.invoice.lines"
    
    def populate_statement(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        statement_id = context.get('statement_id', False)
        if not statement_id:
            return {'type': 'ir.actions.act_window_close'}
        data =  self.read(cr, uid, ids, context=context)[0]
        line_ids = data['line_ids']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        line_obj = self.pool.get('account.move.line')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        currency_obj = self.pool.get('res.currency')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        line_date = time.strftime('%Y-%m-%d')
        statement = statement_obj.browse(cr, uid, statement_id, context=context)

        # for each selected move lines
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            voucher_res = {}
            ctx = context.copy()
            #  take the date for computation of currency => use payment date
            ctx['date'] = line_date
            amount = 0.0

            if line.debit > 0:
                amount = line.debit
            elif line.credit > 0:
                amount = -line.credit

            if line.amount_currency:
                amount = currency_obj.compute(cr, uid, line.currency_id.id,
                    statement.currency.id, line.amount_currency, context=ctx)
            elif (line.invoice and line.invoice.currency_id.id <> statement.currency.id):
                amount = currency_obj.compute(cr, uid, line.invoice.currency_id.id,
                    statement.currency.id, amount, context=ctx)

            context.update({'move_line_ids': [line.id],
                            'invoice_id': line.invoice.id})
            
            type = 'general'
            ttype = amount < 0 and 'payment' or 'receipt'
            sign = 1
            if line.journal_id.type in ('sale', 'sale_refund'):
                type = 'customer'
                ttype = 'receipt'
            elif line.journal_id.type in ('purchase', 'purhcase_refund'):
                type = 'supplier'
                ttype = 'payment'
                sign = -1
                
            result = voucher_obj.onchange_partner_id(cr, uid, [], partner_id=line.partner_id.id, journal_id=statement.journal_id.id, amount=sign*amount, currency_id= statement.currency.id, ttype=ttype, date=line_date, context=context)

            voucher_line_dict =  {}
            for line_dict in result['value']['line_cr_ids'] + result['value']['line_dr_ids']:
                move_line = line_obj.browse(cr, uid, line_dict['move_line_id'], context)
                if line.move_id.id == move_line.move_id.id:
                    voucher_line_dict = line_dict
            
            saldo = 0.0
            if line.journal_id.type in ('sale', 'sale_refund'):
                saldo = voucher_line_dict['amount_unreconciled'] 
            elif line.journal_id.type in ('purchase', 'purhcase_refund'):
                saldo = -voucher_line_dict['amount_unreconciled']
                
            voucher_res = { 'type': ttype,
                            'name': line.name,
                            'partner_id': line.partner_id.id,
                            'journal_id': statement.journal_id.id,
                            'account_id': result['value'].get('account_id', statement.journal_id.default_credit_account_id.id),
                            'company_id': statement.company_id.id,
                            'currency_id': statement.currency.id,
                            'date': line.date,
                            'amount': sign*saldo,
                            'payment_rate': result['value']['payment_rate'],
                            'payment_rate_currency_id': result['value']['payment_rate_currency_id'],
                            'period_id':statement.period_id.id}
            
            voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)


            if voucher_line_dict:
                voucher_line_dict.update({'voucher_id': voucher_id})
                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
            statement_line_obj.create(cr, uid, {
                'name': line.name or '?',
                'amount': sign*voucher_line_dict['amount_unreconciled'],
                'type': type,
                'partner_id': line.partner_id.id,
                'account_id': line.account_id.id,
                'statement_id': statement_id,
                'ref': line.ref,
                'voucher_id': voucher_id,
                'date': time.strftime('%Y-%m-%d'),
            }, context=context)
        return {'type': 'ir.actions.act_window_close'}

account_statement_from_invoice_lines()



class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _columns = {
        'ref_doc': fields.char('Ref Doc', size=64),
        'amount_dpp': fields.float('Amount DPP', digits=(12,2)),
        'amount_pajak': fields.float('Amount Pajak', digits=(12,2)),
    }

    def _update_check(self, cr, uid, ids, context=None):
        done = {}
        for line in self.browse(cr, uid, ids, context=context):
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
            if line.move_id.state <> 'draft' and (not line.journal_id.entry_posted):
                raise osv.except_osv(_('Error!'), _('You cannot do this modification on a confirmed entry. You can just change some non legal fields or you must unconfirm the journal entry first.\n%s.') % err_msg)
            if line.reconcile_id:
                pass #raise osv.except_osv(_('Error!'), _('You cannot do this modification on a reconciled entry. You can just change some non legal fields or you must unreconcile first.\n%s.') % err_msg)
            t = (line.journal_id.id, line.period_id.id)
            if t not in done:
                self._update_journal_check(cr, uid, line.journal_id.id, line.period_id.id, context)
                done[t] = True
        return True
    
account_move_line()


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines"""
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
            company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
            # check if taxes are all computed
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            # I disabled the check_total feature
            group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
            group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
            if group_check_total and uid in [x.id for x in group_check_total.users]:
                if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
                    raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += ait_obj.move_line_get(cr, uid, inv.id)

            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
            acc_id = inv.account_id.id

            if diff_currency_p:
                for i in iml:
                    if inv.kurs:
                        if i['price'] < 0:
                            i['price'] = -(i['amount_currency'] * inv.kurs)
                        else:
                            i['price'] = i['amount_currency'] * inv.kurs
                        if inv.pajak:
                            if i['type'] == 'tax':
                                if i['price'] < 0:
                                    i['price'] = -(i['amount_currency'] * inv.pajak)
                                else:
                                    i['price'] = i['amount_currency'] * inv.pajak 
            ending = 0
            if diff_currency_p:
                for i in iml:    
                    ending += abs(i['price']) 
                if total < 0:
                    total = -(ending)
                else:
                    total = abs(ending)


            name = inv['name'] or inv['supplier_invoice_number'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = payment_term_obj.compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                ctx.update({'date': inv.date_invoice})
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
                    else:
                        amount_currency = False
                    
                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p \
                                and amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                    
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })

            date = inv.date_invoice or time.strftime('%Y-%m-%d')

            part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

            line = self.group_lines(cr, uid, iml, line, inv)

            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise osv.except_osv(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)

            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update(company_id=inv.company_id.id,
                       account_period_prefer_normal=True)
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id

            ctx.update(invoice=inv)
            move_id = move_obj.create(cr, uid, move, context=ctx)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move_obj.post(cr, uid, [move_id], context=ctx)
        self._log_event(cr, uid, ids)
        return True
    
account_invoice()