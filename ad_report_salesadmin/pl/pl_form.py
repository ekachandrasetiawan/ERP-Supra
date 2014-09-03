import time
from report import report_sxw
from osv import osv,fields
from report.render import render
#from ad_num2word_id import num2word
import pooler
#from report_tools import pdf_fill,pdf_merge
from tools.translate import _
import tools
from tools.translate import _
import decimal_precision as dp
#from ad_amount2text_idr import amount_to_text_id
from tools import amount_to_text_en 


class pl_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(pl_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_object':self.get_object,
            'get_dn':self.get_dn,
        }) 
        
    def get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['form']['id']])
        return obj_data
    
    def get_dn(self,dn_id):
        dn_data=self.pool.get('delivery.note').browse(self.cr,self.uid,[dn_id])
        return dn_data
    
#     def /(self,obj):
#         obj_delivery_note_line=self.pool.get("delivery.note.line")
#         self.cr.execute('select * from delivery_note_line where note_id=%s order by packing', (obj.id,))
#         res = self.cr.dictfetchall()
#         return res
    
report_sxw.report_sxw('report.pl.form.reguler', 'delivery.note', 'ad_report_salesadmin/pl/pl_form.mako', parser=pl_form,header=False)
report_sxw.report_sxw('report.pl.form.newmont', 'delivery.note', 'ad_report_salesadmin/pl/pl_form.mako', parser=pl_form,header=False)

class delivery_note(osv.osv):
    _inherit = "delivery.note"
    _columns = {
        "color_code" : fields.char('Color/Stock Code',size=64),
        "jumlah_coli" : fields.char('Jumlah Coli',size=64),
        "ekspedisi" : fields.char('Ekspedisi',size=64),
    }
delivery_note()

class delivery_note_line(osv.osv):
    _inherit = "delivery.note.line"
    _columns = {
        "measurement" : fields.char('Measurement', size=64),
        "weight" : fields.char('Weight', size=64),
        "packing" : fields.char('Pack', size=64),
        "itemno" : fields.char('Item Number',size=64),
    }
delivery_note_line()