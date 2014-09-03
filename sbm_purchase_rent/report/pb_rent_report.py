import time
from report import report_sxw
from osv import osv
import pooler

class ReportPBRent(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportPBRent, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'sum' : sum,
            'get_lines':self.get_lines,
            })

    def get_lines(self,obj):
        details= obj.details
        res=[]
        arrLine={}
        i=1
        for x in details:
            arrLine.update(
                {
                    'no':i,
                    'product':x.name,
                    'uom':x.uom,
                    'qty':x.qty,
                    'notes':x.notes
                }
            )
            res.append(arrLine)
            arrLine={}
            i+=1
        return res

report_sxw.report_sxw('report.print.pbrent', 'rent.requisition', 'sbm_purchase_rent/report/report.rml', parser = ReportPBRent, header = False)