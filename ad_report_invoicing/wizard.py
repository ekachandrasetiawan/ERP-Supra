import time
from report import report_sxw
from osv import osv,fields
from report.render import render
import pooler
from tools.translate import _
import tools
from tools.translate import _
import decimal_precision as dp
from tools import amount_to_text_en 

class wizard_print(osv.osv_memory):
    _name = "wizard.print"
    _columns = {
        "report_type" : fields.selection([('inv', 'Invoice'), ('fp', 'Tax Invoice')], 'What to print?', required=True),
        "report_inv_type" : fields.selection([('1', 'Total Amount Only'), ('2', 'All Invoice Line')], 'Invoice For'),
        "report_fp_type" : fields.selection([('1', 'IDR Currencies'), ('2', 'Foreign Currencies')], 'Tax Invoice for'),
    }
    
    def do_print(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        x = {'ids':context.get('active_ids',[])}
        x['model'] = 'account.invoice'
        x['form'] = self.read(cr,uid,ids)[0]
        if x['form']['report_type']=="inv":
            if x['form']['report_inv_type']=="1":
                diction = {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'invoice2.form',
                    'report_type': 'webkit',
                    'datas': x,
                }
            else:
                diction = {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'invoice2.form',
                    'report_type': 'webkit',
                    'datas': x,
                }
        else:
            if x['form']['report_fp_type']=="1":
                diction = {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'faktur.pajak.form',
                    'report_type': 'webkit',
                    'datas': x,
                }
            else:
                diction = {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'faktur.pajak.valas.form',
                    'report_type': 'webkit',
                    'datas': x,
                }
        #print "=-===",diction
        return diction
wizard_print()