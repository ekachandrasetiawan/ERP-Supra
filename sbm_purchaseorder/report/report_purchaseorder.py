import re
import time
from report import report_sxw
from osv import osv
import pooler

class Reportrachseorder(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Reportrachseorder, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'koma': self.decimal,
            'sum' : sum,
            'get_lines':self.get_lines,
            'get_amount':self.get_amount,
            })

        self.re_digits_nondigits = re.compile(r'\d+|\D+')


    def decimal(self, format, value):
        if value:
            parts = self.re_digits_nondigits.findall(format % (value,))
            for i in xrange(len(parts)):
                s = parts[i]
                if s.isdigit():
                    parts[i] = self.commafy(s)
                    break
            return ''.join(parts)
        #return True
        
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
        arrLine={}
        i=1
        diskon=0
        totaldiscount=0
        amount_untaxed=0
        for x in order_line:
            # print '=======================================',x.product_id.id
            # if x.product_id.id == 9727:
            #     print '<<<<<<<<<<<<<<aaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
            #     res.append({'no':False,'product_id':False, 'name':False,'part_no':False,'qty':False,'satuan':False,'harga':False,'total':False})
            

            if x.note_line == '-':
                res.append({'no':i,'product_id':x.product_id, 'name':x.name,'part_no':x.part_number,'qty':x.product_qty,'satuan':x.product_uom,'harga':x.price_unit,'total':x.price_unit*x.product_qty})
                i+=1
            else:
                if x.product_id.id == 9727:
                    res.append({'no':False,'product_id':False, 'name':False,'part_no':False,'qty':False,'satuan':False,'harga':False,'total':False})
                else:
                    res.append({'no':False,'product_id':False, 'name':x.note_line,'part_no':False,'qty':False,'satuan':False,'harga':False,'total':False})
                    res.append({'no':i,'product_id':x.product_id, 'name':x.name,'part_no':x.part_number,'qty':x.product_qty,'satuan':x.product_uom,'harga':x.price_unit,'total':x.price_unit*x.product_qty})
                    i+=1

        res.append({'no':False,'product_id':False, 'name':False,'part_no':False,'qty':False,'satuan':False,'harga':False,'total':False})
        res.append({'no':False,'product_id':False, 'name':obj.notes,'part_no':False,'qty':False,'satuan':False,'harga':False,'total':False})

        for x in range(0, obj.print_line-len(res)):
            res.append({'no':'-','product_id':False, 'name':False,'part_no':False,'qty':False,'satuan':False,'harga':False,'total':False})
        
        #discountamount=diskon+totaldiscount
        return res

#report_sxw.report_sxw('report.report.purchase.order', 'purchase.order', 'addons/sbm_purchaseorder/report/report_order_local.rml', parser = Reportrachseorder, header = False)
report_sxw.report_sxw('report.report.purchase.order', 'purchase.order', 'addons/sbm_purchaseorder/report/report_purchaseorder.rml', parser = Reportrachseorder, header = False)
