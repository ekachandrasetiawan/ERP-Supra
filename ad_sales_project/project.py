import time
import calendar
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _




class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'default_code' : fields.char('Part Number', size=64, select=True, required=True),
    }
    
    _sql_constraints = [
        ('default_code_unique', 'unique (default_code)', 'The Part Number must be unique !'),

        ('name_template_unique', 'unique (name_template)', 'The Part Name must be unique !')
    ]
    
        
product_product()


class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'kelompok_id': fields.many2one('group.sales', 'Groups Sales'),
    }
    
res_users()

class groups_sales(osv.osv):
    _name = "group.sales"
    _columns = {
        'users_line': fields.one2many('group.sales.line', 'kelompok_id', 'List User'),
        'name': fields.selection(
                [
                    ('g1', 'G1'), 
                        
                    ('g2', 'G2'), 
                    ('g3', 'G3'), 
                    ('g4', 'G4'), 
                    ('g5', 'G5'), 
                    ('g6', 'G6'),
                    ('g2jtt', 'G2JTT'),
                    ('g1sub', 'G1 Subordinat'), 
                    ('g2sub', 'G2 Subordinat'), 
                    ('g3sub', 'G3 Subordinat'), 
                    ('g4sub', 'G4 Subordinat'), 
                    ('g5sub', 'G5 Subordinat'), 
                    ('g6sub', 'G6 Subordinat'),
                    ('jabotabek', 'Jabodetabek'), 
                    ('smb', 'Sumatera'), 
                    ('jtt', 'Jawa Timur/Tengah'), 
                    ('sls', 'Sulawesi'), 
                    ('direksi', 'Direksi'),
                    ('jabotabeksub', 'Jabodetabek Subordinat'), 
                    ('smbsub', 'Sumatera Subordinat'), 
                    ('jttsub', 'Jawa Timur/Tengah Subordinat'), 
                    ('slssub', 'Sulawesi Subordinat'), 
                    ('direksi', 'Direksi'),
                    ('sh','sh'),
                    ('g2joko','G2 Joko'),
                    ('g2paulus','G2 Paulus'),
                    ('g3ricky', 'G3 Ricky'),
                    ('g4sukmawan','G4 Sukmawan'),
                    ('g4hendriktan','G4 Hendrik Tan'),
                    ('g5tasahadi','G5 Tasahadi'),
                    ('g5tomisetiawan','G5 Tomi Setiawan'),
                    ('g6sucinto','G6 Sucinto'),
                    ('jabdartono','Jabodetabek Dartono'),
                    ('jabzulkifli','Jabodetabek Zulkifli'),
                    ('jabheri','Jabodetabek Heri Susanto'),
                    ('jabjoel','Jabodetabek Joel A Lubis'),
                    ('sumdarwin','Sumatera Darwin Zaenal'),
                    ('sumjalvedra','Sumatera Jalvedra'),
                    ('sumsofa','Sumatera Sofa'),
                    ('sumrosita','Sumatera Rosita'),
		            ('sumbahrin','Sumatra Bahrin'),
                    ('summarlin','Sumatra Marliansyah'),
                    ('sumarie','Sumatra Arie Agung Laksono'),
                    ('jttfarchan','Jawa Timur/Tengah Farchan'),
                    ('jttlukman','Jawa Timur/Tengah Lukman'),
                    ('jttagung','Jawa Timur/Tengah Agung'),
                    ('jtttatok','Jawa Timur/Tengah Tatok'),
                    ('jttjudy','Jawa Timur/Tengah Judy'),
                    ('jttali','Jawa Timur/Tengah Ali Wahyudi'),
                    ('sulkristanto','Sulawesi Kristanto'),
                    ('suldedison','Sulawesi Dedison'),
                    ('suljansen','Sulawesi Jansen'),
                ], 
            'REG/PSM', 
            required=True
        ),
    }
    
    
#     _sql_constraints = [
#         ('name_uniq', 'unique (name)', 'The group must be unique !')
#     ]

groups_sales()

class groups_sales_line(osv.osv):
    _name = "group.sales.line"
    _columns = {
        'name': fields.many2one('res.users', 'User Login', required=True),
        'kelompok_id': fields.many2one('group.sales', 'Groups Sales'),
    }
    
    
#     _sql_constraints = [
#         ('name_uniq', 'unique (name)', 'The username must be unique !')
#     ]

groups_sales_line()



# ['|',('user_id','=',[x.name.id for x in user.kelompok_id.users_line]),('user_id','=',False)]
        
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
                'street': fields.char('Street', size=128, required=True),
                'phone': fields.char('Phone', size=64, required=True),
                'week_line' : fields.one2many('log.status.customer', 'customer_id', 'Weekly Status', readonly=True),
    }

res_partner()


class log_status_customer(osv.osv):
    _name = "log.status.customer"        
    _columns = {
        'begin' : fields.date('Begin'),
        'end' : fields.date('End'),
        'name': fields.text('Status'),
        'week_id': fields.many2one('week.status.line', 'Week Status'),
        'salesman_id': fields.many2one('res.users', 'PIC'),
        'customer_id': fields.many2one('res.partner', 'Status Update', required=True, ondelete='cascade'),
    }
    

log_status_customer()


class scope_work_supra(osv.osv):
    _name = "scope.work.supra"        
    _columns = {
        'name': fields.char('Scope of Work', required=True, size=256),
    }
    
scope_work_supra()

class scope_work_customer(osv.osv):
    _name = "scope.work.customer"        
    _columns = {
        'name': fields.char('Scope of Work', required=True, size=256),
    }
    
scope_work_customer()


class term_condition(osv.osv):
    _name = "term.condition"        
    _columns = {
        'name': fields.char('Term and Condition', required=True, size=256),
    }
    
term_condition()

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
            'week': fields.selection([(1, 'W1'), (2, 'W2'), (3, 'W3'), (4, 'W4'), (5, 'W5')], 'Week', readonly=True, states={'draft': [('readonly', False)]}),
            'activity_line' : fields.one2many('log.activity', 'quotation_id', 'Weekly Status', readonly=True),
            'preparation_line' : fields.one2many('order.preparation', 'sale_id', 'Order Packaging', readonly=True),
            'worktype': fields.selection([('regional', 'Regional'), ('product', 'Product'), ('project', 'Project')], 'Work Type', readonly=True, states={'draft': [('readonly', False)]}),
            'due_date' : fields.date('Due Date', select=True, readonly=True, states={'draft': [('readonly', False)]}),
            'delivery_date' : fields.date('Delivery Date', select=True, readonly=True, states={'draft': [('readonly', False)]}),
        
            'attention': fields.many2one('res.partner', 'Attention', domain="[('parent_id', '=', partner_id)]"),
            'scope_work_supra': fields.many2many('scope.work.supra', 'scope_work_supra_rel', 'scope_supra_id', 'order_id', 'Scope of Work Supra'),
            'scope_work_customer': fields.many2many('scope.work.customer', 'scope_work_customer_rel', 'scope_customer_id', 'order_id', 'Scope of Work Customer'),
            'term_condition': fields.many2many('term.condition', 'term_condition_rel','term_id', 'order_id', 'Term and Condition') 
            
