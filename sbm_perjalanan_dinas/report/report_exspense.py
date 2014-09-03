import time
from report import report_sxw
from osv import osv
import pooler

class ReportExspenses(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportExspenses, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'sum' : sum,
            })

report_sxw.report_sxw('report.report.exspense', 'purchase.order', 'addons/sbm_perjalanan_dinas/report/report_exspense.rml', parser = ReportExspenses, header = False)