import re
import time
import xlwt
import pooler
from report import report_sxw
from report_engine_xls import report_xls

class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'koma': self.FormatWithCommas,
        })

        self.re_digits_nondigits = re.compile(r'\d+|\D+')
        
    def FormatWithCommas(self, format, value):
        parts = self.re_digits_nondigits.findall(format % (value,))
        for i in xrange(len(parts)):
            s = parts[i]
            if s.isdigit():
                parts[i] = self.commafy(s)
                break
        return ''.join(parts)
        
    def commafy(self, s):
        r = []
        for i, c in enumerate(reversed(s)):
            if i and (not (i % 3)):
                r.insert(0, ',')
            r.insert(0, c)
        return ''.join(r)

class product_summary_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Product'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1

        cols_specs = [
                      ('Sales Order', 1, 70, 'text', lambda x, d, p: x[0]),
                      ('PO Customer', 1, 70, 'text', lambda x, d, p: x[1]),
                      ('Product', 1, 200, 'text', lambda x, d, p: x[2]),
                      ('Quantity', 1, 70, 'text', lambda x, d, p: x[3]),
                      ('UoM', 1, 70, 'text', lambda x, d, p: x[4]),
                      ('Amount', 1, 70, 'text', lambda x, d, p: x[5]),
                      ('Currency', 1, 50, 'text', lambda x, d, p: x[6]),
        ]
        
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['Sales Order', 'PO Customer', 'Product', 'Quantity', 'UoM', 'Amount', 'Currency'])
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
            row_count += 1
        pass

product_summary_xls('report.management.summary.product', 'management.summary', 'addons/ad_report_management/report/report_summary_product.mako', parser=ReportStatus, header=False)
       

class order_summary_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Order PSM'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1

        cols_specs = [
                      ('Group', 1, 70, 'text', lambda x, d, p: x[0]),
                      ('Customer', 1, 120, 'text', lambda x, d, p: x[1]),
                      ('Amount', 1, 120, 'text', lambda x, d, p: x[2]),
        ]
        
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['Group', 'Customer', 'Amount'])
        self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
              
        row_count = 1
        for x in data['csv']:
            ws.write(row_count, 0, x[0])
            ws.write(row_count, 1, x[1])
            ws.write(row_count, 2, x[2])
            row_count += 1
     
        pass

order_summary_xls('report.management.summary.order', 'management.summary', 'addons/ad_report_management/report/report_summary_product.mako', parser=ReportStatus, header=False)



class quo_summary_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Order Regional'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1

        cols_specs = [
                      ('Group', 1, 70, 'text', lambda x, d, p: x[0]),
                      ('Customer', 1, 120, 'text', lambda x, d, p: x[1]),
                      ('Amount', 1, 120, 'text', lambda x, d, p: x[2]),
        ]
        
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['Group', 'Customer', 'Amount'])
        self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
              
        row_count = 1
        for x in data['csv']:
            ws.write(row_count, 0, x[0])
            ws.write(row_count, 1, x[1])
            ws.write(row_count, 2, x[2])
            row_count += 1
     
        pass

quo_summary_xls('report.management.summary.quo', 'management.summary', 'addons/ad_report_management/report/report_summary_product.mako', parser=ReportStatus, header=False)



class activity_summary_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Sales Resume'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 1
        ws.fit_width_to_pages = 1
        
        cols_specs = [
                      ('Period', 2, 0, 'text', lambda x, d, p: data['judul']['period']),
                      ('Salesman', 2, 0, 'text', lambda x, d, p: data['judul']['nama']),
                      ('Customer', 1, 170, 'text', lambda x, d, p: x[0]),
                      ('Hari', 1, 70, 'text', lambda x, d, p: x[1]),
        ]
         
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
        
        row_hdr1 = self.xls_row_template(cols_specs, ['Period'])
        row_hdr2 = self.xls_row_template(cols_specs, ['Salesman'])
        title = self.xls_row_template(cols_specs, ['Customer', 'Hari'])
        
        self.xls_write_row(ws, None, data, parser, 0, row_hdr1, hdr_style)
        self.xls_write_row(ws, None, data, parser, 1, row_hdr2, hdr_style)
        
        self.xls_write_row_header(ws, 2, title, style, set_column_size=True)
              
        #ws.write(1, 0, 'Period : %s' % data['judul']['period'])
        #ws.write(2, 0, 'Salesman : %s' % data['judul']['nama'])
                      
        row_count = 3
        for x in data['csv']:
            ws.write(row_count, 0, x)
            ws.write(row_count, 1, data['csv'][x])
            row_count += 1
     
        pass

activity_summary_xls('report.management.summary.activity', 'management.summary', 'addons/ad_report_management/report/report_summary_product.mako', parser=ReportStatus, header=False)



class sales_summary_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Sales Resume'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 1
        ws.fit_width_to_pages = 1
        
        cols_specs = [
                      ('GROUP', 1, 150, 'text', lambda x, d, p: x[0]),
                      ('SALES PERIOD', 1, 150, 'text', lambda x, d, p: x[1]),
                      ('SALES ACHIEVEMENT', 1, 150, 'text', lambda x, d, p: x[2]),
        ]
         
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['GROUP', 'SALES PERIOD', 'SALES ACHIEVEMENT'])
        self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
                      
        row_count = 1
        print data['csv']
        for x in data['csv']:
            ws.write(row_count, 0, x[0])
            ws.write(row_count, 1, x[1])
            ws.write(row_count, 2, x[2])
            row_count += 1
     
        pass

sales_summary_xls('report.management.summary.sales', 'management.summary', 'addons/ad_report_management/report/report_summary_product.mako', parser=ReportStatus, header=False)
