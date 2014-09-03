import time
import datetime
import calendar
import base64
from osv import fields, osv



class sale_order_summary(osv.osv_memory):
    _name = "sale.order.summary"
    _columns = {
        'from' : fields.date('From', required=True),
        'to' : fields.date('To', required=True),
        'name': fields.selection([('date', 'Date'), ('order', 'Sales Order')], 'Filter by', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=', True)], required=True),
        'sale_ids': fields.many2many('sale.order', 'sale_line_rel', 'sale_line_id', 'sale_id', 'Sale Order', domain="[('partner_id','=',partner_id)]"),
        'type': fields.selection([('out', 'Outstanding'), ('note', 'Delivery Note')], 'Type Report'),
    }  
     
    _defaults = {
                 'name':'date',
                 'type':'out',
                 'from': time.strftime('%Y-%m-%d'),
                 'to': time.strftime('%Y-%m-%d'),
    }
           
    def sales_summary(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sale.order.summary'
        datas['form'] = self.read(cr, uid, ids)[0]
        
        report = 'sale.outstanding'
        if datas['form']['type'] == 'note': 
            report = 'sale.note'
            
        return {
                'type': 'ir.actions.report.xml',
                'report_name': report,
                'report_type': 'webkit',
                'datas': datas,
            }

sale_order_summary()


