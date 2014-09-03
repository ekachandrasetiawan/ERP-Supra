import os
import re
import time
import pooler
import addons
import tempfile
from report import report_sxw
from pdf_ext import fill_pdf
from report.render import render
from report.interface import report_int


class external_pdf(render):
    def __init__(self, pdf):
        render.__init__(self)
        self.pdf = pdf
        self.output_type='pdf'

    def _render(self):
        return self.pdf


class report_customerinvoice(report_int):
             
    def create(self, cr, uid, ids, datas, context=None):
        pool = pooler.get_pool(cr.dbname)
                
        kwitansi = '-'
        if datas['form']['data']['kwitansi']:
            kwitansi = datas['form']['data']['kwitansi']
            
        result = {
                  'name' : kwitansi,
                  
                  'customer' : datas['form']['data']['partner_id'][1],
                  'alamatcustomer' : datas['form']['data']['alamatcustomer'],
                  
                  'no' : datas['form']['data']['no'],
                  'qty': datas['form']['data']['qty'],
                  'product' : datas['form']['data']['product'].encode('latin9'),
                  'price' : datas['form']['data']['price'],
                  'subtotal' : datas['form']['data']['subtotal'],
        
                  'rsubtotal' : datas['form']['data']['rsubtotal'],
                  'rpajak' : datas['form']['data']['rpajak'],
                  'rtotal' : datas['form']['data']['rtotal'],              
                  
                  'terbilang' : datas['form']['data']['terbilang'],              
                  
                  'tanggal' : time.strftime('%d.%m.%Y', time.strptime(datas['form']['data']['date_invoice'],'%Y-%m-%d')),
                  'orang' : datas['form']['data']['approver'][1],                  
        }
        
        tmp_file = tempfile.mkstemp(".pdf")[1]
        try:
            fill_pdf(addons.get_module_resource('ad_account_finance','report','invoice.pdf'), tmp_file, result)
            with open(tmp_file, "r") as ofile:
                self.obj = external_pdf(ofile.read())
        finally:
            os.remove(tmp_file)    
        self.obj.render()
        return (self.obj.pdf, 'pdf')
        
report_customerinvoice('report.print.customerinvoice')



class report_fakturpajak(report_int):

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
    
    def create(self, cr, uid, ids, datas, context=None):
        pool = pooler.get_pool(cr.dbname)
        
        kwitansi = '-'
        if datas['form']['data']['kwitansi']:
            kwitansi = datas['form']['data']['kwitansi']
            
        result = {
                  'name' : 'INV : ' + kwitansi,
                  'fakturpajak' : datas['form']['data']['faktur_pajak_no'],
                  
                  'supra' : datas['form']['data']['company_id'][1],
                  'alamatsupra' : datas['form']['data']['alamatsupra'],  
                  'npwpsupra' : datas['form']['data']['npwpsupra'],
                  
                  'customer' : datas['form']['data']['partner_id'][1],
                  'alamatcustomer' : datas['form']['data']['alamatcustomer'],
                  'npwpcustomer' : datas['form']['data']['npwpcustomer'],
                  
                  'no' : datas['form']['data']['no'],
                  'qty': datas['form']['data']['qty'],
                  'product': datas['form']['data']['product'].encode('latin9'),
                  'valas' : datas['form']['data']['valas'],
                  'rupiah' : datas['form']['data']['rupiah'],
                  
                  'vtotal' : datas['form']['data']['vtotal'],
                  'vdiskon' : datas['form']['data']['vdiskon'],
                  'vkenapajak' : datas['form']['data']['vtotal'],
                  'vpajak' : datas['form']['data']['vpajak'],
                  
                  'rtotal' : datas['form']['data']['rtotal'],
                  'rdiskon' : datas['form']['data']['rdiskon'],
                  'rkenapajak' : datas['form']['data']['rtotal'],
                  'rpajak' : datas['form']['data']['rpajak'],
                  
                  'kmk' : datas['form']['data']['kmk'],
                  'kurs' : datas['form']['data']['kurs'],
                  'matauang' : '1 ' + datas['form']['data']['currency_id'][1],
                  'currency' : datas['form']['data']['currency_id'][1],
                  
                  'tanggal' : time.strftime('%d-%m-%Y', time.strptime(datas['form']['data']['date_invoice'],'%Y-%m-%d')),
                  'orang' : datas['form']['data']['approver'][1],                  
        }
        
        filepdf = 'fakturpajakrupiah.pdf'
        if result['currency'] != 'IDR' :
            result['rtotal'] = False
            filepdf = 'fakturpajakvalas.pdf'
        
        
        tmp_file = tempfile.mkstemp(".pdf")[1]
        try:
            fill_pdf(addons.get_module_resource('ad_account_finance', 'report', filepdf), tmp_file, result)
            with open(tmp_file, "r") as ofile:
                self.obj = external_pdf(ofile.read())
        finally:
            os.remove(tmp_file)    
        self.obj.render()
        return (self.obj.pdf, 'pdf')
        
report_fakturpajak('report.print.fakturpajak')


















# class ReportStatus(report_sxw.rml_parse):
#     def __init__(self, cr, uid, name, context=None):
#         super(ReportStatus, self).__init__(cr, uid, name, context=context)
#         self.localcontext.update({
#             'time': time,
#             'get_basedon': self.get_basedon,
#         })
# 
#             
#     def get_basedon(self, form):
#         data = self.pool.get(form['model']).browse(self.cr, self.uid, [form['form']['id']])
#         return data
#     
# 
# 
# report_sxw.report_sxw('report.note.continue', 'delivery.note', 'addons/ad_delivery_note/report/note_continue.rml', parser=ReportStatus, header=False)

