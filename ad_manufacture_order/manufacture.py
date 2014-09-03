import time
import netsvc
import decimal_precision as dp
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta



class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale Order', required=True, readonly=True, domain=[('state','in', ('progress','manual'))], states={'draft': [('readonly', False)]}),
        'perintah_id': fields.many2one('perintah.kerja', 'Work Order', required=True, readonly=True, domain=[('state','=', 'done')], states={'draft': [('readonly', False)]}),
        'kontrak': fields.char('Contract No', size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'kontrakdate' : fields.date('Contract Date', readonly=True, states={'draft': [('readonly', False)]}),
        'workshop': fields.char('Working Place', size=64, readonly=True, states={'draft': [('readonly', False)]}),
    }
    
    def perintah_change(self, cr, uid, ids, order):
        if order:
            res = {}
            obj_order = self.pool.get('perintah.kerja').browse(cr, uid, order)
            res['sale_id'] = obj_order.sale_id.id
            res['workshop'] = obj_order.workshop
            res['kontrak'] = obj_order.sale_id.client_order_ref
            res['kontrakdate'] = obj_order.sale_id.date_order
            return  {'value': res}
        return True
        
    _defaults = {
        'kontrakdate': time.strftime('%Y-%m-%d'), 
    }
     
        
mrp_production()




#     def create(self, cr, uid, vals, context=None):    
#         rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
#         usa = str(self.pool.get('sale.order').browse(cr, uid, vals['sale_id']).user_id.initial)
#         val = self.pool.get('ir.sequence').get(cr, uid, 'perintah.kerja').split('/')
#         use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
#         vals['name'] = val[-1]+'A/SBM-ADM/'+usa+'-'+use+'/'+rom[int(val[2])]+'/'+val[1]
#         return super(mrp_production, self).create(cr, uid, vals, context=context)
    
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
