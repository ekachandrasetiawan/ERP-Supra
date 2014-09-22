import re
import time
from osv import osv, fields
from report import report_sxw

class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'koma': self.FormatWithCommas,
            'get_no': self.get_no,
            'get_lines':self.get_lines,
            'get_amount':self.get_amount,       
        })

        self.re_digits_nondigits = re.compile(r'\d+|\D+')
        self.no = 0
        
    def get_no(self):
        self.no = self.no + 1
        return self.no 
        
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


    def get_amount(self,obj):
        order_line= obj.order_line
        res=[]
        res2={}
        arrLine={}
        i=1
        diskon=0
        totaldiscount=0
        amount_untaxed=0
        for x in order_line:
            amount_untaxed=amount_untaxed+(x.product_qty * x.price_unit)
            diskon=diskon+x.discount_nominal
            if x.discount == 0:
                pricediscount=0
            else:
                pricediscount = (x.price_unit *x.product_qty) * ( x.discount / 100 ) 
                
            totaldiscount = totaldiscount+pricediscount
                
                #arrLine.update({'no':i,'product_id':x.product_id, 'name':x.name,'part_no':x.part_number,'qty':x.product_qty,'satuan':x.product_uom,'harga':x.price_unit,'total':x.price_unit*x.product_qty,'noteline':x.note_line})
                #res.append(arrLine)
                #arrLine={}
            i+=1
        discountamount=diskon+totaldiscount
        res2['diskon']=diskon
        res2['amount_untaxed']=amount_untaxed
        res2['total_discount']=totaldiscount
        res2['discountamount']=discountamount
        return res2

    def get_lines(self,obj):
        order_line= obj.order_line
        res=[]
        i=1
        for x in order_line:
                res.append({'no':i,'product_id':x.product_id, 'name':x.name,'part_no':x.part_number,'qty':x.product_qty,'satuan':x.product_uom,'harga':x.price_unit,'total':x.price_unit*x.product_qty})
                i+=1
        return res

report_sxw.report_sxw('report.purchase.imports', 'purchase.order', 'addons/ad_purchase_import/report/imports.rml', parser=ReportStatus, header=False)
report_sxw.report_sxw('report.purchase.importj', 'purchase.order', 'addons/ad_purchase_import/report/importj.rml', parser=ReportStatus, header=False)
       

