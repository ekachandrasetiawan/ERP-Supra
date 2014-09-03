import re
import time
import pooler
from osv import osv
from report import report_sxw

class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_outstanding': self.get_outstanding,
            'koma': self.FormatWithCommas,
            'get_delivered': self.get_delivered,
            'get_supplier': self.get_supplier,
            'get_basedon': self.get_basedon,
            
        })

        self.qty_total = 0
        self.price_total = 0
        self.re_digits_nondigits = re.compile(r'\d+|\D+')
     
    def get_supplier(self, form):
        if form['form']['partner_id']:
            return form['form']['partner_id'][1]
        else:
            return '-' 
            
    def get_basedon(self, form):
        if form['form']['sale_ids']:
            data = self.pool.get('sale.order').browse(self.cr, self.uid, form['form']['sale_ids'])
        else:
            idd = self.pool.get('sale.order').search(self.cr, self.uid, [('due_date', '>=', form['form']['from']), 
                                                                         ('due_date', '<=', form['form']['to'])])
            data = self.pool.get('sale.order').browse(self.cr, self.uid, idd)
        return data

    def get_delivered(self, line):
        res = 0
        dnid = self.pool.get('delivery.note').search(self.cr, self.uid, [('state', '=', 'done'), ('prepare_id', 'in', [x.id for x in line.order_id.preparation_line])])
        if dnid:
            rid = self.pool.get('delivery.note.line').search(self.cr, self.uid, [('product_id', '=', line.product_id.id), ('note_id', 'in', dnid)])
            if rid:
                for x in self.pool.get('delivery.note.line').browse(self.cr, self.uid, rid):
                    res += x.product_qty
        return res 
    
    def get_outstanding(self, line):
        res = []
        dnid = self.pool.get('delivery.note').search(self.cr, self.uid, [('prepare_id', 'in', [x.id for x in line.order_id.preparation_line])])
        if dnid:
            rid = self.pool.get('delivery.note.line').search(self.cr, self.uid, [('product_id', '=', line.product_id.id), ('note_id', 'in', dnid)])
            if rid:
                res =  self.pool.get('delivery.note.line').browse(self.cr, self.uid, rid)
        return res 
    
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

report_sxw.report_sxw('report.sale.outstanding', 'sale.order.summary', 'addons/ad_report_summary/report/report_sale_outstanding.mako', parser = ReportStatus)
report_sxw.report_sxw('report.sale.note', 'sale.order.summary', 'addons/ad_report_summary/report/report_sale_note.mako', parser = ReportStatus)
       
