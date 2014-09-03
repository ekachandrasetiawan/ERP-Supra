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

class wizard_print_op(osv.osv_memory):
    _name = "wizard.print.op"
    _columns = {
        "size" : fields.selection([('v1', 'A4'), ('v2', 'A5')], 'Size', required=True),
    }
    
    def do_print(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        x = {'ids':context.get('active_ids',[])}
        x['model'] = 'order.preparation'
        x['form'] = self.read(cr,uid,ids)[0]
        if x['form']['size']=="v1":
            diction = {
                'type': 'ir.actions.report.xml',
                'report_name': 'deliveryorder.form.A4',
                'report_type': 'webkit',
                'datas': x,
            }
        else:
            diction = {
                'type': 'ir.actions.report.xml',
                'report_name': 'deliveryorder.form.A5',
                'report_type': 'webkit',
                'datas': x,
            }
        #print "=-===",diction
        return diction
wizard_print_op()


class do_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(do_form, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_object':self._get_object,
        }) 
        
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['id']])
        return obj_data

report_sxw.report_sxw('report.deliveryorder.form.A4', 'order.preparation', 'ad_report_salesadmin/do/do_form.mako', parser=do_form,header=False)
report_sxw.report_sxw('report.deliveryorder.form.A5', 'order.preparation', 'ad_report_salesadmin/do/do_form.mako', parser=do_form,header=False)
