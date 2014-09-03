import time
import datetime
import calendar
import base64
from osv import fields, osv
from collections import OrderedDict
                        

# class res_users(osv.osv):
#     _inherit = "res.users"
#     _columns = {
#         'salesman' : fields.boolean('Salesman ?'),
#     }
#     
# res_users()


class management_summary(osv.osv):
    _name = "management.summary"
    _columns = {
        'name': fields.selection([('quo', 'Sales Regional'), ('order', 'Sales PSM'), ('sum', 'Activity Summary'),
                                  ('prod', 'Product @ Customer'), ('sales', 'Sales Summary')], 'Type Report', required=True),
        'period_id': fields.many2one('account.period', 'Bulan', required=True, domain=[('special','=', False)]),
        'salesman_id': fields.many2one('res.users', 'Salesman'),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=', True)]),
    }  
     
    _defaults = {
                 'name':'quo',
    }
           
    def report_summary(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        data = []
        val = self.browse(cr, uid, ids)[0]
        nilai = self.read(cr, uid, ids)[0]
        datas = {'ids': [nilai['id']]}
        datas['model'] = 'management.summary'
        datas['form'] = nilai
        
        obj_order = self.pool.get('sale.order')
        obj_order_line = self.pool.get('sale.order.line')
        obj_group = self.pool.get('group.sales')  
        obj_invoice = self.pool.get('account.invoice')

        if datas['form']['name'] == 'sum':
            idd = self.pool.get('sales.activity').search(cr, uid, [('user_id', '=', val.salesman_id.id), ('begin', '>=', val.period_id.date_start), ('begin', '<', val.period_id.date_stop)])
            if idd:
                partner = {}
                dad = self.pool.get('sales.activity').browse(cr, uid, idd)
                for x in dad:
                    partner[x.id] = {'senin': [], 'selasa': [], 'rabu': [], 'kamis': [], 'jumat': []}
                    for i in x.beforeactualsenin:
                        partner[x.id]['senin'].append(i.partner_id.id)
                    for i in x.afteractualsenin:
                        partner[x.id]['senin'].append(i.partner_id.id)
                    for i in x.beforeactualselasa:
                        partner[x.id]['selasa'].append(i.partner_id.id)
                    for i in x.afteractualselasa:
                        partner[x.id]['selasa'].append(i.partner_id.id)
                    for i in x.beforeactualrabu:
                        partner[x.id]['rabu'].append(i.partner_id.id)
                    for i in x.afteractualrabu:
                        partner[x.id]['rabu'].append(i.partner_id.id)
                    for i in x.beforeactualkamis:
                        partner[x.id]['kamis'].append(i.partner_id.id)
                    for i in x.afteractualkamis:
                        partner[x.id]['kamis'].append(i.partner_id.id)
                    for i in x.beforeactualjumat:
                        partner[x.id]['jumat'].append(i.partner_id.id)
                    for i in x.afteractualjumat:
                        partner[x.id]['jumat'].append(i.partner_id.id)
                
                hasil = []
                for i in partner:
                    for o in partner[i]:
                        hasil += list(OrderedDict.fromkeys(partner[i][o]))

                clean = [x for x in list(OrderedDict.fromkeys(hasil)) if x]
                
                data = {}
                for s in self.pool.get('res.partner').browse(cr, uid, clean):
                    data[s.name] = hasil.count(s.id)
                
                datas['judul'] = {'period': val.period_id.name, 'nama': val.salesman_id.name}
                
        elif datas['form']['name'] == 'sales':
            gr = [1,2,3,4,5,6,7,8,10,11] #['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'jabotabek', 'smb', 'jtt', 'sls']
            group = {'g1':'G1', 'g2':'G2', 'g3':'G3', 'g4':'G4', 'g5':'G5', 'g6':'G6', 'jabotabek':'Jabodetabek', 'smb':'Sumatera', 'jtt':'Jawa Timur/Tengah', 'sls':'Sulawesi'}

            for u in obj_group.browse(cr, uid, gr):
                filter1 = [('user_id', 'in', [x.name.id for x in u.users_line]), ('state', 'not in', ('draft', 'cancel')), ('date_order', '>=', val.period_id.date_start), ('date_order', '<=', val.period_id.date_stop)]
                filter2 = [('user_id', 'in', [x.name.id for x in u.users_line]), ('state', 'not in', ('draft', 'cancel')), ('date_order', '>=', val.period_id.fiscalyear_id.date_start), ('date_order', '<=', val.period_id.date_stop)]
                data.append([
                             group[u.name], 
                             sum([x.amount_total for x in obj_order.browse(cr, uid, obj_order.search(cr, uid, filter1))]), 
                             sum([x.amount_total for x in obj_order.browse(cr, uid, obj_order.search(cr, uid, filter2))])])
                    
                
        elif datas['form']['name'] == 'order' :
            gr = [1,2,3,4,5,6] 
            group = {'g1':'G1', 'g2':'G2', 'g3':'G3', 'g4':'G4', 'g5':'G5', 'g6':'G6'}
  
            for u in obj_group.browse(cr, uid, gr):
                filter = [('user_id', 'in', [x.name.id for x in u.users_line]), ('state', 'not in', ('draft', 'cancel')), ('date_order', '>=', val.period_id.date_start), ('date_order', '<=', val.period_id.date_stop)]
                for x in obj_order.browse(cr, uid, obj_order.search(cr, uid, filter)):               
                    data.append([group[u.name], x.partner_id.name, x.amount_total]) 

        elif datas['form']['name'] == 'quo' :
            gr = [7,8,10,11] 
            group = {'jabotabek':'Jabodetabek', 'smb':'Sumatera', 'jtt':'Jawa Timur/Tengah', 'sls':'Sulawesi'}

            for u in obj_group.browse(cr, uid, gr):
                filter = [('user_id', 'in', [x.name.id for x in u.users_line]), ('state', 'not in', ('draft', 'cancel')), ('date_order', '>=', val.period_id.date_start), ('date_order', '<=', val.period_id.date_stop)]
                for x in obj_order.browse(cr, uid, obj_order.search(cr, uid, filter)):               
                    data.append([group[u.name], x.partner_id.name, x.amount_total]) 
                    
        elif datas['form']['name'] == 'prod' :
            idd = obj_order.search(cr, uid, [('state', 'not in', ('draft', 'cancel')), ('partner_id', '=', val.partner_id.id),
                                             ('date_order', '>=', val.period_id.date_start), ('date_order', '<=', val.period_id.date_stop)])
            lid = obj_order_line.search(cr, uid, [('order_id', 'in', idd)])
            hasil = obj_order_line.browse(cr, uid, lid)
            for o in hasil:
                data.append([o.order_id.name, o.order_id.client_order_ref, o.name, o.product_uom_qty, o.product_uom.name, o.price_unit, o.order_id.pricelist_id.currency_id.name])
                    
        datas['csv'] = data
          
        report = 'management.summary.order'
        if datas['form']['name'] == 'sum': 
            report = 'management.summary.activity'
        elif datas['form']['name'] == 'prod': 
            report = 'management.summary.product'
        elif datas['form']['name'] == 'sales': 
            report = 'management.summary.sales'
        elif datas['form']['name'] == 'quo': 
            report = 'management.summary.quo'
                      
        result = {
                'type': 'ir.actions.report.xml',
                'report_name': report,
                'datas': datas,
                'nodestroy': True
        }
          
#         if report == 'management.summary.product':
#             datas['form']['date_start'] = val.period_id.date_start
#             datas['form']['date_stop'] = val.period_id.date_stop
#             result['report_type'] = 'webkit'
#         else:
#             result
                  
        return result 

management_summary()


