import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _


class res_currency(osv.osv):
    
    def _current_rate(self, cr, uid, ids, name, arg, context=None):
        return self._current_rate_computation(cr, uid, ids, name, arg, True, context=context)

    def _current_rate_computation(self, cr, uid, ids, name, arg, raise_on_no_rate, context=None):
        if context is None:
            context = {}
        res = {}
        if 'date' in context:
            date = context['date']
        else:
            date = time.strftime('%Y-%m-%d')
        date = date or time.strftime('%Y-%m-%d')
        currency_rate_type = context.get('currency_rate_type_id') or None
        operator = '=' if currency_rate_type else 'is'
        for id in ids:
            cr.execute("SELECT currency_id, rate, rating FROM res_currency_rate WHERE currency_id = %s AND name <= %s AND currency_rate_type_id " + operator +" %s ORDER BY name desc LIMIT 1" ,(id, date, currency_rate_type))
            if cr.rowcount:
                id, rate, rating = cr.fetchall()[0]
                res[id] = rate
                self.write(cr, uid, [id], {'rating' :rating})
            elif not raise_on_no_rate:
                res[id] = 0
            else:
                raise osv.except_osv(_('Error!'),_("No currency rate associated for currency %d for the given period" % (id)))
        return res
    
    
    _inherit = "res.currency"
    _columns = {
        'rating': fields.float('Rating', readonly=True, digits=(12,6)),
        'rate': fields.function(_current_rate, string='Current Rate', digits=(12,12), help='The rate of the currency to the currency of rate 1.'),
    }

res_currency()               

class res_currency_rate(osv.osv):
    _inherit = "res.currency.rate"
    _columns = {
        'rating': fields.float('Rating', digits=(12,2)),
        'rate': fields.float('Rate', digits=(12,12), help='The rate of the currency to the currency of rate 1'),
    }    
    
    def onchange_rating(self, cr, uid, ids, rate):
        if rate:
            return {'value': {'rate': 1.0/rate}}      
        
res_currency_rate()
    
