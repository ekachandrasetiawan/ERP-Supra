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

    _order = 'id DESC'
    
    # def create(self, cr, uid, vals, context=None):
    #     try:

    #         if vals['jenis'] == 'impj':
    #             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.importj')
    #         elif vals['jenis'] == 'imps':
    #             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.imports')
    #         else:
    #             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order') or '/'
            
    #     except:
    #         vals['jenis'] = 'loc'
    #         vals['type_permintaan'] = '1'
    #         vals['duedate'] = '10/19/2015'
    #         vals['term_of_payment'] = ' '
    #     order =  super(purchase_order, self).create(cr, uid, vals, context=context)
    #     return order


    def print_po_import_out(self,cr,uid,ids,context=None):
        searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
        browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
        urlTo = str(browseConf.value)+"purchase-order/printpoimport&id="+str(ids[0])+"&uid="+str(uid)

        return {
            'type'  : 'ir.actions.client',
            'target': 'new',
            'tag'   : 'print.out.po.import',
            'params': {
                # 'id'  : ids[0],
                'redir' : urlTo,
                'uid':uid
            },
        }
    _defaults ={
        'total_price':'TOTAL PRICE CIF JAKARTA',
        'shipment_to':'PT.SUPRABAKTI MANDIRI, Destination : JAKARTA PORT',
        'after_shipment':'After shipment, please email me the copy of invoice, Packing List, and Bill of Lading "Telex Release"',
    }

purchase_order()


