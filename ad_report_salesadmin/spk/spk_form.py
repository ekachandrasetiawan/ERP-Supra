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


class spk_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(spk_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_object':self._get_object,
        }) 
        
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['id']])
        return obj_data

report_sxw.report_sxw('report.spk.form', 'perintah.kerja', 'ad_report_salesadmin/spk/spk_form.mako', parser=spk_form,header=True)
