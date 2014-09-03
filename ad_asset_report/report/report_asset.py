import pooler
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from itertools import groupby
from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import calendar
from report import report_sxw
from report_webkit import webkit_report
from report_engine_xls import report_xls

class ReportAsset(report_sxw.rml_parser):
    def __init__(self,cr,uid,name,context=None):
        super(ReportAsset,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
#               'get_sales_activity' : self.get_sales_activity,
        })
report_sxw.report_sxw('report.account.assetreport.form','account.assetreport','addons/ad_asset_report/report/asset.mako', parser=ReportAsset)

class AssetExcel(report_xls):
    def generate_xls_report(self,parser,data,obj,wb):
        ws = wb.add_sheet(('Asset Report'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        
        form=data['form']
        #style = xlwt.easyxf('pattern: no fill;')
        
        #header
        ws.write(1,1,"PIC")
        ws.write(1,2,"NAMA")
        ws.write(1,3,"SENIN")
        ws.write(1,4,"SELASA")
        ws.write(1,5,"RABU")
        ws.write(1,6,"KAMIS")
        ws.write(1,7,"JUMAT")
        print "____________________________________________-__-_"
        pass
AssetExcel('report.account.assetreport.xls', 'account.assetreport', 'addons/ad_asset_report/report/asset.mako', parser=ReportAsset, header=False)