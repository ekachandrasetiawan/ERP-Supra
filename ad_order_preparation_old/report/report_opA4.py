import time
from report import report_sxw
from osv import osv
import pooler

class printopA4(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(printopA4, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'sum' : sum,
            'get_lines':self.get_lines,
            })
    def get_lines(self,obj):
        prepare_lines= obj.prepare_lines
        res=[]
        arrLine={}
        i=1
        customer= ''
        for x in prepare_lines:
            //arrLine.update({'no':i,'name':x.name,'satuan':x.satuan,'part_no':x.part_no,'jumlah_diminta':x.jumlah_diminta,'stok':x.stok,'keterangan':x.keterangan})
            res.append(arrLine)
            arrLine={}
            //customer = x.customer_id.name
            i+=1
        return res

report_sxw.report_sxw('report.print.opA4', 'order.preparation', 'addons/ad_order_preparation/report/report_opA4.rml', parser = printopA4, header = False)