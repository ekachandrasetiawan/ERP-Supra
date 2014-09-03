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

class ReportSARecord(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportSARecord, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
              'get_sales_activity' : self.get_sales_activity,
              'get_sales_person':self.get_sales_person,
        })
        
    def get_sales_activity(self,form,sales_id):
        domain = [('user_id','=',sales_id),('begin','=',form['date_begin']),('end','=',form['date_end'])]
        sa_ids=self.pool.get('sales.activity').search(self.cr,self.uid,domain)
        sa=self.pool.get('sales.activity').browse(self.cr,self.uid,sa_ids)
        return sa
    
    def get_sales_person(self,form):
        domain = []
        if form['user_ids']:
            domain.append(('id','in',form['user_ids']))
        empl_ids=self.pool.get('res.users').search(self.cr,self.uid,domain)
        empl=self.pool.get('res.users').browse(self.cr,self.uid,empl_ids)
        return empl
        
report_sxw.report_sxw('report.salesactivityrecord.crm.form','salesactivityrecord.crm','addons/ad_supra_crm_report/report/salesactivityrecord.mako', parser=ReportSARecord) 


class SalesActivityExcel(report_xls):
    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Sales Activity Record'))
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
        
        sales_person=parser.get_sales_person(form)
        dr=2
        for sp in sales_person:
            x=parser.get_sales_activity(form,sp.id)
            for sa in x:
                weekbefplanrow = [len(sa.beforeplansenin),len(sa.beforeplanselasa),len(sa.beforeplanrabu),len(sa.beforeplankamis),len(sa.beforeplanjumat)]
                weekbefactrow = [len(sa.beforeactualsenin),len(sa.beforeactualselasa),len(sa.beforeactualrabu),len(sa.beforeactualkamis),len(sa.beforeactualjumat)]
                weekaftplanrow = [len(sa.afterplansenin),len(sa.afterplanselasa),len(sa.afterplanrabu),len(sa.afterplankamis),len(sa.afterplanjumat)]
                weekaftactrow = [len(sa.afteractualsenin),len(sa.afteractualselasa),len(sa.afteractualrabu),len(sa.afteractualkamis),len(sa.afteractualjumat)]
                
                #kolom before launch plan
                drw=dr
                for seninbp in sa.beforeplansenin:
                    ws.write(drw,3,seninbp.name)
                    drw+=1
                drw=dr
                for selasabp in sa.beforeplanselasa:
                    ws.write(drw,4,selasabp.name)
                    drw+=1
                drw=dr
                for rabubp in sa.beforeplanrabu:
                    ws.write(drw,5,rabubp.name)
                    drw+=1
                drw=dr
                for kamisbp in sa.beforeplankamis:
                    ws.write(drw,6,kamisbp.name)
                    drw+=1
                drw=dr
                for jumatbp in sa.beforeplanjumat:
                    ws.write(drw,7,jumatbp.name)
                    drw+=1
                
                #kolom after launch plan
                drw=dr+max(weekbefplanrow)
                ws.write_merge(dr, drw-1 ,2,2,"Before Plan")
                ap=drw
                for seninap in sa.afterplansenin:
                    ws.write(drw,3,seninap.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)
                for selasaap in sa.afterplanselasa:
                    ws.write(drw,4,selasaap.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)
                for rabuap in sa.afterplanrabu:
                    ws.write(drw,5,rabuap.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)
                for kamisap in sa.afterplankamis:
                    ws.write(drw,6,kamisap.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)
                for jumatap in sa.afterplanjumat:
                    ws.write(drw,7,jumatap.name)
                    drw+=1
                
                #kolom before launch actual
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)
                ws.write_merge(ap, drw-1 ,2,2,"After Plan")
                ba=drw
                
                for seninba in sa.beforeactualsenin:
                    ws.write(drw,3,seninba.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)
                for selasaba in sa.beforeactualselasa:
                    ws.write(drw,4,selasaba.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)
                for rabuba in sa.beforeactualrabu:
                    ws.write(drw,5,rabuba.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)
                for kamisba in sa.beforeactualkamis:
                    ws.write(drw,6,kamisba.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)
                for jumatba in sa.beforeactualjumat:
                    ws.write(drw,7,jumatba.name)
                    drw+=1                
                
                #kolom after launch actual
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)+max(weekbefactrow)
                ws.write_merge(ba, drw-1 ,2,2,"Before Actual")
                aa=drw
                for seninaa in sa.afteractualsenin:
                    ws.write(drw,3,seninaa.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)+max(weekbefactrow)
                for selasaaa in sa.afteractualselasa:
                    ws.write(drw,4,selasaaa.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)+max(weekbefactrow)
                for rabuaa in sa.afteractualrabu:
                    ws.write(drw,5,rabuaa.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)+max(weekbefactrow)
                for kamisaa in sa.afteractualkamis:
                    ws.write(drw,6,kamisaa.name)
                    drw+=1
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)+max(weekbefactrow)
                for jumataa in sa.afteractualjumat:
                    ws.write(drw,7,jumataa.name)
                    drw+=1
                
                drw=dr+max(weekbefplanrow)+max(weekaftplanrow)+max(weekbefactrow)+max(weekaftactrow)
                
                ws.write_merge(aa, drw-1 ,2,2,"After Actual")
                ws.write_merge(dr, drw-1 ,1,1,sp.name)
                dr=drw
        pass

SalesActivityExcel('report.salesactivityrecord.crm.form.xls', 'salesorderrecord.crm', 'addons/ad_supra_crm_report/report/salesorderrecord.mako', parser=ReportSARecord, header=False)
