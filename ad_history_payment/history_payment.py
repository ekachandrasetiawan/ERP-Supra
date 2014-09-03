import re
import csv
import time
import base64
import calendar
import datetime
from osv import fields, osv
import decimal_precision as dp

class HistoryPayment(osv.osv_memory):
    _name = "history.payment"
    _columns = {
                'date_from' : fields.date('From'),
                'date_to' : fields.date('To'),
                'data_eksport': fields.binary('File', readonly=True),
                'name': fields.char('File Name', 16),
                'report': fields.selection((('ar','Customer Invoice (AR)'), ('ap','Supplier Invoice (AP)')), 'Invoice'),
    }   
    
    _defaults = {
                'report': 'ar',
                'date_from': time.strftime('%Y-%m-%d'),
                'date_to': time.strftime('%Y-%m-%d'),
    }   
        
    def eksport_excel(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0] 
               
        tipe = 'out_invoice'
        title = 'AR.csv'
        data = 'sep=;\nNumber;Date;Customer;KMK;Kwitansi;Faktur Pajak;Account;Currency;Subtotal;Tax;Total;Payment Name;Debit;Credit;Foreign Amount;Account;Currency'
        
        if val.report == 'ap':
            tipe = 'in_invoice'
            title = 'AP.csv'
            data = 'sep=;\nNumber;Date;Supplier;KMK;Kwitansi;Faktur Pajak;Account;Currency;Subtotal;Tax;Total;Payment Name;Debit;Credit;Foreign Amount;Account;Currency'
            
        res = self.pool.get('account.invoice').search(cr, uid, [('type', '=', tipe), ('state', '=', 'paid'), ('date_invoice', '>=', val.date_from), ('date_invoice', '<=',  val.date_to)])
        result = self.pool.get('account.invoice').browse(cr, uid, res) 
         
        if val.report == 'ar':
            for row in result:
                for move in row.payment_ids:
                    d = [row.number, 
                         row.date_invoice,
                         row.partner_id.name,
                         str(row.kmk),
                         str(row.kwitansi),
                         str(row.faktur_pajak_no), 
                         row.account_id.name,
                         row.currency_id.name,
                         str(row.amount_untaxed).replace('.',','),
                         str(row.amount_tax).replace('.',','),
                         str(row.amount_total).replace('.',','),
                         str(move.move_id.name),
                         str(move.debit).replace('.',','),
                         str(move.credit).replace('.',','),
                         str(move.amount_currency).replace('.',','),
                         str(move.account_id.name),
                         str(move.currency_id.name)]
                    data += '\n' + ';'.join(d)
                    
        elif val.report == 'ap':
            for row in result:
                for move in row.payment_ids:
                    d = [row.number, 
                         row.date_invoice,
                         row.partner_id.name,
                         str(row.kmk),
                         str(row.kwitansi),
                         str(row.faktur_pajak_no), 
                         row.account_id.name,
                         row.currency_id.name,
                         str(row.amount_untaxed).replace('.',','),
                         str(row.amount_tax).replace('.',','),
                         str(row.amount_total).replace('.',','),
                         str(move.move_id.name),
                         str(move.debit).replace('.',','),
                         str(move.credit).replace('.',','),
                         str(move.amount_currency).replace('.',','),
                         str(move.account_id.name),
                         str(move.currency_id.name)]
                    data += '\n' + ';'.join(d)
                    
        out = base64.b64encode(data.encode('ascii',errors='ignore'))
        self.write(cr, uid, ids, {'data_eksport':out, 'name':title}, context=context)
        
        view_rec = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ad_history_payment', 'view_wizard_history_payment')
        view_id = view_rec[1] or False
        
        return {
            'view_type': 'form',
            'view_id' : [view_id],
            'view_mode': 'form',
            'res_id': val.id, 
            'res_model': 'history.payment', # Object wizard terkait
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    
HistoryPayment()



