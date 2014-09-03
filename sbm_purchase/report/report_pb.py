import time
from report import report_sxw
from osv import osv
import pooler

class ReportPB(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportPB, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'sum' : sum,
            'get_lines':self.get_lines,
            })
    def get_lines(self,obj):
        detail_pb_ids= obj.detail_pb_ids
        res=[]
        arrLine={}
        i=1
        customer= ''
        for x in detail_pb_ids:
            arrLine.update({'no':i,'name':x.name,'satuan':x.satuan,'part_no':x.part_no,'jumlah_diminta':x.jumlah_diminta,'stok':x.stok,'keterangan':x.keterangan})
            res.append(arrLine)
            arrLine={}
            customer = x.customer_id.name
            i+=1
        return res

report_sxw.report_sxw('report.print.pb', 'pembelian.barang', 'addons/sbm_purchase/report/report_pb.rml', parser = ReportPB, header = False)