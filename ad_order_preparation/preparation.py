import time
import netsvc
import decimal_precision as dp
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta


class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'initial' : fields.char('Initial', size=254),
    }
    
res_users()


class order_preparation(osv.osv):
    _name = "order.preparation"
    _columns = {
        'name': fields.char('Reference', required=True, size=64, select=True, readonly=False, states={'draft': [('readonly', False)]}),
        'poc': fields.char('Customer Reference', size=64),
        'tanggal' : fields.date('Date Preparation', readonly=True, states={'draft': [('readonly', False)]}),
        'duedate' : fields.date('Delivery Date', readonly=True, states={'draft': [('readonly', False)]}),
        'sale_id': fields.many2one('sale.order', 'Sale Order', select=True, required=True, readonly=True, domain=[('state','in', ('progress','manual'))], states={'draft': [('readonly', False)]}),
        'picking_id': fields.many2one('stock.picking', 'Delivery Order', required=True, domain="[('sale_id','=', sale_id), ('state','not in', ('cancel','done'))]", readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'), ('approve', 'Approved'), ('cancel', 'Cancel'), ('done', 'Done')], 'State', readonly=True),
        'prepare_lines': fields.one2many('order.preparation.line', 'preparation_id', 'Packaging Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_lines': fields.one2many('delivery.note', 'prepare_id', 'Delivery Lines', readonly=True),
        'write_date': fields.datetime('Date Modified', readonly=True),
        'write_uid':  fields.many2one('res.users', 'Last Modification User', readonly=True),
        'create_date': fields.datetime('Date Created', readonly=True),
        'create_uid':  fields.many2one('res.users', 'Creator', select=True, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Customer', select=True, domain=[('customer','=', True)], readonly=True, states={'draft': [('readonly', False)]}),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', domain=[('customer','=', True)], readonly=True, states={'draft': [('readonly', False)]}),
        'note': fields.text('Notes'),
        'terms':fields.text('Terms & Condition'),
    }
    

    def print_preparationA5(self, cr, uid, ids, context=None):
        data = {}
        val = self.browse(cr, uid, ids)[0]
        data['form'] = {}
        data['ids'] = context.get('active_ids',[])
        data['form']['data'] = self.read(cr, uid, ids)[0]
        
        data['form']['data']['street'] = val.partner_id.street
        data['form']['data']['jalan'] = val.partner_id.street2
        data['form']['data']['phone'] = val.partner_id.phone
        
        qty = ''
        product_name = ''
        product_code = ''
        for x in val.prepare_lines:
            qty = qty + str(x.product_qty) + ' ' + x.product_uom.name + '\n\n'
            product_name = product_name + x.name + '\n\n'
            product_code = product_code + x.product_id.code + '\n\n'
        
        data['form']['data']['qty'] = qty
        data['form']['data']['product_name'] = product_name
        data['form']['data']['product_code'] = product_code
         
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'preparation.A5',
                'datas': data,
                'nodestroy':True
        }
    
    def print_preparationA4(self, cr, uid, ids, context=None):
        data = {}
        val = self.browse(cr, uid, ids)[0]
        data['form'] = {}
        data['ids'] = context.get('active_ids',[])
        data['form']['data'] = self.read(cr, uid, ids)[0]
        
        data['form']['data']['street'] = str(val.partner_id.street)
        data['form']['data']['jalan'] = str(val.partner_id.street2)
        data['form']['data']['phone'] = str(val.partner_id.phone)
        
        qty = ''
        product_name = ''
        product_code = ''
        for x in val.prepare_lines:
            qty = qty + str(x.product_qty) + ' ' + x.product_uom.name + '\n\n'
            product_name = product_name + x.name + '\n\n'
            product_code = product_code + x.product_id.code + '\n\n'
        
        data['form']['data']['qty'] = qty
        data['form']['data']['product_name'] = product_name
        data['form']['data']['product_code'] = product_code
         
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'preparation.A4',
                'datas': data,
                'nodestroy':True
        }

    def print_preparationA4_rev(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'order.preparation'
        datas['form'] = self.read(cr, uid, ids)[0]
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'print.opA4',
            'report_type': 'webkit',
            'datas': datas,
            }
            
    def create(self, cr, uid, vals, context=None):    
        rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
        usa = str(self.pool.get('sale.order').browse(cr, uid, vals['sale_id']).user_id.initial)
        val = self.pool.get('ir.sequence').get(cr, uid, 'pesan.antar').split('/')
        use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
        vals['name'] = val[-1]+'B/SBM-ADM/'+usa+'-'+use+'/'+rom[int(val[2])]+'/'+val[1]
        return super(order_preparation, self).create(cr, uid, vals, context=context)
 
    def preparation_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True                                  
 
    def preparation_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True                                  
         
    def preparation_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approve'})
        return True

    def preparation_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        return True                                  
          
    def unlink(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids, context={})[0]
        if val.state != 'draft':
            raise osv.except_osv(('Invalid action !'), ('Cannot delete a order preparation which is in state \'%s\'!') % (val.state,))
        return super(order_preparation, self).unlink(cr, uid, ids, context=context)
    
    def sale_change(self, cr, uid, ids, sale):
        
        if sale:
            res = {}
            obj_sale = self.pool.get('sale.order').browse(cr, uid, sale)
            res['prepare_lines'] = [] 
            res['poc'] = obj_sale.client_order_ref
            res['picking_id'] = False
            res['partner_id'] = obj_sale.partner_id.id
            res['duedate'] = obj_sale.delivery_date
            res['partner_shipping_id'] = obj_sale.partner_shipping_id.id
            
            return  {'value': res}
    
    def picking_change(self, cr, uid, ids, pick):
        if pick :
            res = {}; line = []
            data = self.pool.get('stock.picking').browse(cr, uid, pick)
            for x in data.move_lines:
                line.append({
                             'no': x.sale_line_id.sequence,
                             'product_id' : x.product_id.id,
                             'product_qty': x.product_qty,
                             'product_uom': x.product_uom.id,
                             'name': x.name
                             })
             
            res['prepare_lines'] = line
            return  {'value': res}
        
        
    _defaults = {
        'name': '/',
        'state': 'draft',
        'tanggal': time.strftime('%Y-%m-%d'), 
    }
     
        
