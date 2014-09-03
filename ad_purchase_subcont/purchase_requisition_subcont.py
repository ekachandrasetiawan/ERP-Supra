from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
import time
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp.tools.translate import _

class purchase_requisition_subcont(osv.osv):
    _name="purchase.requisition.subcont"
    _description="Purchase Requisition Subcont"
    _order = "name desc"
    _columns = {
        'name': fields.char('Requisition Reference', size=32,required=True, readonly=True),
        'origin': fields.char('Source Document', size=32),
        'date_start': fields.datetime('Requisition Date',states={'done': [('readonly', True)], 'approved': [('readonly', True)]}),
        'date_end': fields.datetime('Requisition Deadline',states={'done': [('readonly', True)],'approved': [('readonly', True)]}),
        'user_id': fields.many2one('res.users', 'Responsible',states={'done': [('readonly', True)],'approved': [('readonly', True)]}),
        'description': fields.text('Description',states={'done': [('readonly', True)]}),
        'company_id': fields.many2one('res.company', 'Company', required=True,states={'done': [('readonly', True)]}),
        'product_ids' : fields.one2many('purchase.requisition.subcont.line','requisition_id','Products to Purchase',states={'done': [('readonly', True)],'draft2': [('readonly', True)],'draft3': [('readonly', True)],'confirm': [('readonly', True)],'approved': [('readonly', True)]}),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse',states={'done': [('readonly', True)]}),        
        'state': fields.selection([('draft1','Draft'),('revisi','Revisi'),('draft2','Product Initialized'),('draft3','Product To Send Initialized'),('confirm','Confirm'),('approved','Approved'),('cancel','Cancelled'),('done','Purchase Done')],
            'Status', track_visibility='onchange', required=True),
        'subcont_type' : fields.selection([('1','Jasa'),('2','Barang dan Jasa')],'Type Subcont',required=True),
        'product_send_ids' : fields.one2many('purchase.requisition.subcont.send.line','requisition_id','Products to Sent',readonly=True),
        'wo_ids' : fields.many2many('perintah.kerja','wizard_spk_rel','spk_id','line_ids','SPK',readonly=True),
    }
    _defaults = {
        'date_start': lambda *args: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft1',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.requisition', context=c),
        'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
        'name': '/',
        'subcont_type' : '1'
    }
    
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.requisition.subcont') or '/'
        order =  super(purchase_requisition_subcont, self).create(cr, uid, vals, context=context)
        return order
    
    def cancel(self, cr, uid, ids, context=None):
        pb_obj=self.pool.get('purchase.requisition.subcont')
        pb_send_obj=self.pool.get('purchase.requisition.subcont.send.line')
        pb = pb_obj.browse(cr,uid,ids)[0]
        for send_line in pb.product_send_ids:
            pb_send_obj.unlink(cr,uid,[send_line.id])
        for line in pb.product_ids:
            pb_obj.write(cr,uid,[pb.id],{'wo_ids':[(6,0,[])]},context=context)
        return self.write(cr, uid, ids, {'state': 'cancel'})
    def save2(self, cr, uid, ids, context=None):
        pb_obj=self.pool.get('purchase.requisition.subcont')
        pb_line_obj=self.pool.get('purchase.requisition.subcont.line')
        wo_objs=[]
        pb = pb_obj.browse(cr,uid,ids)[0]
        for line in pb.product_ids:
            if line.wo_id:
                if line.wo_id.id in wo_objs:
                    continue
                wo_objs.append(line.wo_id.id)
        pb_obj.write(cr,uid,[pb.id],{'wo_ids':[(6,0,wo_objs)]},context=context)
        return self.write(cr, uid, ids, {'state':'draft2'} ,context=context)
    def generate_product(self, cr, uid, ids, context=None):
        pb_obj=self.pool.get('purchase.requisition.subcont')
        pb_send_obj=self.pool.get('purchase.requisition.subcont.send.line')
#         pb_send={}
        pb = pb_obj.browse(cr,uid,ids)[0]
        for line in pb.product_ids:
            if line.product_send_ids:
                for send_line in line.product_send_ids:
