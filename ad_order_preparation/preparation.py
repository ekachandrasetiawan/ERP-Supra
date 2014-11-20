import time
import netsvc
import openerp.exceptions
import decimal_precision as dp
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare


class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'initial' : fields.char('Initial', size=254),
    }
    
res_users()


class product_batch(osv.osv):
    _description = 'Product Batch Delivery Order'
    _name = 'product.batch.line'
    _columns = {
        'nama':fields.char('Serial Number',size=64),
        'preparation_id': fields.many2one('order.preparation', 'Order Preparation', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product',track_visibility='always'),
        'desc':fields.char('Description', size=64),
        'product_qty':fields.integer('Product Qty'),
    }

product_batch()

class order_preparation(osv.osv):
    _name = "order.preparation"
    _description = "Order Packaging"
    _columns = {
        'name': fields.char('Reference', required=True, size=64, select=True, readonly=False, states={'draft': [('readonly', False)]}),
        'poc': fields.char('Customer Reference', size=64,track_visibility='onchange'),
        'tanggal' : fields.date('Date Preparation', readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange'),
        'duedate' : fields.date('Delivery Date', readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange'),
        'sale_id': fields.many2one('sale.order', 'Sale Order', select=True, required=True, readonly=True, domain=[('state','in', ('progress','manual'))], states={'draft': [('readonly', False)]}),
        'picking_id': fields.many2one('stock.picking', 'Delivery Order', required=True, domain="[('sale_id','=', sale_id), ('state','not in', ('cancel','done'))]", readonly=True, states={'draft': [('readonly', False)]},track_visibility='always'),
        
        'prepare_lines': fields.one2many('order.preparation.line', 'preparation_id', 'Packaging Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'delivery_lines': fields.one2many('delivery.note', 'prepare_id', 'Delivery Lines', readonly=True),
        'write_date': fields.datetime('Date Modified', readonly=True),
        'write_uid':  fields.many2one('res.users', 'Last Modification User', readonly=True),
        'create_date': fields.datetime('Date Created', readonly=True),
        'create_uid':  fields.many2one('res.users', 'Creator', select=True, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Customer', select=True, domain=[('customer','=', True)], readonly=True, states={'draft': [('readonly', False)]}),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', domain=[('customer','=', True)], readonly=True, states={'draft': [('readonly', False)]}),
        'batch_lines ': fields.one2many('product.batch.line','preparation_id','Product Batch', readonly=True, states={'draft': [('readonly', False)]}),
        'note': fields.text('Notes'),
        'terms':fields.text('Terms & Condition'),
        'state': fields.selection([('draft', 'Draft'), ('approve', 'Approved'), ('cancel', 'Cancel'), ('done', 'Done')], 'State', readonly=True),
    }
    _inherit = ['mail.thread']
    _track = {
        'note':{},
        'state':{
            'ad_order_preparation.mt_pack_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approve',
            'ad_order_preparation.mt_pack_canceled': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
            'ad_order_preparation.mt_pack_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
            'ad_order_preparation.mt_pack_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',

        },
        'prepare_lines':{

        }
    }
    
    def print_op_out(self,cr,uid,ids,context=None):
        searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
        browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
        urlTo = str(browseConf.value)+"order-preparation/print&id="+str(ids[0])+"&uid="+str(uid)
        
        
        return {
            'type'  : 'ir.actions.client',
            'target': 'new',
            'tag'   : 'print.out.op',
            'params': {
                # 'id'  : ids[0],
                'redir' : urlTo,
                'uid':uid
            },
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
        check = self.search(cr,uid,[('sale_id','=',vals['sale_id']),('picking_id','=',vals['picking_id']),('state','!=','cancel')])
        OPs = self.browse(cr,uid,check,context=None)
        if check:
            allOp = []
            for op in OPs:
                allOp.append(op.name)
                
            mm = '\n==> '.join(allOp)
            msg = 'You cannot create an Order Package which is has been exist.\n\n===> '+mm
            
            raise openerp.exceptions.Warning(msg)
        
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
        val = self.browse(cr, uid, ids)[0]
        for x in val.prepare_lines:
            product =self.pool.get('product.product').browse(cr, uid, x.product_id.id)
            if product.not_stock == False:
                 # print '=========================',product.qty_available
                mm = ' ' + product.default_code + ' '
                stock = ' ' + str(product.qty_available) + ' '
                msg = 'Stock Product' + mm + 'Tidak Mencukupi.!\n'+ ' On Hand Qty '+ stock 

                if x.product_qty > product.qty_available:
                    raise openerp.exceptions.Warning(msg)
                    return False

        self.write(cr, uid, ids, {'state': 'approve'})
        # self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def preparation_done(self, cr, uid, ids, context=None):
        setDueDateValue = time.strftime('%Y-%m-%d')
        dn_id=self.pool.get('delivery.note').search(cr,uid,[('prepare_id', '=' ,ids)])
        self.pool.get("delivery.note").write(cr, uid, dn_id, {'tanggal': setDueDateValue})
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
        'tanggal': time.strftime(DEFAULT_SERVER_DATE_FORMAT), 
    }
     
        
order_preparation()
 
class order_preparation_line(osv.osv):
    _name = "order.preparation.line"

    _columns = {
        'no': fields.integer('No', size=3),
        'name': fields.text('Description'),
        'preparation_id': fields.many2one('order.preparation', 'Order Preparation', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product',track_visibility='always'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'UoM'),
        'detail':fields.text('Detail Product'),
        'product_packaging': fields.many2one('product.packaging', 'Packaging'),
        'prodlot_id':fields.one2many('order.preparation.batch','batch_id','Serial Number', ondelete='cascade'),
    }
         
order_preparation_line()

class order_preparation_batch(osv.osv):
    _name = "order.preparation.batch"
    _columns = {
        'name':fields.many2one('stock.production.lot','Serial Number', ondelete='cascade'),
        'desc':fields.char('Description'),
        'exp_date':fields.date('Exp Date'),
        'stock_available': fields.float('Stock Available'),
        'qty': fields.float('Qty'),
        'batch_id': fields.many2one('order.preparation.line', 'Batch Product', ondelete='cascade'),
    }

    _defaults = {
        'qty': 0.0,
    }

    def product_batch(self,cr,uid,ids,prodlot_id,qty,context=None):
        hasil=self.pool.get('stock.production.lot').browse(cr,uid,[prodlot_id])[0]
        if qty > hasil.stock_available:
            raise openerp.exceptions.Warning('Stock Available Tidak Mencukupi')
            return {'value':{'qty':0}}

        return {'value':{'desc':hasil.desc,'exp_date':hasil.exp_date,'stock_available':hasil.stock_available}}
# class order_preparation(osv.osv):
#     _name = "order.preparation"
#     _description = "Order Preparation Packaging"
#     # inherit from mail.thread allows the use of OpenChatter
#     _inherit = ['mail.thread']