#             'sow1': fields.boolean('Supply of Rubber Lining material (rubber sheet, adhesive, primer and solvent)'),
#             'sow2': fields.boolean('Supply sufficient working tools and other consumable'),
#             'sow3': fields.boolean('Supply of workers (Supervisor and technician)'),
#             'sow4': fields.boolean('Dismantle tank lorry from vehicle'),
#             'sow5': fields.boolean('Chipping existing rubber lining and painting outside tank'),
#             'sow6': fields.boolean('Rubber lining and Painting outside application'),
#             'sow7': fields.boolean('Fabrication and Install half pipe into partition of tank'),
#             'sow8': fields.boolean('Surface preparation with standard SA 2,5 inside and outside tank'),
#             'sow9': fields.boolean('Repair welding and grinding if any un-standard on substrate '),
#             'sow10': fields.boolean('Set up tank in to new vehicle'),
#             'sow11': fields.boolean('Provide new bolt and nut'),
#             'sow12': fields.boolean('Provide rubber pad between chassis and tank'),
#             'sow13': fields.boolean('Perform test (pinhole test, thickness and hardness)'),
#             'sow14': fields.boolean('Perform final documents'),
#             
#             'sowA': fields.boolean('Transportation NaCLO Tank Lorry to and from SBM Workshop - Tangerang'),
#             'sowB': fields.boolean('Third party inspection'),
#             'sowC': fields.boolean('Witness final inspection'),
#             
#             'kondisi1': fields.boolean('The above price does not include 10 % VAT'),
#             'kondisi2': fields.boolean('Payment : As Previously following ASC Term of Payment'),
#             'kondisi3': fields.boolean('Validity : 2(two) months from the date of quotation'),
                        
    }
    
    def onchange_dateorder(self, cr, uid, ids, tgl):
        if tgl:
            week = 0
            tahun = int(tgl.split('-')[0])
            bulan = int(tgl.split('-')[1])
            hari = str(int(tgl.split('-')[2]))
            month = calendar.month(tahun, bulan).split('\n')[2:-1]
            for i in month:
                if hari in i.split():
                    week = month.index(i)+1
		    if week > 5 :
			week =5
            return {'value': {'week': week}}
        return True


    def action_wait(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
            noprod = self.test_no_product(cr, uid, o, context)
            
            if not o.client_order_ref:
                raise osv.except_osv(('Perhatian !'), ("Customer Reference wajib diisi !"))
       
            if (o.order_policy == 'manual') or noprod:
                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            else:
                self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
        return True

    
sale_order()


class log_activity(osv.osv):
    _name = "log.activity"        
    _columns = {
        'name': fields.text('Result'),
        'date' : fields.date('Date'),
        'lunch' : fields.selection([(1, 'Before Lunch'), (2, 'After Lunch')], 'Time'),
        'day' : fields.selection([(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), 
                                  (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], 'Day'),
        'activity_id': fields.many2one('sales.activity', 'Activity'),
        'salesman_id': fields.many2one('res.users', 'PIC'),
        'quotation_id': fields.many2one('sale.order', 'Sale Order', required=True, ondelete='cascade'),
    }
    

log_activity()


class week_status(osv.osv):
    _name = "week.status"
    _columns = {
        'name': fields.char('Refference', required=True, size=64),
        'type': fields.selection(
                [
                    ('g1', 'G1'), 
                    ('g2', 'G2'), 
                    ('g3', 'G3'), 
                    ('g4', 'G4'), 
                    ('g5', 'G5'), 
                    ('g6', 'G6'),
                    ('g2jtt', 'G2JTT'),
                    ('g1sub', 'G1 Subordinat'), 
                    ('g2sub', 'G2 Subordinat'), 
                    ('g3sub', 'G3 Subordinat'), 
                    ('g4sub', 'G4 Subordinat'), 
                    ('g5sub', 'G5 Subordinat'), 
                    ('g6sub', 'G6 Subordinat'),
                    ('jabotabek', 'Jabodetabek'), 
                    ('smb', 'Sumatera'), 
                    ('jtt', 'Jawa Timur/Tengah'), 
                    ('sls', 'Sulawesi'), 
                    ('direksi', 'Direksi'),
                    ('jabotabeksub', 'Jabodetabek Subordinat'), 
                    ('smbsub', 'Sumatera Subordinat'), 
                    ('jttsub', 'Jawa Timur/Tengah Subordinat'), 
                    ('slssub', 'Sulawesi Subordinat'), 
                    ('direksi', 'Direksi'),
                    ('sh','sh'),
                    ('g2joko','G2 Joko'),
                    ('g2paulus','G2 Paulus'),
                    ('g3ricky','G3 Ricky'),
                    ('g4sukmawan','G4 Sukmawan'),
                    ('g4hendriktan','G4 Hendrik Tan'),
                    ('g5tasahadi','G5 Tasahadi'),
                    ('g5tomisetiawan','G5 Tomi Setiawan'),
                    ('g6sucinto','G6 Sucinto'),
                    ('jabdartono','Jabodetabek Dartono'),
                    ('jabzulkifli','Jabodetabek Zulkifli'),
                    ('jabheri','Jabodetabek Heri Susanto'),
                    ('jabjoel','Jabodetabek Joel A Lubis'),
                    ('sumdarwin','Sumatera Darwin Zaenal'),
                    ('sumjalvedra','Sumatera Jalvedra'),
                    ('sumsofa','Sumatera Sofa'),
                    ('sumrosita','Sumatera Rosita'),
                    ('sumbahrin','Sumatera Bahrin'),
                    ('summarlin','Sumatra Marliansyah'),
                    ('sumarie','Sumatra Arie Agung Laksono'),
                    ('jttfarchan','Jawa Timur/Tengah Farchan'),
                    ('jttlukman','Jawa Timur/Tengah Lukman'),
                    ('jttagung','Jawa Timur/Tengah Agung'),
                    ('jtttatok','Jawa Timur/Tengah Tatok'),
                    ('jttjudy','Jawa Timur/Tengah Judy'),
                    ('jttali','Jawa Timur/Tengah Ali Wahyudi'),
                    ('sulkristanto','Sulawesi Kristanto'),
                    ('suldedison','Sulawesi Dedison'),
                    ('suljansen','Sulawesi Jansen'),
                ], 'REG/PSM', required=True),
        'user_id': fields.many2one('res.users', 'PIC', required=True),
        'state': fields.selection([('draft', 'Draft')], 'State', readonly=True),
        'status_line': fields.one2many('week.status.line', 'status_id', 'Week Status Line', domain=[('state', 'in', ('nego','quo'))]),
    }
     
    _defaults = {
        'name': '/', 
        'state': 'draft'
    }
    
    _order = 'name desc'
     
    def create(self, cr, uid, vals, context=None):    
        ada = self.pool.get('week.status').search(cr, uid, [('user_id', '=', uid)])
        if ada:
            nama = self.pool.get('week.status').browse(cr, uid, ada)[0]
            raise osv.except_osv(('Perhatian !'), ("Anda telah membuat week status dengan nama %s , silahkan untuk mengupdatenya !" % nama.name))
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'week.status')
        return super(week_status, self).create(cr, uid, vals, context=context)
    
    def report_mingguan(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        
        data = []
        title = 'status.mingguan.excel'                
        nilai = self.read(cr, uid, ids)[0]
        
        if context is None:
            context = {}


        for x in val.status_line:
            data.append([
                            x.name.name, 
                            str(x.order_id.name),
                            str(x.amount),
                            str(x.currency_id.name),
                            str(x.project),
                            str(x.product_group),
                            str(x.state),
                            str([(a.begin +' s/d '+ a.end +': '+ a.name) for a in x.update_line])
            ])  
            
        datas = {'ids': [nilai['id']]}
        datas['model'] = 'week.status'
        datas['form'] = nilai
        datas['csv'] = data
                 
        return {
            'type': 'ir.actions.report.xml',
            'report_name': title,
            'nodestroy': True,
            'datas': datas,
        }
            
week_status()


class week_status_line(osv.osv):
    _name = "week.status.line"
    _columns = {
        'name': fields.many2one('res.partner', 'Customer', required=True),
        'amount': fields.float('Amount', digits=(12,2)),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'quotation' : fields.date('Date', readonly=True),
        'project': fields.char('Project/Prospect', required=True, size=64),
        'salesman_id': fields.related('status_id', 'user_id', type='many2one', relation='res.users', string='Salesperson', readonly=True),
        'status': fields.text('Last Status', required=True),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'product_group': fields.selection([('pekerjaanbarang', 'Pekerjaan dan Barang'), ('pekerjaan', 'Pekerjaan'),('abb','ABB'), ('rema', 'Rema TipTop'), ('almex', 'Almex Vulcanizer '), ('crew', 'SuperScrew by Minet'), 
                                           ('uhmw', 'UHMW'), ('etec', 'Etec - Ceremic Lining'), ('ring', 'Ringfeder'), ('ohji', 'Ohji Rubber'), 
                                           ('karet', 'R/L Karet Lokal'), ('loctite', 'Loctite'), ('mbx', 'MBX Bristle Blaster'), ('3lt', '3LT'), 
                                           ('rtt', 'RTT Lining'), ('amp', 'AMP - Roady'), ('yifan', 'YIFAN - Crusher'),
                                           ('tehno', 'Tehnoroll / Ecoroll'), ('pulley', 'Tehnopulley'), ('Rulmeca', 'rulmeca'), ('lorb', 'Lorbrand'), ('voith', 'Voith'), ('trell', 'Trelleborg Marine System : Mining & Pelindo'), 
                                           ('Martin Product', 'martin'), ('tru', 'TruTrac'), ('mc', 'Mc Lanahan'), ('ball', 'Grinding Ball'), ('goodyear', 'GoodYear'), ('rocktrans', 'Rocktrans'),
                                           ('hkm', 'HKM : Magnet separator / Metal Detector'), ('ecp', 'ECP : Safety Device'), ('mti', 'Stacker Reclaimer - MTI'), ('borg', 'Trelleborg Marine System : Oil & Gas'), 
                                           ('belt', 'Belt Conveyor'), ('roler', 'Roller & Pulley')], 'Product Group'),
        'update_line': fields.one2many('status.subline', 'line_id', 'Update Line', readonly=True),
        'state': fields.selection([('nego', 'Presentation'), ('win', 'Win'), ('quo', 'Quotation'), ('budget', 'budgetary'), ('lost', 'Lost'), ('post', 'Postpone')], 'State', readonly=True),
        'status_id': fields.many2one('week.status', 'Week Status', required=True, ondelete='cascade'),
    }
    
    _defaults = {'currency_id': 13, 'state': 'nego', 'status': '-'}
    

    def play_order(self, cr, uid, ids, context=None):
        make = self.browse(cr, uid, ids, context=context)[0]
        self.write(cr, uid, ids, {'state': 'nego'})
        if make.order_id:
            self.write(cr, uid, ids, {'state': 'quo'})
        return True

    def cancel_order(self, cr, uid, ids, context=None):
        make = self.browse(cr, uid, ids, context=context)[0]
        self.write(cr, uid, ids, {'state': 'nego', 'order_id': False, 'quotation': False})
        return True

    def post_order(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'post'})
        return True
    
    def win_order(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'win'})
        return True

    def lost_order(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids, context=context)[0]
        if not val.status:
            raise osv.except_osv(('Attention !'), ("Please fill the reasons of lost !"))
        self.write(cr, uid, ids, {'state': 'lost'})
        return True
        
    def create_order(self, cr, uid, ids, context=None):
        make = self.browse(cr, uid, ids, context=context)[0]
        product_obj = self.pool.get('product.product')
        sale_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')
        
        if not make.amount:
            raise osv.except_osv(('Attention !'), ("Please fill amount field !"))
        
        product = product_obj.browse(cr, uid, 2)
        
        cust = make.name
        pricelist = cust.property_product_pricelist.id 
        partner_addr = self.pool.get('res.partner').address_get(cr, uid, [cust.id], ['default', 'invoice', 'delivery', 'contact'])
        new_id = sale_obj.create(cr, uid, {
            'partner_id': cust.id,
            'pricelist_id': pricelist,
            'partner_invoice_id': partner_addr['invoice'],
            'partner_shipping_id': partner_addr['delivery'],
            'date_order': time.strftime('%Y-%m-%d'),
        }, context=context)
        
        sale_line_obj.create(cr, uid, {
                        'order_id': new_id,
                        'name': '[' + str(product.code) + '] ' + str(product.name),
                        'product_id': 2,
                        'product_qty': 1,
                        'product_uom': 1,
                        'price_unit': make.amount
        })
                    
        self.write(cr, uid, ids, {'state': 'quo', 'order_id': new_id, 'quotation': time.strftime('%Y-%m-%d')})
        return True


      
    def write(self, cr, uid, ids, vals, context=None):
        val = self.browse(cr, uid, ids)[0]
        if vals.has_key('status'):
            week_obj = self.pool.get('status.subline')
            status_obj = self.pool.get('log.status.customer')
            
            week = int(date.today().strftime("%W")) + 1
            year = int(date.today().strftime("%Y"))
            d = date(year,1,1)
            if(d.weekday()>3):
                d = d+timedelta(7-d.weekday())
            else:
                d = d - timedelta(d.weekday())
            dlt = timedelta(days = (week-1)*7)
            begin = d + dlt
            end = d + dlt + timedelta(days=6)
            sid = week_obj.search(cr, uid, [('line_id', '=', val.id), 
                                            ('begin', '=', begin.strftime('%Y-%m-%d')),
                                            ('end', '=', end.strftime('%Y-%m-%d'))])
            cid = status_obj.search(cr, uid, [('week_id', '=', val.id), 
                                            ('begin', '=', begin.strftime('%Y-%m-%d')),
                                            ('end', '=', end.strftime('%Y-%m-%d'))])
            if sid:
                week_obj.write(cr, uid, sid, {'name': vals['status']})
                status_obj.write(cr, uid, cid, {'name': vals['status']})
            else:
                week_obj.create(cr, uid, ({
                                           'line_id': val.id,
                                           'end': end.strftime('%Y-%m-%d'),
                                           'begin': begin.strftime('%Y-%m-%d'),
                                           'name': vals['status']
                                           }))
                status_obj.create(cr, uid, ({
                                           'week_id': val.id,
                                           'customer_id': val.name.id,
                                           'end': end.strftime('%Y-%m-%d'),
                                           'begin': begin.strftime('%Y-%m-%d'),
                                           'name': vals['status'],
                                           'salesman_id': val.salesman_id.id
                                           }))
        return super(week_status_line, self).write(cr, uid, ids, vals, context=context)                                    

    