#                     pb_send.update({
#                         'product_id':send_line.product_id.id,
#                         'product_qty':send_line.product_qty,
#                         'product_uom_id':send_line.product_uom_id.id,
#                         'requisition_id':line.requisition_id.id,
#                     })
                    pb_send_obj.create(cr, uid, {
                        'product_id':send_line.product_id.id,
                        'product_qty':send_line.product_qty,
                        'product_uom_id':send_line.product_uom_id.id,
                        'requisition_id':line.requisition_id.id,
                    } ,context=context)
#         if pb_send:
#             self.write(cr, uid, ids, {'product_send_ids':pb_send} ,context=context)
        return self.write(cr, uid, ids, {'state':'draft3'} ,context=context)
    def confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'confirm'} ,context=context)
    def approve(self, cr, uid, ids, context=None):
        pb_obj=self.pool.get('purchase.requisition.subcont')
        pb_line_obj=self.pool.get('purchase.requisition.subcont.line')
        pb = pb_obj.browse(cr,uid,ids)[0]
        for line in pb.product_ids:
            pb_line_obj.write(cr,uid,[line.id],{'state_line':'ready'},context=context)
        return self.write(cr, uid, ids, {'state':'approved'} ,context=context)
    
    def revisi(self, cr, uid, ids, context=None):
        pb_obj=self.pool.get('purchase.requisition.subcont')
        pb_send_obj=self.pool.get('purchase.requisition.subcont.send.line')
        pb = pb_obj.browse(cr,uid,ids)[0]
        for send_line in pb.product_send_ids:
            pb_send_obj.unlink(cr,uid,[send_line.id])
        for line in pb.product_ids:
            pb_obj.write(cr,uid,[pb.id],{'wo_ids':[(6,0,[])]},context=context)
        return self.write(cr, uid, ids, {'state':'revisi'} ,context=context)

    def reset(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft1'})

    def done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done', 'date_end':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
purchase_requisition_subcont()

class purchase_requisition_subcont_line(osv.osv):

    _name = "purchase.requisition.subcont.line"
    _description="Purchase Requisition Subcont Line"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product' ,required=True),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure',required=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),required=True),
        'requisition_id' : fields.many2one('purchase.requisition.subcont','Purchase Requisition', ondelete='cascade',readonly=True),
        'company_id': fields.related('requisition_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
        'wo_id':fields.many2one('perintah.kerja','No SPK'),
        'product_send_ids' : fields.one2many('purchase.requisition.subcont.line.to.send','line_id','Product To Send'),
        'state_line': fields.selection([('draft','Draft'),('ready','Ready To Process'),('onproses','On Proses'),('po','Purchase Order'),('done','Done')],
            'Status', track_visibility='onchange', required=True, readonly=True),
    }
    
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.requisition.line', context=c),
        'state_line' : 'draft'
    }
    
purchase_requisition_subcont_line()

class purchase_requisition_subcont_line_to_send(osv.osv):

    _name = "purchase.requisition.subcont.line.to.send"
    _description="Purchase Requisition Subcont Line to Send"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product' ,required=True),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure',required=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),required=True),
        'line_id' : fields.many2one('purchase.requisition.subcont.line','Purchase Requisition Subcont Line', ondelete='cascade',required=True),
        'company_id': fields.related('line_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
        'wo_id': fields.related('line_id','wo_id',type='many2one',relation='perintah.kerja',string='No SPK', store=True, readonly=True),
    }
    
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.requisition.line', context=c),
    }    
    
purchase_requisition_subcont_line()

class purchase_requisition_subcont_sent_line(osv.osv):

    _name = "purchase.requisition.subcont.send.line"
    _description="Purchase Requisition Subcont Send Line"
    _columns = {
        'product_id': fields.many2one('product.product', 'Product',required=True),
        'product_uom_id': fields.many2one('product.uom', 'Product Unit of Measure',required=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),required=True),
        'requisition_id' : fields.many2one('purchase.requisition.subcont','Purchase Requisition', ondelete='cascade',required=True),
        'company_id': fields.related('requisition_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
    }
    
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.requisition.line', context=c),
    }    
    
purchase_requisition_subcont_sent_line()
