import time
from report import report_sxw
from osv import osv,fields
from report.render import render
from ad_num2word_id import num2word
import pooler
#from report_tools import pdf_fill,pdf_merge
from tools.translate import _
import tools
from tools.translate import _
import decimal_precision as dp
#from ad_amount2text_idr import amount_to_text_id
from tools import amount_to_text_en 


class invoice_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(invoice_form, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_object':self._get_object,
            'convert':self.convert,
            'get_sum1':self.get_sum1,
            'get_sum2':self.get_sum2,
            'get_sum3':self.get_sum3,
            'get_sum4':self.get_sum4,
            'get_sum5':self.get_sum5,
            'get_sum6':self.get_sum6,
        }) 
        
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['id']])
        return obj_data
   
    def convert(self, amount_total, cur):
        amt_id = num2word.num2word_id(amount_total,"id").decode('utf-8')
        return amt_id

    def get_sum1(self,obj):
        total=0.0
        for line in obj.invoice_line:
            total+=line.quantity*line.price_unit
        return total

    def get_sum2(self,obj):
        total=0.0
        for line in obj.invoice_line:
            if line.discount>0:
                total+=line.quantity*line.price_unit*(line.discount/100)
        return total

    def get_sum3(self,obj):
        total=0.0
        for line in obj.invoice_line:
            if line.price_subtotal<0:
                total+=(-1*line.price_subtotal)
        return total

    def get_sum4(self,obj):
        return obj.amount_untaxed

    def get_sum5(self,obj):
        return obj.amount_tax

    def get_sum6(self,obj):
        return obj.amount_total

report_sxw.report_sxw('report.invoice2.form', 'account.invoice', 'ad_report_salesadmin/inv/inv_form.mako', parser=invoice_form,header=False)