week_status_line()


class status_subline(osv.osv):
    _name = "status.subline"        
    _columns = {
        'begin' : fields.date('Begin', readonly=True, states={'draft': [('readonly', False)]}),
        'end' : fields.date('End', readonly=True, states={'draft': [('readonly', False)]}),
        'name': fields.text('Status', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft')], 'State', readonly=True),
        'line_id': fields.many2one('week.status.line', 'Status Update', required=True, ondelete='cascade'),
    }
    
    _defaults = {
        'name': 'Evaluasi',
        'state': 'draft'
    }

status_subline()


class sales_activity(osv.osv):
    _name = "sales.activity"
    _columns = {
        'begin' : fields.date('Begin', readonly=True),
        'end' : fields.date('End', readonly=True),        
        'name': fields.char('Refference', required=True, size=64, readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'PIC', readonly=True),

        'beforeplansenin': fields.one2many('before.plan.senin', 'activity_id', 'Plan', readonly=True),
        'afterplansenin': fields.one2many('after.plan.senin', 'activity_id', 'Plan', readonly=True),
        'beforeactualsenin': fields.one2many('before.actual.senin', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        'afteractualsenin': fields.one2many('after.actual.senin', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        
        'beforeplanselasa': fields.one2many('before.plan.selasa', 'activity_id', 'Plan', readonly=True),
        'afterplanselasa': fields.one2many('after.plan.selasa', 'activity_id', 'Plan', readonly=True),
        'beforeactualselasa': fields.one2many('before.actual.selasa', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        'afteractualselasa': fields.one2many('after.actual.selasa', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        
        'beforeplanrabu': fields.one2many('before.plan.rabu', 'activity_id', 'Plan', readonly=True),
        'afterplanrabu': fields.one2many('after.plan.rabu', 'activity_id', 'Plan', readonly=True),
        'beforeactualrabu': fields.one2many('before.actual.rabu', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        'afteractualrabu': fields.one2many('after.actual.rabu', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        
        'beforeplankamis': fields.one2many('before.plan.kamis', 'activity_id', 'Plan', readonly=True),
        'afterplankamis': fields.one2many('after.plan.kamis', 'activity_id', 'Plan', readonly=True),
        'beforeactualkamis': fields.one2many('before.actual.kamis', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        'afteractualkamis': fields.one2many('after.actual.kamis', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        
        'beforeplanjumat': fields.one2many('before.plan.jumat', 'activity_id', 'Plan', readonly=True),
        'afterplanjumat': fields.one2many('after.plan.jumat', 'activity_id', 'Plan', readonly=True),
        'beforeactualjumat': fields.one2many('before.actual.jumat', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        'afteractualjumat': fields.one2many('after.actual.jumat', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        
        'beforeplansabtu': fields.one2many('before.plan.sabtu', 'activity_id', 'Plan', readonly=True),
        'afterplansabtu': fields.one2many('after.plan.sabtu', 'activity_id', 'Plan', readonly=True),
        'beforeactualsabtu': fields.one2many('before.actual.sabtu', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        'afteractualsabtu': fields.one2many('after.actual.sabtu', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        
        'beforeplanahad': fields.one2many('before.plan.ahad', 'activity_id', 'Plan', readonly=True),
        'afterplanahad': fields.one2many('after.plan.ahad', 'activity_id', 'Plan', readonly=True),
        'beforeactualahad': fields.one2many('before.actual.ahad', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        'afteractualahad': fields.one2many('after.actual.ahad', 'activity_id', 'Actual', states={'done': [('readonly', True)]}),
        
        'state': fields.selection([('draft', 'Draft'), ('done', 'Confirmed')], 'State', readonly=True),
        
    }
     
    _defaults = {
        'name': '/',
        'state': 'draft',
    }
    
    _order = 'name desc'
     
    def create(self, cr, uid, vals, context=None):    
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sales.activity')

        return super(sales_activity, self).create(cr, uid, vals, context=context)


    def activity_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def activity_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        return True
        
sales_activity()


class reset_status(osv.osv):
    _name = "reset.status"

    def action_reset(self, cr, uid, ids, context=None):
        idd = self.pool.get('week.status.line').search(cr, uid, [])
        self.pool.get('week.status.line').write(cr, uid, idd, {'status': ''})
        
        tanggal = datetime.now() - timedelta(days=14)
        
        sid = self.pool.get('sale.order').search(cr, uid, [('date_order', '<=', tanggal.strftime('%Y-%m-%d')), ('state', 'in', ('draft', 'sent'))])
        sad = self.pool.get('sale.order').browse(cr, uid, sid)
        
        for x in sad: 
            self.pool.get('remainder.salesman').create(cr, uid, {
                'name': x.date_order,
                'amount': x.amount_total,
                'order_id': x.id,
                'partner_id': x.partner_id.id,
                'salesman_id': x.user_id.id,
                'currency_id': x.currency_id.id
            })
        
        return True
         
reset_status()

class remainder_salesman(osv.osv):
    _name = "remainder.salesman"        
    _columns = {
        'name' : fields.date('Quotation Date', readonly=True, select=True),
        'currency_id': fields.many2one('res.currency', 'Currency', readonly=True, select=True),
        'amount': fields.float('Amount', digits=(12,2), readonly=True, select=True),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True, select=True),
        'salesman_id': fields.many2one('res.users', 'PIC', readonly=True, select=True),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, select=True),
    }
    

remainder_salesman()

class wizard_activity(osv.osv):
    _name = "wizard.activity"
    _columns = {
        'begin' : fields.date('Begin', required=True),
        'end' : fields.date('End', required=True),        
        'name': fields.many2one('res.users', 'PIC', required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', domain="[('user_id','=',name)]"),

        'beforeplansenin': fields.one2many('wizard.before.plan.senin', 'wizard_id', 'Plan'),
        'afterplansenin': fields.one2many('wizard.after.plan.senin', 'wizard_id', 'Plan'),
#         'beforeactualsenin': fields.one2many('wizard.before.actual.senin', 'wizard_id', 'Actual'),
#         'afteractualsenin': fields.one2many('wizard.after.actual.senin', 'wizard_id', 'Actual'),
        
        'beforeplanselasa': fields.one2many('wizard.before.plan.selasa', 'wizard_id', 'Plan'),
        'afterplanselasa': fields.one2many('wizard.after.plan.selasa', 'wizard_id', 'Plan'),
#         'beforeactualselasa': fields.one2many('wizard.before.actual.selasa', 'wizard_id', 'Actual'),
#         'afteractualselasa': fields.one2many('wizard.after.actual.selasa', 'wizard_id', 'Actual'),
        
        'beforeplanrabu': fields.one2many('wizard.before.plan.rabu', 'wizard_id', 'Plan'),
        'afterplanrabu': fields.one2many('wizard.after.plan.rabu', 'wizard_id', 'Plan'),
#         'beforeactualrabu': fields.one2many('wizard.before.actual.rabu', 'wizard_id', 'Actual'),
#         'afteractualrabu': fields.one2many('wizard.after.actual.rabu', 'wizard_id', 'Actual'),
        
        'beforeplankamis': fields.one2many('wizard.before.plan.kamis', 'wizard_id', 'Plan'),
        'afterplankamis': fields.one2many('wizard.after.plan.kamis', 'wizard_id', 'Plan'),
#         'beforeactualkamis': fields.one2many('wizard.before.actual.kamis', 'wizard_id', 'Actual'),
#         'afteractualkamis': fields.one2many('wizard.after.actual.kamis', 'wizard_id', 'Actual'),
        
        'beforeplanjumat': fields.one2many('wizard.before.plan.jumat', 'wizard_id', 'Plan'),
        'afterplanjumat': fields.one2many('wizard.after.plan.jumat', 'wizard_id', 'Plan'),
#         'beforeactualjumat': fields.one2many('wizard.before.actual.jumat', 'wizard_id', 'Actual'),
#         'afteractualjumat': fields.one2many('wizard.after.actual.jumat', 'wizard_id', 'Actual'),
        
#         'beforeplansabtu': fields.one2many('wizard.before.plan.sabtu', 'wizard_id', 'Plan'),
#         'afterplansabtu': fields.one2many('wizard.after.plan.sabtu', 'wizard_id', 'Plan'),
#         'beforeactualsabtu': fields.one2many('wizard.before.actual.jumat', 'wizard_id', 'Actual'),
#         'afteractualsabtu': fields.one2many('wizard.after.actual.jumat', 'wizard_id', 'Actual'),
        
#         'beforeplanahad': fields.one2many('wizard.before.plan.ahad', 'wizard_id', 'Plan'),
#         'afterplanahad': fields.one2many('wizard.after.plan.ahad', 'wizard_id', 'Plan'),
#         'beforeactualahad': fields.one2many('wizard.before.actual.jumat', 'wizard_id', 'Actual'),
#         'afteractualahad': fields.one2many('wizard.after.actual.jumat', 'wizard_id', 'Actual'),
        
#         'type': fields.selection([('plan', 'Plan')], 'Type'),
    }
     

    _defaults = {
        'name': lambda self, cr, uid, context: uid,
    }
     

    def onchange_tanggal(self, cr, uid, ids, begin, end):
        if begin:
            
            actid = self.pool.get('sales.activity').search(cr, uid, [('begin', '=', begin), ('user_id', '=', uid)])           
            if actid:
                actda = self.pool.get('sales.activity').browse(cr, uid, actid[0])
                return {'warning': {"title": _("Perhatian"), "message": _("Sales Activity pada tanggal %s telah dibuat yaitu %s") % (begin, actda.name)}, 'value': {'begin': False, 'end': False}}
            
            hariini = date.today().strftime("%Y-%m-%d")
            if begin < hariini:
                return {'warning': {"title": _("Perhatian"), "message": _("Tanggal Begin harus setelah hari ini !")}, 'value': {'begin': False, 'end': False}}
                
            hari = datetime.strptime(begin, "%Y-%m-%d").strftime('%A')
            if hari != 'Monday':
                return {'warning': {"title": _("Perhatian"), "message": _("Tanggal Begin harus hari senin !")}, 'value': {'begin': False, 'end': False}}
                
            ahad = datetime.strptime(begin, "%Y-%m-%d") + timedelta(days=6)
            return {'value': {'end': ahad.strftime('%Y-%m-%d')}}
        return True

    def create_activity(self, cr, uid, ids, context=None):    
        val = self.browse(cr, uid, ids, context=context)[0]
        actid = self.pool.get('sales.activity').create(cr, uid, {'name': val.name, 'begin': val.begin, 'end': val.end, 'user_id': val.name.id})
        if val.beforeplansenin:
            self.update_activity(cr, uid, ids, actid, val.beforeplansenin, 'before.plan.senin')
            self.update_activity(cr, uid, ids, actid, val.beforeplansenin, 'before.actual.senin', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Monday must have plan !"))
        if val.afterplansenin:
            self.update_activity(cr, uid, ids, actid, val.afterplansenin, 'after.plan.senin')
            self.update_activity(cr, uid, ids, actid, val.afterplansenin, 'after.actual.senin', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Monday must have plan !"))
        if val.beforeplanselasa:
            self.update_activity(cr, uid, ids, actid, val.beforeplanselasa, 'before.plan.selasa')
            self.update_activity(cr, uid, ids, actid, val.beforeplanselasa, 'before.actual.selasa', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Tuesday must have plan !"))
        if val.afterplanselasa:
            self.update_activity(cr, uid, ids, actid, val.afterplanselasa, 'after.plan.selasa')
            self.update_activity(cr, uid, ids, actid, val.afterplanselasa, 'after.actual.selasa', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Tuesday must have plan !"))
        if val.beforeplanrabu:
            self.update_activity(cr, uid, ids, actid, val.beforeplanrabu, 'before.plan.rabu')
            self.update_activity(cr, uid, ids, actid, val.beforeplanrabu, 'before.actual.rabu', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Wednesday must have plan !"))
        if val.afterplanrabu:
            self.update_activity(cr, uid, ids, actid, val.afterplanrabu, 'after.plan.rabu')
            self.update_activity(cr, uid, ids, actid, val.afterplanrabu, 'after.actual.rabu', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Wednesday must have plan !"))
        if val.beforeplankamis:
            self.update_activity(cr, uid, ids, actid, val.beforeplankamis, 'before.plan.kamis')
            self.update_activity(cr, uid, ids, actid, val.beforeplankamis, 'before.actual.kamis', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Thursday must have plan !"))
        if val.afterplankamis:
            self.update_activity(cr, uid, ids, actid, val.afterplankamis, 'after.plan.kamis')
            self.update_activity(cr, uid, ids, actid, val.afterplankamis, 'after.actual.kamis', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Thursday must have plan !"))
        if val.beforeplanjumat:
            self.update_activity(cr, uid, ids, actid, val.beforeplanjumat, 'before.plan.jumat')
            self.update_activity(cr, uid, ids, actid, val.beforeplanjumat, 'before.actual.jumat', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Friday must have plan !"))
        if val.afterplanjumat:
            self.update_activity(cr, uid, ids, actid, val.afterplanjumat, 'after.plan.jumat')
            self.update_activity(cr, uid, ids, actid, val.afterplanjumat, 'after.actual.jumat', 'actual')
        else:
            raise osv.except_osv(('Attention !'), ("Friday must have plan !"))
            
            
    def update_activity(self, cr, uid, ids, actid, data, tabel, jenis=''):
        for x in data:
            if jenis:
                self.pool.get(tabel).create(cr, uid, {'activity_id': actid, 'name': ' ', 'jenis': 'plan', 'partner_id': x.partner_id.id, 'location': x.location})
            else:
                self.pool.get(tabel).create(cr, uid, {'activity_id': actid, 'name': x.name, 'partner_id': x.partner_id.id, 'location': x.location})
                                                  
wizard_activity()

### SENIN ###

class before_plan_senin(osv.osv):
    _name = "before.plan.senin"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
before_plan_senin()

class after_plan_senin(osv.osv):
    _name = "after.plan.senin"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
after_plan_senin()


class before_actual_senin(osv.osv):
    _name = "before.actual.senin"
    _idx = 1
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(before_actual_senin, self).unlink(cr, uid, ids, context=context)

    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    
    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
        
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 1; lunch = 1
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d")
        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}
        
        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', dat),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : dat,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True
    
before_actual_senin()

class after_actual_senin(osv.osv):
    _name = "after.actual.senin"
    _idx = 1
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(after_actual_senin, self).unlink(cr, uid, ids, context=context)


    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
    

    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 1; lunch = 2
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d")
        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}
        
        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', dat),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : dat,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True

    
after_actual_senin()
        
### SELASA ###

class before_plan_selasa(osv.osv):
    _name = "before.plan.selasa"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
before_plan_selasa()

class after_plan_selasa(osv.osv):
    _name = "after.plan.selasa"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
after_plan_selasa()


class before_actual_selasa(osv.osv):
    _name = "before.actual.selasa"
    _idx = 2
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(before_actual_selasa, self).unlink(cr, uid, ids, context=context)


    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
    
    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 2; lunch = 1
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=1)
        tgl.strftime('%Y-%m-%d')

        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}
        
        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True

    
before_actual_selasa()

class after_actual_selasa(osv.osv):
    _name = "after.actual.selasa"
    _idx=2
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(after_actual_selasa, self).unlink(cr, uid, ids, context=context)


    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
    

    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 2; lunch = 2
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=1)
        tgl.strftime('%Y-%m-%d')

        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}
        
        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True

    
after_actual_selasa()

### RABU ###

class before_plan_rabu(osv.osv):
    _name = "before.plan.rabu"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
before_plan_rabu()

class after_plan_rabu(osv.osv):
    _name = "after.plan.rabu"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
after_plan_rabu()


class before_actual_rabu(osv.osv):
    _name = "before.actual.rabu"
    _idx=3
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(before_actual_rabu, self).unlink(cr, uid, ids, context=context)

    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
    

    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 3; lunch = 1
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=2)
        tgl.strftime('%Y-%m-%d')

        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}
        
        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True


before_actual_rabu()

class after_actual_rabu(osv.osv):
    _name = "after.actual.rabu"
    _idx=3
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(after_actual_rabu, self).unlink(cr, uid, ids, context=context)


    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
    
    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 3; lunch = 2
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=2)
        tgl.strftime('%Y-%m-%d')

        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}
        
        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True

    
after_actual_rabu()

### KAMIS ###

class before_plan_kamis(osv.osv):
    _name = "before.plan.kamis"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
before_plan_kamis()

class after_plan_kamis(osv.osv):
    _name = "after.plan.kamis"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
after_plan_kamis()


class before_actual_kamis(osv.osv):
    _name = "before.actual.kamis"
    _idx=4
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(before_actual_kamis, self).unlink(cr, uid, ids, context=context)


    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
    
    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 4; lunch = 1
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=3)
        tgl.strftime('%Y-%m-%d')

        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}

        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True
    
before_actual_kamis()

class after_actual_kamis(osv.osv):
    _name = "after.actual.kamis"
    _idx=4
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(after_actual_kamis, self).unlink(cr, uid, ids, context=context)


    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
    
    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 4; lunch = 2
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=3)
        tgl.strftime('%Y-%m-%d')

        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}

        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True
    
after_actual_kamis()

### JUMAT ###

class before_plan_jumat(osv.osv):
    _name = "before.plan.jumat"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
before_plan_jumat()

class after_plan_jumat(osv.osv):
    _name = "after.plan.jumat"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
after_plan_jumat()


class before_actual_jumat(osv.osv):
    _name = "before.actual.jumat"
    _idx=5
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(before_actual_jumat, self).unlink(cr, uid, ids, context=context)

    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
    

    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 5; lunch = 1
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=4)
        tgl.strftime('%Y-%m-%d')

        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}

        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True
    
before_actual_jumat()

class after_actual_jumat(osv.osv):
    _name = "after.actual.jumat"
    _idx=5
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'batal': fields.boolean('Cancel ?', help="Check jika actual tidak sesuai plan"),
        'jenis': fields.selection([('plan', 'Plan'), ('actual', 'Actual')], 'Jenis'),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        move = self.browse(cr, uid, ids, context=context)
        move = move[0]
        if move.jenis == 'plan':
            raise osv.except_osv(_('Perhatian'),_('Data Aktual tidak bisa dihapus !'))
        return super(after_actual_jumat, self).unlink(cr, uid, ids, context=context)


    def onchange_cancel(self, cr, uid, ids, batal):
        if batal:
            return {'value': {'name': False}}
        return True
    
    def onchange_rencana(self, cr, uid, ids):
        val = self.browse(cr, uid, ids)
        if val:
            if val[0].jenis == 'plan':
                    return {'warning': {"title": _("Perhatian !"), "message": _("Customer tidak bisa diganti !")}, 
                        'value': {'partner_id': val[0].partner_id.id}}
        return True
    
    
    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 5; lunch = 2
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=4)
        tgl.strftime('%Y-%m-%d')

        if date.today() > date(int(tgl.strftime('%Y')), int(tgl.strftime('%m')), int(tgl.strftime('%d'))):
            return {'warning': {"title": _("Attention !"), "message": _("Time has expired !")}, 
                    'value': {'name': False, 'partner_id': False, 'order_id': False, 'location': False}}

        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True
    
after_actual_jumat()

### SABTU ###

class before_plan_sabtu(osv.osv):
    _name = "before.plan.sabtu"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
before_plan_sabtu()

class after_plan_sabtu(osv.osv):
    _name = "after.plan.sabtu"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
after_plan_sabtu()


class before_actual_sabtu(osv.osv):
    _name = "before.actual.sabtu"
    _idx=6
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }


    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 6; lunch = 1
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=5)
        tgl.strftime('%Y-%m-%d')

        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True
    
before_actual_sabtu()

class after_actual_sabtu(osv.osv):
    _name = "after.actual.sabtu"
    _idx=6
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }


    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 6; lunch = 2
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=5)
        tgl.strftime('%Y-%m-%d')

        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True
    
after_actual_sabtu()


### AHAD ###

class before_plan_ahad(osv.osv):
    _name = "before.plan.ahad"

    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
before_plan_ahad()

class after_plan_ahad(osv.osv):
    _name = "after.plan.ahad"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
after_plan_ahad()


class before_actual_ahad(osv.osv):
    _name = "before.actual.ahad"
    _idx=0
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }


    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 7; lunch = 1
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=6)
        tgl.strftime('%Y-%m-%d')

        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True

