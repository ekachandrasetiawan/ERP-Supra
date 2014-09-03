import time
import calendar
from osv import fields, osv

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns = {
            'jenis': fields.selection([('loc', 'Local'), ('impj', 'Import J'), ('imps', 'Import S')], 'Type', readonly=True,required=True, states={'draft':[('readonly',False)]}, select=True),
            'port' : fields.char("Port Name", size=128),
            'note' : fields.text("Note"),
            'total_price':fields.char("Total Price"),
            'after_shipment':fields.text("After Shipment"),
            'shipment_to':fields.text("Shipment To"),
            'yourref' : fields.text("Your ref"),
            'delivery' : fields.text("Delivery"),
            'other' : fields.text("Other"),
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals['jenis'] == 'impj':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.importj')
        elif vals['jenis'] == 'imps':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.imports')
        else:
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order') or '/'
        order =  super(purchase_order, self).create(cr, uid, vals, context=context)
        return order

    _defaults ={
        'total_price':'TOTAL PRICE CIF JAKARTA',
        'shipment_to':'PT.SUPRABAKTI MANDIRI, Destination : JAKARTA PORT',
        'after_shipment':'After shipment, please fax me the copy of invoice, Packing List, Insurance Certificate and Bill of Lading "Telex Release"',
    }

purchase_order()