order_preparation()
 
class order_preparation_line(osv.osv):
    _name = "order.preparation.line"
    _columns = {
        'no': fields.char('No', size=3),
        'name': fields.text('Description'),
        'preparation_id': fields.many2one('order.preparation', 'Order Preparation', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'UoM'),
        'product_packaging': fields.many2one('product.packaging', 'Packaging'),
    }
         
order_preparation_line()

#         'spkdate' : fields.date('SPK Date', readonly=True, states={'draft': [('readonly', False)]}),
#         'kontrak': fields.char('Contract No', size=64, readonly=True, states={'draft': [('readonly', False)]}),
#         'kontrakdate' : fields.date('Contract Date', readonly=True, states={'draft': [('readonly', False)]}),
#         'workshop': fields.char('Working Place', size=64, readonly=True, states={'draft': [('readonly', False)]}),
#         'dodate' : fields.datetime('Delivery Date', readonly=True, states={'draft': [('readonly', False)]}),
#         'gudang': fields.char('Warehouse', size=64, readonly=True, states={'draft': [('readonly', False)]}),
#         'suratjalan': fields.char('DO No', required=True, size=64, readonly=True, states={'draft': [('readonly', False)]}),
#         'suratkerja': fields.char('WO No', required=True, size=64, readonly=True, states={'draft': [('readonly', False)]}),
#         'do': fields.boolean('DO ?', help="Check jika ada DO"),
#         'spk': fields.boolean('WO ?', help="Check jika ada SPK"),

    
#     def spk_change(self, cr, uid, ids, spk, sale):
#         # ex: 000001A/SBM-ADM/JH-NR/X/13
#         if not sale:
#             raise osv.except_osv(('Attention !'), ('Please select a sales order!'))    
#         kerja = '/'
#         rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
#         if spk:
#             usa = str(self.pool.get('sale.order').browse(cr, uid, sale).user_id.initial)
#             val = self.pool.get('ir.sequence').get(cr, uid, 'perintah.kerja').split('/')
#             use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
#             kerja = val[-1]+'A/SBM-ADM/'+usa+'-'+use+'/'+rom[int(val[2])]+'/'+val[1]
#         return  {'value': {'suratkerja': kerja}}
#     
#     def do_change(self, cr, uid, ids, do, sale):
#         # ex: 000001B/SBM-ADM/JH-NR/X/13
#         if not sale:
#             raise osv.except_osv(('Attention !'), ('Please select a sales order!'))
#         kirim = '/'
#         rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
#         if do:
#             usa = str(self.pool.get('sale.order').browse(cr, uid, sale).user_id.initial)
#             val = self.pool.get('ir.sequence').get(cr, uid, 'pesan.antar').split('/')
#             use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
#             kirim = val[-1]+'B/SBM-ADM/'+usa+'-'+use+'/'+rom[int(val[2])]+'/'+val[1]
#         return  {'value': {'suratjalan': kirim}}
    
#     def sale_change(self, cr, uid, ids, sale):
#         
#         if sale:
#             res = {}
#             obj_sale = self.pool.get('sale.order').browse(cr, uid, sale)
#             res['prepare_lines'] = [] 
#             res['picking_id'] = False
#             res['partner_id'] = obj_sale.partner_id.id
#             res['kontrak'] = obj_sale.client_order_ref
#              
#             return  {'value': res}
