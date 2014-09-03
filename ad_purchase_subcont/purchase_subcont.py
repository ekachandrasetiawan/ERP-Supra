from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
import time
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp.tools.translate import _

class purchase_subcont(osv.osv):
    _inherit='purchase.order'
    _description='Purchase Order Subcont'
    
    _columns={
        'wo_ids' : fields.many2many('perintah.kerja','wo_relation','production_id','wo_id','SPK',readonly=True),
        'pb_ids' : fields.many2many('purchase.requisition.subcont','pb_rel','line_id','pb_id','PB',readonly=True),
        'rm_sent':fields.boolean('Raw Material Sent', readonly=True, select=True, help="It indicates that a Raw Material has been sent"),
        'product_sent_ids' : fields.one2many('purchase.order.subcont.sent.line','order_id','Products to Sent',readonly=True),
    }
    
    _default={
        'jenis' : 'loc',
    }
    
    def _prepare_do_picking(self, cr, uid, order, context=None):
        return {
            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out'),
            'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
            'type': 'out',
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'company_id': order.company_id.id,
            'move_lines' : [],
        }
    
    def _prepare_do_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        return {
            'name': order_line.product_id.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uom': order_line.product_uom_id.id,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'location_id': order.location_id.id,
            'location_dest_id': order.partner_id.property_stock_customer.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'state': 'draft',
            'type':'out',
            'company_id': order.company_id.id,
        }
    
    def action_picking_create(self, cr, uid, ids, context=None):
        picking_ids = []
        todo_moves=[]
        for order in self.browse(cr, uid, ids):
            if order.product_sent_ids:
                stock_move_obj=self.pool.get('stock.move')
                stock_picking_obj=self.pool.get('stock.picking')
                stock_picking_out_obj=self.pool.get('stock.picking.out')
                do_id = stock_picking_obj.create(cr, uid, self._prepare_do_picking(cr, uid, order, context=context))
                for line in order.product_sent_ids:
                    mv=stock_move_obj.create(cr, uid, self._prepare_do_line_move(cr, uid, order, line , do_id, context=context))
                    todo_moves.append(mv)
                stock_move_obj.action_confirm(cr, uid, todo_moves)
                stock_move_obj.force_assign(cr, uid, todo_moves)
                
            picking_ids.extend(self._create_pickings(cr, uid, order, order.order_line, None, context=context))

        # Must return one unique picking ID: the one to connect in the subflow of the purchase order.
        # In case of multiple (split) pickings, we should return the ID of the critical one, i.e. the
        # one that should trigger the advancement of the purchase workflow.
        # By default we will consider the first one as most important, but this behavior can be overridden.
        return picking_ids[0] if picking_ids else False
         
purchase_subcont()

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    _columns = {
        'pb_id' : fields.many2one('purchase.requisition.subcont','No PB',readonly=True),
        'wo_id' : fields.related('line_pb_subcont_id','wo_id',type='many2one',relation='mrp.production',string='No SPK',store=True,readonly=True),
        'line_pb_subcont_id' : fields.many2one('purchase.requisition.subcont.line','Product PB'),
    }
     
    def unlink(self,cr,uid,ids,context=None):
        if context is None:
            context={}
        
        po_obj=self.pool.get('purchase.order')
        po_line_obj=self.pool.get('purchase.order.line')
        pb_line_obj=self.pool.get('purchase.requisition.subcont.line')
        po_send_obj=self.pool.get('purchase.order.subcont.sent.line')
        
        po_line=po_line_obj.browse(cr,uid,ids)[0]
        if po_line.line_pb_subcont_id:
            po=po_obj.browse(cr,uid,[po_line.order_id.id])[0]
            for po_send in po.product_sent_ids:
                if po_send.pb_line_id.id==po_line.line_pb_subcont_id.id:
                    po_send_obj.unlink(cr,uid,po_send.id)
            wo_objs=[]
            pb_objs=[]
            for po_line1 in po.order_line:
                if po_line1.id==po_line.id:
                    continue
                wo_objs.append(po_line1.wo_id.id)
                pb_objs.append(po_line1.pb_id.id)
            wo_objs=[x for x in set(wo_objs)]
            pb_objs=[y for y in set(pb_objs)]
            po_obj.write(cr,uid,[po.id],{'wo_ids':[(6,0,wo_objs)]},context=context)
            po_obj.write(cr,uid,[po.id],{'pb_ids':[(6,0,pb_objs)]},context=context)
            pb_line_obj.write(cr,uid,[po_line.line_pb_subcont_id.id],{'state_line':'ready'})
                    
        return super(purchase_order_line,self).unlink(cr,uid,ids,context=context)
            
purchase_order_line()

class purchase_order_subcont_sent_line(osv.osv):

    _name = "purchase.order.subcont.sent.line"
    _description="Purchase Order Subcont Sent Line"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product' ),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'pb_line_id':fields.many2one('purchase.requisition.subcont.line','PB Line'),
        'order_id': fields.many2one('purchase.order','Purchase Order Subcont', ondelete='cascade'),
        'company_id': fields.related('order_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
    }
    
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.order', context=c),
    }    
    
purchase_order_subcont_sent_line()

class account_analytic_account(osv.osv):
    _inherit = "account.analytic.account"
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code']+' '+name
            res.append((record['id'],name ))
        return res
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if context is None:
            context={}
        if context.get('current_model') == 'project.project':
            project_obj = self.pool.get("account.analytic.account")
            project_ids = project_obj.search(cr, uid, args)
            return self.name_get(cr, uid, project_ids, context=context)
        if name:
            account_ids = self.search(cr, uid, [('code', '=', name)] + args, limit=limit, context=context)
            if not account_ids:
                dom = []
                for name2 in name.split('/'):
                    name = name2.strip()
                    account_ids = self.search(cr, uid, dom + [('code', 'ilike', name)] + args, limit=limit, context=context)
                    if not account_ids: break
                    dom = [('parent_id','in',account_ids)]
        else:
            account_ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, account_ids, context=context)
account_analytic_account()