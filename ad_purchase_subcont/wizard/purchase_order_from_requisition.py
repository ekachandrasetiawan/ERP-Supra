import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

class purchase_order_line_from_requisition_lines(osv.osv_memory):
    _name = "purchase.order.line.from.requisition.lines"
    _description = "Entries by PO Lines from Requisition Lines"
    _columns = {
        'line_ids': fields.many2many('purchase.requisition.subcont.line', 'wizard_purchase_requisition_rel', 'purchase_requisition_id', 'line_id', 'Purchase Requisitions'),
    }

    def populate_order_lines(self, cr, uid, ids, context=None):
        po_obj=self.pool.get('purchase.order')
        po_line_obj=self.pool.get('purchase.order.line')
        po_send_line_obj=self.pool.get('purchase.order.subcont.sent.line')
        pb_subcont_line_obj=self.pool.get('purchase.requisition.subcont.line')
        
        if context is None:
            context={}
        spk=context.get('spk_list')[0][2]
        po_id=context.get('po_id')
        

        print '======================',po_id
        if not po_id:
            return {'type': 'ir.actions.act_window_close'}
        
        data = self.read(cr,uid,ids,context=context)[0]
        line_ids=data['line_ids']
        
        po=po_obj.browse(cr,uid,po_id,context=context)
        pb_objs=[]
        wo_objs=[]
        for x in po.pb_ids:
            pb_objs.append(x.id)
        for y in po.wo_ids:
            wo_objs.append(y.id)
        
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}
        
        for line in pb_subcont_line_obj.browse(cr,uid,line_ids,context=context):
            
            if po_line_obj.search(cr,uid,[('line_pb_subcont_id','=',line.id)]):
                continue
            else:
                if line.requisition_id.id not in pb_objs:
                    pb_objs.append(line.requisition_id.id)
                    po_obj.write(cr,uid,[po.id],{'pb_ids':[(6,0,pb_objs)]},context=context)
                if line.wo_id:
                    if line.wo_id.id not in wo_objs:
                        wo_objs.append(line.wo_id.id)
                        po_obj.write(cr,uid,[po.id],{'wo_ids':[(6,0,wo_objs)]},context=context)
                po_obj.write(cr,uid,[po.id],{'type_permintaan':'3'},context=context)
                po_line_obj.create(cr,uid, {
                        'product_id':line.product_id.id,
                        'name': line.product_id.name,
                        'date_planned' : po.date_order,
                        'pb_id':line.requisition_id.id,
                        'product_qty' : line.product_qty,
                        'product_uom' : line.product_uom_id.id,
                        'price_unit' : 0.0,
                        'order_id':po_id,
                        'line_pb_subcont_id':line.id,
                    },context=context)      
                for send_line in line.product_send_ids:
                    po_send_line_obj.create(cr, uid, {
                            'product_id':send_line.product_id.id,
                            'product_qty':send_line.product_qty,
                            'product_uom_id':send_line.product_uom_id.id,
                            'pb_line_id':line.id,
                            'order_id':po_id,
                        } ,context=context)
                pb_subcont_line_obj.write(cr,uid,[line.id],{'state_line':'onproses'})
            
        return {'type': 'ir.actions.act_window_close'}

purchase_order_line_from_requisition_lines()