before_actual_ahad()

class after_actual_ahad(osv.osv):
    _name = "after.actual.ahad"
    _idx=0
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation'),
        'location': fields.char('Location', size=64, required=True),
        'activity_id': fields.many2one('sales.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }

    def onchange_activity(self, cr, uid, ids, order_id, dat, result, activity):
        day = 7; lunch = 2
        log_obj = self.pool.get('log.activity')
        
        tgl = datetime.strptime(dat, "%Y-%m-%d") + timedelta(days=6)
        tgl.strftime('%Y-%m-%d')

        if order_id:
            cid = log_obj.search(cr, uid, [('quotation_id', '=', order_id), 
                                            ('date', '=', tgl),
                                            ('lunch', '=', lunch)])
            if cid:
                log_obj.write(cr, uid, cid, {'name': result})
            else:
                log_obj.create(cr, uid, ({
                                        'name': result,
                                        'date' : tgl,
                                        'lunch' : lunch,
                                        'day' : day,
                                        'activity_id': activity,
                                        'salesman_id': uid,
                                        'quotation_id': order_id}))
        return True
    
after_actual_ahad()



########################################################
########################################################

### WIZARD SENIN ###

class wizard_before_plan_senin(osv.osv):
    _name = "wizard.before.plan.senin"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_plan_senin()

class wizard_after_plan_senin(osv.osv):
    _name = "wizard.after.plan.senin"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_plan_senin()


class wizard_before_actual_senin(osv.osv):
    _name = "wizard.before.actual.senin"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_actual_senin()

class wizard_after_actual_senin(osv.osv):
    _name = "wizard.after.actual.senin"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_actual_senin()

### WIZARD SELASA ###

class wizard_before_plan_selasa(osv.osv):
    _name = "wizard.before.plan.selasa"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_plan_selasa()

class wizard_after_plan_selasa(osv.osv):
    _name = "wizard.after.plan.selasa"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_plan_selasa()


class wizard_before_actual_selasa(osv.osv):
    _name = "wizard.before.actual.selasa"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_actual_selasa()

class wizard_after_actual_selasa(osv.osv):
    _name = "wizard.after.actual.selasa"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_actual_selasa()

### WIZARD RABU ###

class wizard_before_plan_rabu(osv.osv):
    _name = "wizard.before.plan.rabu"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_plan_rabu()

class wizard_after_plan_rabu(osv.osv):
    _name = "wizard.after.plan.rabu"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_plan_rabu()


class wizard_before_actual_rabu(osv.osv):
    _name = "wizard.before.actual.rabu"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_actual_rabu()

class wizard_after_actual_rabu(osv.osv):
    _name = "wizard.after.actual.rabu"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_actual_rabu()

### WIZARD KAMIS ###

class wizard_before_plan_kamis(osv.osv):
    _name = "wizard.before.plan.kamis"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_plan_kamis()

class wizard_after_plan_kamis(osv.osv):
    _name = "wizard.after.plan.kamis"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_plan_kamis()


class wizard_before_actual_kamis(osv.osv):
    _name = "wizard.before.actual.kamis"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_actual_kamis()

class wizard_after_actual_kamis(osv.osv):
    _name = "wizard.after.actual.kamis"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_actual_kamis()

### WIZARD JUMAT ###

class wizard_before_plan_jumat(osv.osv):
    _name = "wizard.before.plan.jumat"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_plan_jumat()

class wizard_after_plan_jumat(osv.osv):
    _name = "wizard.after.plan.jumat"
    _columns = {
        'name': fields.text('Objectives', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_plan_jumat()


class wizard_before_actual_jumat(osv.osv):
    _name = "wizard.before.actual.jumat"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_before_actual_jumat()

class wizard_after_actual_jumat(osv.osv):
    _name = "wizard.after.actual.jumat"
    _columns = {
        'name': fields.text('Results', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
        'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
        'location': fields.char('Location', size=64, required=True),
        'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
    }
    
wizard_after_actual_jumat()


### WIZARD SABTU ###

# class wizard_before_plan_sabtu(osv.osv):
#     _name = "wizard.before.plan.sabtu"
#     _columns = {
#         'name': fields.text('Objectives', required=True),
#         'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
#         'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
#         'location': fields.char('Location', size=64, required=True),
#         'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
#     }
#     
# wizard_before_plan_sabtu()
# 
# class wizard_after_plan_sabtu(osv.osv):
#     _name = "wizard.after.plan.sabtu"
#     _columns = {
#         'name': fields.text('Objectives', required=True),
#         'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
#         'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
#         'location': fields.char('Location', size=64, required=True),
#         'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
#     }
#     
# wizard_after_plan_sabtu()


# class wizard_before_actual_sabtu(osv.osv):
#     _name = "wizard.before.actual.sabtu"
#     _columns = {
#         'name': fields.text('Results', required=True),
#         'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
#         'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
#         'location': fields.char('Location', size=64, required=True),
#         'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
#     }
#     
# wizard_before_actual_sabtu()
# 
# class wizard_after_actual_sabtu(osv.osv):
#     _name = "wizard.after.actual.sabtu"
#     _columns = {
#         'name': fields.text('Results', required=True),
#         'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
#         'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
#         'location': fields.char('Location', size=64, required=True),
#         'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
#     }
#     
# wizard_after_actual_sabtu()



### WIZARD AHAD ###

# class wizard_before_plan_ahad(osv.osv):
#     _name = "wizard.before.plan.ahad"
#     _columns = {
#         'name': fields.text('Objectives', required=True),
#         'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
#         'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
#         'location': fields.char('Location', size=64, required=True),
#         'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
#     }
#     
# wizard_before_plan_ahad()
# 
# class wizard_after_plan_ahad(osv.osv):
#     _name = "wizard.after.plan.ahad"
#     _columns = {
#         'name': fields.text('Objectives', required=True),
#         'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
#         'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
#         'location': fields.char('Location', size=64, required=True),
#         'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
#     }
#     
# wizard_after_plan_ahad()


# class wizard_before_actual_ahad(osv.osv):
#     _name = "wizard.before.actual.ahad"
#     _columns = {
#         'name': fields.text('Results', required=True),
#         'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
#         'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
#         'location': fields.char('Location', size=64, required=True),
#         'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
#     }
#     
# wizard_before_actual_ahad()
# 
# class wizard_after_actual_ahad(osv.osv):
#     _name = "wizard.after.actual.ahad"
#     _columns = {
#         'name': fields.text('Results', required=True),
#         'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=',True)]),
#         'order_id': fields.many2one('sale.order', 'Quotation', readonly=True),
#         'location': fields.char('Location', size=64, required=True),
#         'wizard_id': fields.many2one('wizard.activity', 'Sales Activity', required=True, ondelete='cascade'),
#     }
#     
# wizard_after_actual_ahad()


# class mrp_production(osv.osv):
#     _inherit = "mrp.production"
#     _columns = {
#                 'biaya_lines': fields.one2many('biaya.workshop', 'biaya_id', 'Cost Lines'),
#     }
# 
# mrp_production()
# 
# 
# class biaya_workshop(osv.osv):
#     _name = "biaya.workshop"
#     _columns = {
#         'name': fields.char('Task', size=64),
#         'price_unit': fields.float('Cost', digits=(12,2)),
#         'biaya_id': fields.many2one('mrp.production', 'Workshop', required=True, ondelete='cascade'),
#     }
#          
# biaya_workshop()


#             if sid:
#                 did = self.pool.get('status.subline').browse(cr, uid, sid[0])
#                 begin = datetime.strptime(did.begin, "%Y-%m-%d") + timedelta(days=7) 
#                 end = datetime.strptime(did.end, "%Y-%m-%d") + timedelta(days=7)
#                 return {'value': {'begin': begin.strftime('%Y-%m-%d'), 'end': end.strftime('%Y-%m-%d')}}
#             else:
#                 week = int(date.today().strftime("%W")) + 1
#                 year = int(date.today().strftime("%Y"))
#                 d = date(year,1,1)
#                 if(d.weekday()>3):
#                     d = d+timedelta(7-d.weekday())
#                 else:
#                     d = d - timedelta(d.weekday())
#                 dlt = timedelta(days = (week-1)*7)
#                 begin = d + dlt
#                 end = d + dlt + timedelta(days=6)
#                 return {'value': {'begin': begin.strftime('%Y-%m-%d'), 'end': end.strftime('%Y-%m-%d')}}  



#         if val.type == "actual":
#             if val.beforeactualsenin:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.beforeactualsenin, 'before.actual.senin')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Monday must have actual !"))
#             if val.afteractualsenin:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.afteractualsenin, 'after.actual.senin')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Monday must have actual !"))
#             if val.beforeactualselasa:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.beforeactualselasa, 'before.actual.selasa')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Tuesday must have actual !"))
#             if val.afteractualselasa:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.afteractualselasa, 'after.actual.selasa')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Tuesday must have actual !"))
#             if val.beforeactualrabu:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.beforeactualrabu, 'before.actual.rabu')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Wednesday must have actual !"))
#             if val.afteractualrabu:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.afteractualrabu, 'after.actual.rabu')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Wednesday must have actual !"))
#             if val.beforeactualkamis:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.beforeactualkamis, 'before.actual.kamis')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Thursday must have actual !"))
#             if val.afteractualkamis:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.afteractualkamis, 'after.actual.kamis')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Thursday must have actual !"))
#             if val.beforeactualjumat:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.beforeactualjumat, 'before.actual.jumat')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Friday must have actual !"))
#             if val.afteractualjumat:
#                 self.update_activity(cr, uid, ids, val.activity_id.id, val.afteractualjumat, 'after.actual.jumat')
#             else:
#                 raise osv.except_osv(('Attention !'), ("Friday must have actual !"))

