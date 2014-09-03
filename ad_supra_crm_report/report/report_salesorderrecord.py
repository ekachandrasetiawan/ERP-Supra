from report import report_sxw
import pooler
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby
from report_webkit import webkit_report
from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import calendar
from report_engine_xls import report_xls
import xlwt

class ReportSORecord(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportSORecord, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
		      'get_interval' : self.get_interval,
              'get_sales_order' : self.get_sales_order,
              'get_sales_person':self.get_sales_person,
              'get_regional' : self.get_regional,
        })

    
    def get_interval(self,form):
        mm=self.pool.get('account.period').browse(self.cr,self.uid,form['periode'][0])
        
        dstart=datetime.strptime(mm.date_start,'%Y-%m-%d')
        dstop=datetime.strptime(mm.date_stop,'%Y-%m-%d')
        weeks={}
        curr=dstart
        while curr<=dstop:
            if curr.strftime('%W') not in weeks:
                weeks.update({
                              curr.strftime('%W'):[curr.strftime('%Y-%m-%d')]
                              })
            else:
                n=weeks[curr.strftime('%W')]
                n.append(curr.strftime('%Y-%m-%d'))
                weeks.update({
                              curr.strftime('%W'):n
                            })
            curr+=relativedelta(days=1)
        w=SortedDisplayDict(weeks)
        return w
    
    def get_sales_order(self,form,sales_id,intervals):
        domain = [('user_id','=',sales_id),('state','in',('progress','manual','done')),('date_order','in',intervals)]
        so_ids=self.pool.get('sale.order').search(self.cr,self.uid,domain)
        so=self.pool.get('sale.order').browse(self.cr,self.uid,so_ids)
        return so
    
    def get_sales_person(self,form,reg_id):
        domain = [('regional','=',reg_id)]
        if form['salesman_ids']:
            domain.append(('id','in',form['salesman_ids'])) 
        
        empl_ids=self.pool.get('hr.employee').search(self.cr,self.uid,domain)
        empl=self.pool.get('hr.employee').browse(self.cr,self.uid,empl_ids)
        
        return empl
        
    def get_regional(self):
        regid=self.pool.get('regional').search(self.cr,self.uid,[])
        reg=self.pool.get('regional').browse(self.cr,self.uid,regid)
        return reg
        
report_sxw.report_sxw('report.salesorderrecord.crm.form','salesorderrecord.crm','addons/ad_supra_crm_report/report/salesorderrecord.mako', parser=ReportSORecord) 

class SalesOrderExcel(report_xls):
    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Sales Order Record'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        
        form=data['form']
        #style = xlwt.easyxf('pattern: no fill;')
        
        #header
        ws.write_merge(2,3,1,1,"REG")
        ws.write_merge(2,3,2,2,"SALES")
        mm=parser.pool.get('account.period').browse(parser.cr,parser.uid,form['periode'][0])
        ws.write_merge(2,2,3,7,str((datetime.strptime(mm.date_start,'%Y-%m-%d')).strftime('%B')))
        interval=parser.get_interval(form)
        dr=3
        dc=3
        for x1 in range(len(interval)):
            ws.write(dr,dc,min(interval[str(x1+int(min(interval.keys())))])+"-"+max(interval[str(x1+int(min(interval.keys())))]))
            dc+=1
        
        #body
        dr=4
        for reg in parser.get_regional():
            sales_person=parser.get_sales_person(form,reg.id)
            ws.write_merge(dr,dr+len(sales_person)-1,1,1,reg.name)
            for sales in sales_person:
                ws.write(dr,2,sales.name)
                total_penjualan=0
                dc=3
                for week in range(len(interval)):
                    for so in parser.get_sales_order(form,sales.user_id.id,interval[str(week+int(min(interval.keys())))]):
                        total_penjualan+=so.amount_total
                    ws.write(dr,dc,total_penjualan)
                    dc+=1
                dr+=1
        pass

SalesOrderExcel('report.salesorderrecord.crm.form.xls', 'salesorderrecord.crm', 'addons/ad_supra_crm_report/report/salesorderrecord.mako', parser=ReportSORecord, header=False)

    
class SortedDisplayDict(dict):
    def __str__(self):
        return "{" + ", ".join("%r: %r" % (key, self[key]) for key in sorted(self)) + "}"
