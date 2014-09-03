import time
import xlwt
import pooler
from osv import osv
from report import report_sxw
from report_engine_xls import report_xls


class Sales(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Sales, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_plan': self.get_plan,
            'get_notes': self.get_notes,
        }) 


    def get_plan(self, plan):
        hasil = ''
        for x in plan:
            hasil += x.location + ': ' + x.name + ', '
        
        return hasil


    def get_notes(self, before, after):
        hasilbefore = ''
        for x in before:
            hasilbefore += x.location + ': ' + x.name + ', '
            
        hasilafter = ''
        for x in after:
            hasilafter += x.location + ': ' + x.name + ', '
            
        data = hasilbefore + '\n' + hasilafter
        return data

report_sxw.report_sxw('report.sales.status', 'sales.activity', 'addons/ad_sales_project/report/report_sales.rml', parser = Sales, header = False)
report_sxw.report_sxw('report.plan.status', 'sales.activity', 'addons/ad_sales_project/report/report_plan.rml', parser = Sales, header = False)




class weekly_status_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Weekly Status'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1

        cols_specs = [
                      ('Customer', 1, 150, 'text', lambda x, d, p: x[0]),
                      ('Sales Order', 1, 100, 'text', lambda x, d, p: x[1]),
                      ('Amount', 1, 70, 'text', lambda x, d, p: x[2]),
                      ('Currency', 1, 70, 'text', lambda x, d, p: x[3]),
                      ('Project/Prospect', 1, 200, 'text', lambda x, d, p: x[4]),
                      ('Product Group', 1, 150, 'text', lambda x, d, p: x[5]),
                      ('State', 1, 70, 'text', lambda x, d, p: x[6]),
                      ('Week Status', 1, 200, 'text', lambda x, d, p: x[7]),
        ]
       
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['Customer', 'Sales Order', 'Amount', 'Currency', 'Project/Prospect', 'Product Group', 'State', 'Week Status'])
        self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
        
        row_count = 1
        for x in data['csv']:
            ws.write(row_count, 0, x[0])
            ws.write(row_count, 1, x[1])
            ws.write(row_count, 2, x[2])
            ws.write(row_count, 3, x[3])
            ws.write(row_count, 4, x[4])
            ws.write(row_count, 5, x[5])
            ws.write(row_count, 6, x[6])
            y = 7
            for a in x[7].split(','):
                ws.write(row_count, y, a[2:-1])
                y += 1
            row_count += 1
            
        pass

weekly_status_xls('report.status.mingguan.excel', 'week.status', 'addons/ad_sales_project/report/report_sales.rml', parser=Sales, header=False)
