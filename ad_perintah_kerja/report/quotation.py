import os
import time
import pooler
import tools
import addons
import tempfile
from pdf_ext import fill_pdf
from report import report_sxw
from report.render import render
from report.interface import report_int


class quotation_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(quotation_form, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_object':self._get_object,
        }) 
        
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['id']])
        return obj_data

report_sxw.report_sxw('report.quotation.report', 'sale.order', 'ad_perintah_kerja/report/quotation.mako', parser=quotation_form,header=False)



class external_pdf(render):
    def __init__(self, pdf):
        render.__init__(self)
        self.pdf = pdf
        self.output_type='pdf'

    def _render(self):
        return self.pdf


class report_perintah(report_int):

    def create(self, cr, uid, ids, datas, context=None):
        pool = pooler.get_pool(cr.dbname)
        
        result = {
                  'name' : datas['form']['data']['name'],
                  'date' : time.strftime('%d %B %Y', time.strptime(datas['form']['data']['kontrakdate'],'%Y-%m-%d')),
                  'tanggal' : time.strftime('%d %B %Y', time.strptime(datas['form']['data']['date'],'%Y-%m-%d')),
                  'kirim' : time.strftime('%d %B %Y', time.strptime(datas['form']['data']['delivery_date'],'%Y-%m-%d')),
                  'order': datas['form']['data']['kontrak'],
                  'qty': datas['form']['data']['qty'],
                  'partner': datas['form']['data']['partner_id'][1],
                  'product': datas['form']['data']['product'].encode('latin9'),
                  'creator': datas['form']['data']['creator'],
                  'checker': datas['form']['data']['checker'],
                  'approver': datas['form']['data']['approver']
        }
        
        
        tmp_file = tempfile.mkstemp(".pdf")[1]
        try:
            fill_pdf(addons.get_module_resource('ad_perintah_kerja','report','perintahA4.pdf'), tmp_file, result)
            with open(tmp_file, "r") as ofile:
                self.obj = external_pdf(ofile.read())
        finally:
            os.remove(tmp_file)    
        self.obj.render()
        return (self.obj.pdf, 'pdf')
        
report_perintah('report.perintah.A4')


class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_basedon': self.get_basedon,
        })

            
    def get_basedon(self, form):
        data = self.pool.get(form['model']).browse(self.cr, self.uid, [form['form']['id']])
        return data
    


report_sxw.report_sxw('report.spk.continue', 'perintah.kerja', 'addons/ad_perintah_kerja/report/spk_continue.rml', parser=ReportStatus, header=False)

