import re
import time
import netsvc
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta

class account_bank_statement(osv.osv):

    _inherit = 'account.bank.statement'   

    def balance_check(self, cr, uid, st_id, journal_type='bank', context=None):
        return True

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
            bank_st_line_obj.write(cr, uid, [st_line_id], {'move_ids': [(4, v.move_id.id, False)]})

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
        'ref':fields.text('Reference',required=False),
        'kurs': fields.float('BI Rate', digits=(12,2), select=True),
        'code_voucher': fields.char('No Cek/Giro', size=32),
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


class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
            'kmk': fields.char('KMK', size=64, select=True),
            'kurs': fields.float('BI Rate', digits_compute= dp.get_precision('Product Price'), select=True),
            'pajak': fields.float('Tax Rate', digits_compute= dp.get_precision('Product Price'), select=True),
            'approver' : fields.many2one('res.users', 'Approved by'),
            'kwitansi': fields.char('Kwitansi', size=64, select=True),
            'faktur_pajak_no' : fields.char('Faktur Pajak', size=20, required=False, help='Misal 010.000-10.00000001'),
    }
    
    _defaults = {
        'approver' : 28,
        'faktur_pajak_no': '0000000000000000',
    }
    

    def koma(self, format, value):
        parts = re.compile(r'\d+|\D+').findall(format % (value,))
        for i in xrange(len(parts)):
            s = parts[i]
            if s.isdigit():
                parts[i] = self.commafy(s)
                break
        return ''.join(parts)
        
    def commafy(self, s):
        r = []
        for i, c in enumerate(reversed(s)):
            if i and (not (i % 3)):
                r.insert(0, ',')
            r.insert(0, c)
        return ''.join(r)
    
    def invoice_validate(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        if not val.faktur_pajak_no:
            raise osv.except_osv(_('Perhatian!'), _('Kolom Faktur Pajak wajib diisi !'))    
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        return True

    def onchange_format_faktur(self, cr, uid, ids, no):
        print no
        print "Len ->",len(no)
        try:
            int(no)
            if len(no) == 16:
                value = list(no)
                value.insert(3, '.')
                value.insert(7, '-')
                value.insert(10, '.')
                result = "".join(value)
                return {'value': {'faktur_pajak_no': result}}      
            else:
                return {'warning': {"title": _("Perhatian"), "message": _("Nomor faktur pajak harus 16 digit")}, 'value': {'faktur_pajak_no': False}}
        except:
            return {'warning': {"title": _("Perhatian"), "message": _("Masukan 16 digit angka tanpa separator")}, 'value': {'faktur_pajak_no': False}}


    def print_fakturpajak(self, cr, uid, ids, context=None):
        data = {}
        val = self.browse(cr, uid, ids)[0]
        data['form'] = {}
        data['ids'] = context.get('active_ids',[])
        data['form']['data'] = self.read(cr, uid, ids)[0]
        
        no = ''; qty = ''; product = '';harga = ''
        data['form']['data']['valas'] = False
        data['form']['data']['rupiah'] = False
        
        for x in val.invoice_line:
            no = no + str(x.sequence) + '\n\n'
            qty = qty + str(x.quantity) + ' ' + x.uos_id.name + '\n\n'
            product = product + x.name + '\n\n'
            harga = harga + self.koma('%.2f', x.price_subtotal) + '\n\n'
        
        data['form']['data']['alamatsupra'] = val.company_id.street + ' - ' + val.company_id.street2 + ' ' + val.company_id.zip  
        data['form']['data']['npwpsupra'] = '01.327.742.1-038.000'
        
        jalan = ''
        if val.partner_id.street2:
            jalan += val.partner_id.street2
        if val.partner_id.zip:
            jalan += ' ' + val.partner_id.zip
        if val.partner_id.city:
            jalan += ' ' + val.partner_id.city
            
        data['form']['data']['alamatcustomer'] = val.partner_id.street + ' - ' + jalan   
        data['form']['data']['npwpcustomer'] = val.partner_id.npwp
             
        data['form']['data']['no'] = no
        data['form']['data']['qty'] = qty
        data['form']['data']['product'] = product
        
        data['form']['data']['kurs'] = False
        
        data['form']['data']['vtotal'] = False
        data['form']['data']['vdiskon'] = False
        data['form']['data']['vpajak'] = False
                  
        data['form']['data']['rtotal'] = False
        data['form']['data']['rdiskon'] = False
        data['form']['data']['rpajak'] = False
        
        if val.kurs:
            data['form']['data']['kurs'] = self.koma('%.2f', float(val.kurs))
        
        if val.currency_id.id == 13:
            data['form']['data']['rupiah'] = harga 
            data['form']['data']['rtotal'] = self.koma('%.2f', val.amount_untaxed)
            data['form']['data']['rpajak'] = self.koma('%.2f', val.amount_tax)
        else:
            data['form']['data']['valas'] = harga
            data['form']['data']['vtotal'] = self.koma('%.2f', val.amount_untaxed)
            data['form']['data']['vpajak'] = self.koma('%.2f', val.amount_tax)
            data['form']['data']['rtotal'] = self.koma('%.2f', val.amount_untaxed*val.kurs)
            data['form']['data']['rpajak'] = self.koma('%.2f', val.amount_tax*val.kurs)
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'print.fakturpajak',
                'datas': data,
                'nodestroy':True
        }


    def print_customerinvoice(self, cr, uid, ids, context=None):
        data = {}
        val = self.browse(cr, uid, ids)[0]
        data['form'] = {}
        data['ids'] = context.get('active_ids',[])
        data['form']['data'] = self.read(cr, uid, ids)[0]
        
        mata = val.currency_id.name
        no = ''; qty = ''; product = '';harga = ''; subtotal = ''
        for x in val.invoice_line:
            no = no + str(x.sequence) + '\n\n'
            qty = qty + str(x.quantity) + ' ' + x.uos_id.name + '\n\n'
            product = product + x.name + '\n\n'
            harga = harga + self.koma('%.2f', x.price_unit) + ' ' + mata + '\n\n'
            subtotal = subtotal + self.koma('%.2f', x.price_subtotal) + ' ' + mata + '\n\n'
        
        jalan = ''; zip = ''; city = ''
        if val.partner_id.street2:
            jalan = val.partner_id.street2
        if val.partner_id.zip:
            zip = val.partner_id.zip
        if val.partner_id.city:
            city = val.partner_id.city
            
        data['form']['data']['alamatcustomer'] = val.partner_id.street + ' - ' + jalan + ' ' + zip + ' ' + city  
             
        data['form']['data']['no'] = no
        data['form']['data']['qty'] = qty
        data['form']['data']['product'] = product
        data['form']['data']['price'] = harga 
        data['form']['data']['subtotal'] = subtotal 
        
        data['form']['data']['terbilang'] = terbilang(val.amount_total, mata, 'id')
        if mata != 'IDR':
            data['form']['data']['terbilang'] = terbilang(val.amount_total, mata, 'en') 
        
        data['form']['data']['rsubtotal'] = self.koma('%.2f', val.amount_untaxed) + ' ' + mata
        data['form']['data']['rpajak'] = self.koma('%.2f', val.amount_tax) + ' ' + mata
        data['form']['data']['rtotal'] = self.koma('%.2f', val.amount_total) + ' ' + mata
               
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'print.customerinvoice',
                'datas': data,
                'nodestroy':True
        }

    def compute_invoice_totals(self, cr, uid, inv, company_currency, ref, invoice_move_lines, context=None):
        if context is None:
            context={}
        total = 0
        total_currency = 0
        cur_obj = self.pool.get('res.currency')
        for i in invoice_move_lines:
            if inv.currency_id.id != company_currency:
                context.update({'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                i['currency_id'] = inv.currency_id.id
                i['amount_currency'] = i['price']
                # base compute price
                # i['price'] = cur_obj.compute(cr, uid, inv.currency_id.id,
                #         company_currency, i['price'],
                #         context=context)
                # this changes based on compute real price in company currency using tax rate that inputed on invoice
                # if pajak field inputed, then compute the price using pajak as multiplier, else using currency rate on master data
                i['price'] = inv.pajak and  cur_obj.round(cr,uid,self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id,i['price']*inv.pajak) or cur_obj.compute(cr, uid, inv.currency_id.id,
                        company_currency, i['price'],
                        context=context)            
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            i['ref'] = ref
            if inv.type in ('out_invoice','in_refund'):
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
                i['price'] = - i['price']
            else:
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
        return total, total_currency, invoice_move_lines     
       
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
            # udah pak, silahkan dicoba dulu
            # if diff_currency_p:
            #     for i in iml:
            #         if inv.pajak:
            #             if i['price'] < 0:
            #                 i['price'] = cur_obj.round(cr,uid,self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id,(i['amount_currency'] * inv.pajak))
            #             else:
            #                 i['price'] = cur_obj.round(cr,uid,self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id,i['amount_currency'] * inv.pajak)
            
            name = inv['name'] or inv['supplier_invoice_number']
            # name = inv['name'] or inv['supplier_invoice_number'] or '/'
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
            # print '================',move
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            
            move_obj.post(cr, uid, [move_id], context=ctx)
        self._log_event(cr, uid, ids)
        return True
    
account_invoice()




dic = {       
    'to_19' : ('Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'),
    'tens'  : ('Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'),
    'denom' : ('', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion'),        
    'to_19_id' : ('Nol', 'Satu', 'Dua', 'Tiga', 'Empat', 'Lima', 'Enam', 'Tujuh', 'Delapan', 'Sembilan', 'Sepuluh', 'Sebelas', 'Dua Belas', 'Tiga Belas', 'Empat Belas', 'Lima Belas', 'Enam Belas', 'Tujuh Belas', 'Delapan Belas', 'Sembilan Belas'),
    'tens_id'  : ('Dua Puluh', 'Tiga Puluh', 'Empat Puluh', 'Lima Puluh', 'Enam Puluh', 'Tujuh Puluh', 'Delapan Puluh', 'Sembilan Puluh'),
    'denom_id' : ('', 'Ribu', 'Juta', 'Miliar', 'Triliun', 'Biliun')
}

def terbilang(number, currency, bhs):
    number = '%.2f' % number
    units_name = ' ' + cur_name(currency) + ' '
    lis = str(number).split('.')
    start_word = english_number(int(lis[0]), bhs)
    end_word = english_number(int(lis[1]), bhs)
    cents_number = int(lis[1])
    cents_name = (cents_number > 1) and 'Sen' or 'sen'
    final_result_sen = start_word + units_name + end_word +' '+cents_name
    final_result = start_word + units_name
    if end_word == 'Nol' or end_word == 'Zero':
        final_result = final_result
    else:
        final_result = final_result_sen
    
    return final_result[:1].upper()+final_result[1:]

def _convert_nn(val, bhs):
    tens = dic['tens_id']
    to_19 = dic['to_19_id']
    if bhs == 'en':
        tens = dic['tens']
        to_19 = dic['to_19']
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                return dcap + ' ' + to_19[val % 10]
            return dcap

def _convert_nnn(val, bhs):
    word = ''; rat = ' Ratus'; to_19 = dic['to_19_id']
    if bhs == 'en':
        rat = ' Hundred'
        to_19 = dic['to_19']
    (mod, rem) = (val % 100, val // 100)
    if rem == 1:
        word = 'Seratus'
        if mod > 0:
            word = word + ' '    
    elif rem > 1:
        word = to_19[rem] + rat
        if mod > 0:
            word = word + ' '
    if mod > 0:
        word = word + _convert_nn(mod, bhs)
    return word

def english_number(val, bhs):
    denom = dic['denom_id']
    if bhs == 'en':
        denom = dic['denom']
    if val < 100:
        return _convert_nn(val, bhs)
    if val < 1000:
        return _convert_nnn(val, bhs)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn(l, bhs) + ' ' + denom[didx]
            if r > 0:
                ret = ret + ' ' + english_number(r, bhs)
            if bhs == 'id':
                if val < 2000:
                    ret = ret.replace("Satu Ribu", "Seribu")
            return ret

def cur_name(cur="idr"):
    cur = cur.lower()
    if cur=="usd":
        return "Dollars"
    elif cur=="aud":
        return "Dollars"
    elif cur=="idr":
        return "Rupiah"
    elif cur=="jpy":
        return "Yen"
    elif cur=="sgd":
        return "Dollars"
    elif cur=="usd":
        return "Dollars"
    elif cur=="eur":
        return "Euro"
    else:
        return cur
    


#     def button_dummy(self, cr, uid, ids, context=None):
#         val = self.browse(cr, uid, ids)[0]
#         hasil = val.balance_start + sum([x.amount for x in val.line_ids])        
#         return self.write(cr, uid, ids, {'balance_end_real': hasil}, context=context)


# class account_statement_from_invoice_lines(osv.osv_memory):
#     _inherit = "account.statement.from.invoice.lines"
#     
#     def populate_statement(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         statement_id = context.get('statement_id', False)
#         if not statement_id:
#             return {'type': 'ir.actions.act_window_close'}
#         data =  self.read(cr, uid, ids, context=context)[0]
#         line_ids = data['line_ids']
#         if not line_ids:
#             return {'type': 'ir.actions.act_window_close'}
# 
#         line_obj = self.pool.get('account.move.line')
#         statement_obj = self.pool.get('account.bank.statement')
#         statement_line_obj = self.pool.get('account.bank.statement.line')
#         currency_obj = self.pool.get('res.currency')
#         voucher_obj = self.pool.get('account.voucher')
#         voucher_line_obj = self.pool.get('account.voucher.line')
#         line_date = time.strftime('%Y-%m-%d')
#         statement = statement_obj.browse(cr, uid, statement_id, context=context)
# 
#         # for each selected move lines
#         for line in line_obj.browse(cr, uid, line_ids, context=context):
#             voucher_res = {}
#             ctx = context.copy()
#             #  take the date for computation of currency => use payment date
#             ctx['date'] = line_date
#             amount = 0.0
# 
#             if line.debit > 0:
#                 amount = line.debit
#             elif line.credit > 0:
#                 amount = -line.credit
# 
#             if line.amount_currency:
#                 amount = currency_obj.compute(cr, uid, line.currency_id.id, statement.currency.id, line.amount_currency, context=ctx)
#             elif (line.invoice and line.invoice.currency_id.id <> statement.currency.id):
#                 amount = currency_obj.compute(cr, uid, line.invoice.currency_id.id, statement.currency.id, amount, context=ctx)
#             
#             context.update({'move_line_ids': [line.id], 'invoice_id': line.invoice.id})
#             
#             type = 'general'
#             ttype = amount < 0 and 'payment' or 'receipt'
#             sign = 1
#             if line.journal_id.type in ('sale', 'sale_refund'):
#                 type = 'customer'
#                 ttype = 'receipt'
#             elif line.journal_id.type in ('purchase', 'purhcase_refund'):
#                 type = 'supplier'
#                 ttype = 'payment'
#                 sign = -1
#                 
#             result = voucher_obj.onchange_partner_id(cr, uid, [], partner_id=line.partner_id.id, journal_id=statement.journal_id.id, amount=sign*amount, currency_id= statement.currency.id, ttype=ttype, date=line_date, context=context)
# 
#             voucher_line_dict =  {}
#             for line_dict in result['value']['line_cr_ids'] + result['value']['line_dr_ids']:
#                 move_line = line_obj.browse(cr, uid, line_dict['move_line_id'], context)
#                 if line.move_id.id == move_line.move_id.id:
#                     voucher_line_dict = line_dict
#             
#             saldo = 0.0
#             if line.journal_id.type in ('sale', 'sale_refund'):
#                 saldo = voucher_line_dict['amount_unreconciled'] 
#             elif line.journal_id.type in ('purchase', 'purhcase_refund'):
#                 saldo = -voucher_line_dict['amount_unreconciled']
# 
#             print 'saldo ==================>', saldo
#                             
#             voucher_res = { 'type': ttype,
#                             'name': line.name,
#                             'partner_id': line.partner_id.id,
#                             'journal_id': statement.journal_id.id,
#                             'account_id': result['value'].get('account_id', statement.journal_id.default_credit_account_id.id),
#                             'company_id': statement.company_id.id,
#                             'currency_id': statement.currency.id,
#                             'date': line.date,
#                             'amount': sign*saldo,
#                             'payment_rate': result['value']['payment_rate'],
#                             'payment_rate_currency_id': result['value']['payment_rate_currency_id'],
#                             'period_id':statement.period_id.id}
#             
#             voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)
# 
# 
#             if voucher_line_dict:
#                 voucher_line_dict.update({'voucher_id': voucher_id})
#                 voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
#             statement_line_obj.create(cr, uid, {
#                 'name': line.name or '?',
#                 'amount': sign*voucher_line_dict['amount_unreconciled'],
#                 'type': type,
#                 'partner_id': line.partner_id.id,
#                 'account_id': line.account_id.id,
#                 'statement_id': statement_id,
#                 'ref': line.ref,
#                 'voucher_id': voucher_id,
#                 'date': time.strftime('%Y-%m-%d'),
#             }, context=context)
#         return {'type': 'ir.actions.act_window_close'}
# 
# account_statement_from_invoice_lines()
# 
# 
#
# class account_voucher(osv.osv):
#     _inherit = "account.voucher"

# account_voucher()

class account_voucher(osv.osv):
    _inherit = "account.voucher"

    def recompute_payment_rate(self, cr, uid, ids, vals, currency_id, date, ttype, journal_id, amount, context=None):
        if context is None:
            context = {}
        #on change of the journal, we need to set also the default value for payment_rate and payment_rate_currency_id
        currency_obj = self.pool.get('res.currency')
        journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
        company_id = journal.company_id.id
        payment_rate = 1.0
        currency_id = currency_id or journal.company_id.currency_id.id
        payment_rate_currency_id = currency_id
        ctx = context.copy()
        ctx.update({'date': date})
        o2m_to_loop = False
        if ttype == 'receipt':
            o2m_to_loop = 'line_cr_ids'
        elif ttype == 'payment':
            o2m_to_loop = 'line_dr_ids'
        if o2m_to_loop and 'value' in vals and o2m_to_loop in vals['value']:
            for voucher_line in vals['value'][o2m_to_loop]:
                if voucher_line['currency_id'] != currency_id:
                    # we take as default value for the payment_rate_currency_id, the currency of the first invoice that
                    # is not in the voucher currency
                    payment_rate_currency_id = voucher_line['currency_id']
                    tmp = currency_obj.browse(cr, uid, payment_rate_currency_id, context=ctx).rate
                    payment_rate = tmp / currency_obj.browse(cr, uid, currency_id, context=ctx).rate
                    break
        vals['value'].update({
            'payment_rate': payment_rate,
            'currency_id': currency_id,
            'payment_rate_currency_id': payment_rate_currency_id
        })
        #read the voucher rate with the right date in the context
        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        ctx.update({
            'voucher_special_currency_rate': payment_rate * voucher_rate,
            'voucher_special_currency': payment_rate_currency_id})
        res = self.onchange_rate(cr, uid, ids, payment_rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
        for key in res.keys():
            vals[key].update(res[key])
        return vals

    def basic_onchange_partner(self, cr, uid, ids, partner_id, journal_id, ttype, context=None):
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        res = {'value': {'account_id': False}}
        if not partner_id or not journal_id:
            return res

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        account_id = False
        if journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
        elif journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

        res['value']['account_id'] = account_id
        return res

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        
        if not journal_id:
            return {}
        if context is None:
            context = {}
        #TODO: comment me and use me directly in the sales/purchases views
        res = self.basic_onchange_partner(cr, uid, ids, partner_id, journal_id, ttype, context=context)
        if ttype in ['sale', 'purchase']:
            return res
        ctx = context.copy()
        # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
        ctx.update({'date': date})
        vals = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
        vals2 = self.recompute_payment_rate(cr, uid, ids, vals, currency_id, date, ttype, journal_id, amount, context=context)
        for key in vals.keys():
            res[key].update(vals[key])
        for key in vals2.keys():
            res[key].update(vals2[key])
        #TODO: can probably be removed now
        #TODO: onchange_partner_id() should not returns [pre_line, line_dr_ids, payment_rate...] for type sale, and not 
        # [pre_line, line_cr_ids, payment_rate...] for type purchase.
        # We should definitively split account.voucher object in two and make distinct on_change functions. In the 
        # meanwhile, bellow lines must be there because the fields aren't present in the view, what crashes if the 
        # onchange returns a value for them
        if ttype == 'sale':
            del(res['value']['line_dr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        elif ttype == 'purchase':
            del(res['value']['line_cr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        return res


    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False

        if context is None:
            context = {}
        context_multi_currency = context.copy()

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_dr_ids': [] ,'line_cr_ids': [] ,'pre_line': False,},
        }

        #drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        if context.get('account_id'):
            account_type = self.pool['account.account'].browse(cr, uid, context['account_id'], context=context).type
        if ttype == 'payment':
            if not account_type:
                account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            if not account_type:
                account_type = 'receivable'

        if not context.get('move_line_ids', False):
            if(account_type=='payable'):
                ids = move_line_pool.search(cr, uid, [('state','=','valid'),('journal_id','=',2), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
            else:
                ids = move_line_pool.search(cr, uid, [('state','=','valid'),('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_lines_found.append(line.id)
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_lines_found.append(line.id)
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        remaining_amount = price
        #voucher line creation
        for line in account_move_lines:

            if(account_type=='payable'):
                move_id = line.move_id.id
                # Cek Data Kwitansi
                cekkwitansi=self.pool.get('account.invoice').search(cr,uid,[('move_id', '=' ,move_id)])
                hasilkwitansi=self.pool.get('account.invoice').browse(cr,uid,cekkwitansi)[0]
            
                nokwitansi=hasilkwitansi.kwitansi # No Kwitansi

                cektax=self.pool.get('account.move.line').search(cr,uid,[('tax_code_id', '=' ,9), ('move_id', '=' ,move_id)])
                if(cektax): # Cek Apakah Ada PPN atau Tidak ? 
                    hasiltax=self.pool.get('account.move.line').browse(cr,uid,cektax)[0] 
                    ppn23=self.pool.get('account.move.line').search(cr,uid,[('tax_code_id', '=' ,9), ('move_id', '=' ,move_id),('account_id', '=' ,133)])
                    if(ppn23): # Cek apakah ada PPH 23
                        hasilppn23=self.pool.get('account.move.line').browse(cr,uid,ppn23)[0]
                        amount_ppn23=hasilppn23.credit
                        amout_tax=hasiltax.debit-amount_ppn23
                    else:
                        amout_tax=hasiltax.debit
                else:
                    amout_tax=0

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual), context=context_multi_currency)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            if(account_type=='payable'):
                rs = {
                    'name':line.move_id.name,
                    'type': line.credit and 'dr' or 'cr',
                    'ref_doc':nokwitansi,
                    'amount_dpp':amount_original-amout_tax,
                    'amount_tax':amout_tax,
                    'move_line_id':line.id,
                    'account_id':line.account_id.id,
                    'amount_original': amount_original,
                    'amount': (line.id in move_lines_found) and min(abs(remaining_amount), amount_unreconciled) or 0.0,
                    'date_original':line.date,
                    'date_due':line.date_maturity,
                    'amount_unreconciled': amount_unreconciled,
                    'currency_id': line_currency_id,
                }
            else:
                rs = {
                    'name':line.move_id.name,
                    'type': line.credit and 'dr' or 'cr',
                    # 'ref_doc':nokwitansi,
                    # 'amount_dpp':amount_original-amout_tax,
                    # 'amount_tax':amout_tax,
                    'move_line_id':line.id,
                    'account_id':line.account_id.id,
                    'amount_original': amount_original,
                    'amount': (line.id in move_lines_found) and min(abs(remaining_amount), amount_unreconciled) or 0.0,
                    'date_original':line.date,
                    'date_due':line.date_maturity,
                    'amount_unreconciled': amount_unreconciled,
                    'currency_id': line_currency_id,
                }   
            remaining_amount -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        return default

account_voucher()

class account_voucher_line(osv.osv):
    _inherit = "account.voucher.line"
    _description = 'Voucher Lines'
    _order = "move_line_id"

    def _compute_balance(self, cr, uid, ids, name, args, context=None):

        print '==========EKA CHANDRA==========',
        currency_pool = self.pool.get('res.currency')
        rs_data = {}
        for line in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx.update({'date': line.voucher_id.date})
            voucher_rate = self.pool.get('res.currency').read(cr, uid, line.voucher_id.currency_id.id, ['rate'], context=ctx)['rate']
            ctx.update({
                'voucher_special_currency': line.voucher_id.payment_rate_currency_id and line.voucher_id.payment_rate_currency_id.id or False,
                'voucher_special_currency_rate': line.voucher_id.payment_rate * voucher_rate})
            res = {}
            company_currency = line.voucher_id.journal_id.company_id.currency_id.id
            voucher_currency = line.voucher_id.currency_id and line.voucher_id.currency_id.id or company_currency
            move_line = line.move_line_id or False

            if not move_line:
                res['amount_original'] = 0.0
                res['amount_unreconciled'] = 0.0
            elif move_line.currency_id and voucher_currency==move_line.currency_id.id:
                res['amount_original'] = abs(move_line.amount_currency)
                res['amount_unreconciled'] = abs(move_line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.credit or move_line.debit or 0.0, context=ctx)
                res['amount_unreconciled'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, abs(move_line.amount_residual), context=ctx)

            rs_data[line.id] = res
        return rs_data

    _columns = {
        'ref_doc': fields.char('Ref Doc', size=64),
        'amount_dpp': fields.function(_compute_balance, multi='dc', type='float', string='Original DPP', store=True, digits_compute=dp.get_precision('Account')),
        'amount_tax': fields.function(_compute_balance, multi='dc', type='float', string='Original Tax', store=True, digits_compute=dp.get_precision('Account')),
    } 
 
account_voucher_line()
# 
# 
# class account_invoice_line(osv.osv):
#     
#     _inherit = "account.invoice.line"
#     _columns = {
#         'spk': fields.many2one('perintah.kerja', 'Work Order'),
#     }
#     
# account_invoice_line()
