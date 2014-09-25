import os
import time
import pooler
import addons
import tempfile
from openerp.osv import fields, osv
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


class report_delivery(report_int):

    def create(self, cr, uid, ids, datas, context=None):
        pool = pooler.get_pool(cr.dbname)
        
        result = {
                  'name' : datas['form']['data']['name'],
                  'order': datas['form']['data']['poc'],
                  'prepare': datas['form']['data']['prepare_id'][1],
                  'qty': datas['form']['data']['qty'],
                  'partner': datas['form']['data']['partner_id'][1]+'\n'+datas['form']['data']['street']+'\n'+datas['form']['data']['jalan']+'\n'+datas['form']['data']['phone'],
                  'product_name': datas['form']['data']['product_name'].encode('latin9'),
                  'product_code': datas['form']['data']['product_code']
        }
        
        print '------------------',datas['form']['data']['partner_id'][1]+'\n'+datas['form']['data']['street']+'\n'+datas['form']['data']['jalan']+'\n'+datas['form']['data']['phone']

        tmp_file = tempfile.mkstemp(".pdf")[1]
        try:
            fill_pdf(addons.get_module_resource('ad_delivery_note','report','deliveryA4.pdf'), tmp_file, result)
            with open(tmp_file, "r") as ofile:
                self.obj = external_pdf(ofile.read())
        finally:
            os.remove(tmp_file)    
        self.obj.render()
        return (self.obj.pdf, 'pdf')
        
report_delivery('report.delivery.note.A4')



class report_packaging(report_int):

    def create(self, cr, uid, ids, datas, context=None):
        pool = pooler.get_pool(cr.dbname)
        
        color = ''
        if datas['form']['data']['color']:
            color = 'COLOUR CODE : ' + datas['form']['data']['color']  
        
        result = {
                  'no' : datas['form']['data']['no'],
                  'urgent' : datas['form']['data']['urgent'],
                  'weight' : datas['form']['data']['weight'],
                  'measurement' : datas['form']['data']['measurement'],
                  'name' : datas['form']['data']['name'],
                  'attention' : datas['form']['data']['attention'],
                  'date' : time.strftime('     %B %Y', time.strptime(datas['form']['data']['date'],'%Y-%m-%d %H:%M:%S')),
                  'reference': datas['form']['data']['reference'],
                  'purchase' : 'Purchase Order No.' + datas['form']['data']['purchase'] + ', Tgl. ' + time.strftime('%d/%m/%Y', time.strptime(datas['form']['data']['pur_date'],'%Y-%m-%d')),
                  'color': color,
                  'qty': datas['form']['data']['qty'],
                  'product': datas['form']['data']['product'],
                  'totalitem': 'Total :    Item',
                  'totalbox': 'Total :    Box',
        }
        
        
        tmp_file = tempfile.mkstemp(".pdf")[1]
        try:
            fill_pdf(addons.get_module_resource('ad_delivery_note','report','paketA4.pdf'), tmp_file, result)
            with open(tmp_file, "r") as ofile:
                self.obj = external_pdf(ofile.read())
        finally:
            os.remove(tmp_file)    
        self.obj.render()
        return (self.obj.pdf, 'pdf')
        
report_packaging('report.paket.A4')


class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_basedon': self.get_basedon,
            'get_location': self.get_location,
            'get_lines':self.get_lines,
        })

    def get_lines(self,obj):
      res={}
      res['prepare_no']=obj.prepare_id.name[:7]
      
      note_lines= obj.note_lines
      for x in note_lines:
        # product_set=self.pool.get('mrp.bom').search(cr,uid,[('product_id', '=' ,x.product_id)])
        print '============================',x.product_id
        # res.append({'no':x.no,'product_id':x.product_qty, 'product_uom':x.product_uom.name, name':x.name,'part_no':x.product_id.default_code})

      return res
            
    def get_basedon(self, form):
        data = self.pool.get(form['model']).browse(self.cr, self.uid, [form['form']['id']])
        return data
    
    def get_location(self, o):
        loc = []; data = []
        for x in o.move_lines :
            loc.append(x.location_dest_id.id)
            
        if len(set(loc)) > 1 :
            raise osv.except_osv(('Perhatian !'), ('Lokasi tujuan harus satu tempat'))
        
        data = (o.move_lines[0].location_dest_id.name, o.move_lines[0].location_dest_id.comment)
        return data

report_sxw.report_sxw('report.delivery.note', 'delivery.note', 'addons/ad_delivery_note/report/delivery_note.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.note.continue', 'delivery.note', 'addons/ad_delivery_note/report/note_continue.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.internal.move', 'stock.picking', 'addons/ad_delivery_note/report/internal_move.rml', parser=ReportStatus, header=False)

