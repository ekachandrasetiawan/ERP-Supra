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

class ReportSPRecord(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportSPRecord, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
              'get_sales_prospect' : self.get_sales_prospect,
              'get_sales_person':self.get_sales_person,
              'get_week_line':self.get_week_line,
        })
        
    def get_sales_prospect(self,form):
        domain = [('user_id','in',form['user_ids'])]
        sa_ids=self.pool.get('week.status').search(self.cr,self.uid,domain)
        sa=self.pool.get('week.status').browse(self.cr,self.uid,sa_ids)
        return sa
    
    def get_sales_person(self,form):
        domain = []
        if form['user_ids']:
            domain.append(('id','in',form['user_ids']))
        empl_ids=self.pool.get('res.users').search(self.cr,self.uid,domain)
        empl=self.pool.get('res.users').browse(self.cr,self.uid,empl_ids)
        return empl
    
    def get_week_line(self,form):
        if form['filter_selection']=='1':
            domain=[('name','=',form['customer_id'][0])]
        elif form['filter_selection']=='2':
            domain=[('product_group','=',form['product_group'])]
        elif form['filter_selection']=='3':
            domain=[('amount','>=',form['amount'])]
        elif form['filter_selection']=='4':
            weekstatus=[x.id for x in self.get_sales_prospect(form)]
            domain=[('status_id','in',weekstatus)]
        wl_ids=self.pool.get('week.status.line').search(self.cr,self.uid,domain)
        wl=self.pool.get('week.status.line').browse(self.cr,self.uid,wl_ids)
        return wl
    
report_sxw.report_sxw('report.salesprospectrecord.crm.form','salesprospectrecord.crm','ad_supra_crm_report/report/salesprospectrecord.mako', parser=ReportSPRecord) 

class SalesProspectExcel(report_xls):
    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Sales Prospect Record'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        
        form=data['form']
        #style = xlwt.easyxf('pattern: no fill;')
        
        #header
        ws.write(1,1,"PSM")
        ws.write(1,2,"CUSTOMER")
        ws.write(1,3,"LOCATION")
        ws.write(1,4,"PRODUCT")
        ws.write(1,5,"AMOUNT")
        ws.write(1,6,"PROJECT")
        ws.write(1,7,"UPDATE INFORMATION")
        dr=2
        for sp in parser.get_sales_person(form):
            for spo in parser.get_sales_prospect(form,sp.id):
                for st in spo.status_line:
                    ws.write(dr,1,spo.user_id.name)
                    ws.write(dr,2,st.name.name)
                    ws.write(dr,3,spo.type)
                    ws.write(dr,4,st.product_id.name)
                    ws.write(dr,5,st.currency_id.name+" "+str(st.amount))
                    ws.write(dr,6,st.project)
                    ws.write(dr,7,st.update_line[0].name)
                    dr+=1        
        pass

SalesProspectExcel('report.salesprospectrecord.crm.form.xls', 'salesorderrecord.crm', 'ad_supra_crm_report/report/salesorderrecord.mako', parser=ReportSPRecord, header=False)
