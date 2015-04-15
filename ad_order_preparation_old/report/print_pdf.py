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


class report_preparation(report_int):

    def create(self, cr, uid, ids, datas, context=None):
        pool = pooler.get_pool(cr.dbname)
        
        result = {
                  'name' : datas['form']['data']['name'],
                  'date' : time.strftime('%d %B %Y', time.strptime(datas['form']['data']['tanggal'],'%Y-%m-%d')),
                  'order': datas['form']['data']['poc'],
                  'qty': datas['form']['data']['qty'],
                  'partner': datas['form']['data']['partner_id'][1]+'\n'+datas['form']['data']['street']+'\n'+datas['form']['data']['jalan']+'\n'+datas['form']['data']['phone'],
                  'product_name': datas['form']['data']['product_name'].encode('utf-8'),
                  'product_code': datas['form']['data']['product_code']
        }
        
        tmp_file = tempfile.mkstemp(".pdf")[1]
        try:
            fill_pdf(addons.get_module_resource('ad_order_preparation','report','preparationA4.pdf'), tmp_file, result)
            with open(tmp_file, "r") as ofile:
                self.obj = external_pdf(ofile.read())
        finally:
            os.remove(tmp_file)    
        self.obj.render()
        return (self.obj.pdf, 'pdf')
        
report_preparation('report.preparation.A4')



class print_preparation(report_int):

    def create(self, cr, uid, ids, datas, context=None):
        pool = pooler.get_pool(cr.dbname)
        
        result = {
                  'name' : datas['form']['data']['name'],
                  'date' : time.strftime('%d %B %Y', time.strptime(datas['form']['data']['tanggal'],'%Y-%m-%d')),
                  'order': datas['form']['data']['poc'],
                  'qty': datas['form']['data']['qty'],
                  'partner': datas['form']['data']['partner_id'][1]+'\n'+datas['form']['data']['street']+'\n'+datas['form']['data']['jalan']+'\n'+datas['form']['data']['phone'],
                  'product_name': datas['form']['data']['product_name'].encode('utf-8'),
                  'product_code': datas['form']['data']['product_code']
        }
        
        
        tmp_file = tempfile.mkstemp(".pdf")[1]
        try:
            fill_pdf(addons.get_module_resource('ad_order_preparation','report','preparationA5.pdf'), tmp_file, result)
            with open(tmp_file, "r") as ofile:
                self.obj = external_pdf(ofile.read())
        finally:
            os.remove(tmp_file)    
        self.obj.render()
        return (self.obj.pdf, 'pdf')
        
print_preparation('report.preparation.A5')




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
    


report_sxw.report_sxw('report.preparation.continue', 'order.preparation', 'addons/ad_order_preparation/report/preparation_continue.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.preparation.multipage', 'order.preparation', 'addons/ad_order_preparation/report/preparation_A4multi.rml', parser=ReportStatus, header=False)

