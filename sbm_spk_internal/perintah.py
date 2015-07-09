import time
import netsvc
import decimal_precision as dp
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta


class perintah_kerja_internal(osv.osv):
    _name = "perintah.kerja.internal"
    _columns = {
        'name': fields.char('Work Order', required=True, size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'date' : fields.date('Order Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'type': fields.selection([('other', 'Others'), ('pabrikasi', 'Pabrikasi'), ('man', 'Man Power'), ('service', 'Service')], 'Type', readonly=True, states={'draft': [('readonly', False)]}),
        # 'sale_id': fields.many2one('sale.order', 'Sale Order', required=True, readonly=True, domain=[('state','in', ('progress','manual'))], states={'draft': [('readonly', False)]}),
        'no_pb': fields.char('No PB', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=', True)], readonly=True, states={'draft': [('readonly', False)]}),
        'kontrak': fields.char('Contract No', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'kontrakdate' : fields.date('Contract Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'workshop': fields.char('Working Place', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'), ('approve', 'Approved'), ('done', 'Done')], 'State', readonly=True),
        'perintah_lines': fields.one2many('perintah.kerja.line.internal', 'perintah_id', 'Work Lines', readonly=True, states={'draft': [('readonly', False)]}), 
        'delivery_date' : fields.date('Delivery Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'write_date': fields.datetime('Date Modified', readonly=True),
        'write_uid':  fields.many2one('res.users', 'Last Modification User', readonly=True),
        'create_date': fields.datetime('Date Created', readonly=True),
        'create_uid':  fields.many2one('res.users', 'Creator', readonly=True),
        'creator' : fields.many2one('res.users', 'Created by'),
        'checker' : fields.many2one('res.users', 'Checked by'),
        'approver' : fields.many2one('res.users', 'Approved by'),
        'note': fields.text('Notes'),
        'terms':fields.text('Terms & Condition'),
        'location_src_id': fields.many2one('stock.location', 'Raw Materials Location', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'location_dest_id': fields.many2one('stock.location', 'Finished Products Location', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        
    }
    
    _defaults = {
        'name': '/',
        'note': '-',
        'type': 'pabrikasi',
        'state': 'draft',
        'location_src_id': 12,
        'location_dest_id': 12,
        'date': time.strftime('%Y-%m-%d'),
        'kontrakdate': time.strftime('%Y-%m-%d'), 
    }
     
    _order = "name desc"
    
    def create(self, cr, uid, vals, context=None): 
        person = self.pool.get('res.users').browse(cr, uid, uid)
        rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
        # usa = str(self.pool.get('sale.order').browse(cr, uid, vals['sale_id']).user_id.initial)
        val = self.pool.get('ir.sequence').get(cr, uid, 'perintah.kerja').split('/')
        use = str(person.initial)
        vals['creator'] = person.id
        # vals['name'] = val[-1]+'A/SBM-ADM/'+usa+'-'+use+'/'+rom[int(val[2])]+'/'+val[1]
        vals['name'] = val[-1]+'A/SBM-ADM/'+'-'+use+'/'+rom[int(val[2])]+'/'+val[1]
        return super(perintah_kerja_internal, self).create(cr, uid, vals, context=context)

    def sale_change(self, cr, uid, ids, sale):
        if sale:
            res = {}; line = []
            obj_sale = self.pool.get('sale.order').browse(cr, uid, sale)
            for x in obj_sale.order_line:
                line.append({
                             'product_id' : x.product_id.id,
                             'product_qty': x.product_uom_qty,
                             'product_uom': x.product_uom.id,
                             'name': x.name
                             # 'name': '['+str(x.product_id.code)+']' + ' ' + str(x.product_id.name)
                             })
              
            res['perintah_lines'] = line
            res['kontrak'] = obj_sale.client_order_ref
            res['partner_id'] = obj_sale.partner_id.id
            res['kontrakdate'] = obj_sale.date_order
            res['delivery_date'] = obj_sale.delivery_date
             
            return  {'value': res}
        return True

    def work_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True                                  
         
    def work_confirm(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        if not val.perintah_lines:
            raise osv.except_osv(('Perhatian !'), ('Tabel work line harus diisi !'))
        self.write(cr, uid, ids, {'state': 'approve', 'checker': self.pool.get('res.users').browse(cr, uid, uid).id})
        return True

    def work_validate(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids, context={})[0]
        if val.type == 'pabrikasi' :
            material_id = self.pool.get('stock.picking').create(cr,uid, {
                                    'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.internal'),
                                    'origin': val.name,
                                    'type': 'internal',
                                    'move_type': 'one',
                                    'state': 'auto',
                                    'date': val.date,
                                    'auto_picking': True,
                                    'company_id': 1,
                                })
            
            goods_id = self.pool.get('stock.picking').create(cr,uid, {
                                    'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.internal'),
                                    'origin': val.name,
                                    'type': 'internal',
                                    'move_type': 'one',
                                    'state': 'auto',
                                    'date': val.date,
                                    'auto_picking': True,
                                    'company_id': 1,
                                })
            
            # for x in val.material_lines:
            #     self.pool.get('stock.move').create(cr,uid, {
            #                         'name': x.product_id.default_code + x.product_id.name_template,
            #                         'picking_id': material_id,
            #                         'product_id': x.product_id.id,
            #                         'product_qty': x.product_qty,
            #                         'product_uom': x.product_uom.id,
            #                         'date': val.date,
            #                         'location_id': val.location_src_id.id,
            #                         'location_dest_id': 7,
            #                         'state': 'waiting',
            #                         'company_id': 1})
                
            for x in val.perintah_lines:
                self.pool.get('stock.move').create(cr,uid, {
                                    'name': x.product_id.default_code + x.product_id.name_template,
                                    'picking_id': goods_id,
                                    'product_id': x.product_id.id,
                                    'product_qty': x.product_qty,
                                    'product_uom': x.product_uom.id,
                                    'date': val.date,
                                    'location_id': 7,
                                    'location_dest_id': val.location_dest_id.id,
                                    'state': 'waiting',
                                    'company_id': 1})
                
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', goods_id, 'button_confirm', cr)
            wf_service.trg_validate(uid, 'stock.picking', material_id, 'button_confirm', cr)
                            
        self.write(cr, uid, ids, {'state': 'done', 'approver': self.pool.get('res.users').browse(cr, uid, uid).id})
        return True
           
    def unlink(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids, context={})[0]
        if val.state != 'draft':
            raise osv.except_osv(('Invalid action !'), ('Cannot delete a work order which is in state \'%s\'!') % (val.state,))
        return super(perintah_kerja, self).unlink(cr, uid, ids, context=context)
     

    def print_perintah(self, cr, uid, ids, context=None):
        data = {}
        val = self.browse(cr, uid, ids)[0]
        data['form'] = {}
        data['ids'] = context.get('active_ids',[])
        data['form']['data'] = self.read(cr, uid, ids)[0]
                
        qty = ''
        product = ''
        for x in val.perintah_lines:
            qty = qty + str(x.product_qty) + ' ' + x.product_uom.name + '\n\n'
            product = product + x.name + '\n\n'
            
        product = product + '\n\n' + val.note 
        
        data['form']['data']['qty'] = qty
        data['form']['data']['product'] = product
        data['form']['data']['creator'] = val.creator.name
        data['form']['data']['checker'] = val.checker.name
        data['form']['data']['approver'] = val.approver.name
         
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'perintah.A4',
                'datas': data,
                'nodestroy':True
        }
        
perintah_kerja_internal()


class perintah_kerja_line_internal(osv.osv):
    _name = "perintah.kerja.line.internal"
    _columns = {
        'no': fields.char('No', size=3),
        'name': fields.text('Description'),
        'perintah_id': fields.many2one('perintah.kerja.internal', 'Work Order', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'UoM'),
    }

    _defaults = {
        'product_uom': 1, 
    }
     
     
    def product_change(self, cr, uid, ids, product):
        if product:
            obj_product = self.pool.get('product.product').browse(cr, uid, product)
            res = {'name': '[' + obj_product.code + '] ' + obj_product.name}
            return  {'value': res}
        return True
        
perintah_kerja_line_internal()
