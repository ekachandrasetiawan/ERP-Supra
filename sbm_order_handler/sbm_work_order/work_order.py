import time
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.exceptions

class SBM_Adhoc_Order_Request(osv.osv):
	_name = "sbm.adhoc.order.request"
	_columns = {
		'name' : fields.char(string='No',required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'customer_id':fields.many2one('res.partner','Customer', required=True, domain=[('customer','=',True),('is_company','=',True)],readonly=True, states={'draft':[('readonly',False)]},track_visibility='onchange'),
		'attention_id':fields.many2one('res.partner','Attention', required=True, readonly=True, states={'draft':[('readonly',False)]},track_visibility='onchange'),
		'customer_site_id':fields.many2one('res.partner','Site Address', readonly=True, states={'draft':[('readonly',False)]},track_visibility='onchange'),
		'cust_ref_type': fields.selection([('pr', 'Purchase Requisition'),('mail', 'Email Customer')], 'Customer Ref', readonly=True,required=True, states={'draft':[('readonly',False)]}, select=True,track_visibility='onchange'),
		'cust_ref_no' : fields.char(string='Cust Ref No',required=True,track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]}),
		'sale_group_id':fields.many2one('group.sales','Sales Group',required=True,track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]}, domain=[('is_main_group','=',True)]),
		'sales_man_id':fields.many2one('res.users', string='Sales', required=True,track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]}),
		'sale_order_id':fields.many2one('sale.order', string='Sales Order', readonly=True,track_visibility='onchange'),
		'due_date':fields.date('Due Date', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'item_ids':fields.one2many('sbm.adhoc.order.request.output','adhoc_order_request_id', 'Detail Item',readonly=True, states={'draft':[('readonly',False)]},ondelete='cascade'),
		'wo_ids':fields.one2many('sbm.work.order','adhoc_order_request_id', 'Work Order ID',readonly=True,ondelete='cascade'),
		'term_of_payment':fields.many2one('account.payment.term','Term Of Payment', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'notes':fields.text(string='Notes', required=False, readonly=True, states={'draft':[('readonly',False)]}),
		'scope_of_work':fields.text(string='Scope Of Work', required=False, readonly=True, states={'draft':[('readonly',False)]}),
		'term_condition':fields.text(string='Term Condition', required=False, readonly=True, states={'draft':[('readonly',False)]}),
		'state': fields.selection([
			('draft', 'Draft'),
			('submited','Submit'),
			('approved','Approve'),
			('done', 'Done'),
			], 'Status', readonly=True, select=True, track_visibility='onchange'),
	}

	_inherit = ['mail.thread']
	_track = {
		'state':{
			'SBM_Adhoc_Order_Request.adhoc_pack_submited': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'submited',
			'SBM_Adhoc_Order_Request.adhoc_pack_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
			'SBM_Adhoc_Order_Request.adhoc_pack_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
			'SBM_Adhoc_Order_Request.adhoc_pack_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
		},
	}

	_sql_constraints = [
		('name_unique', 'unique (name)', 'The Part Number must be unique !')
	]

	_defaults = {
		'state': 'draft',
		'name':'/'
	}


	def create(self, cr, uid, vals, context={}):
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sbm.adhoc.order.request')

		return super(SBM_Adhoc_Order_Request, self).create(cr, uid, vals, context={})

	def change_customer(self, cr, uid, ids, customer_id, context=None):
		if customer_id:
			p=self.pool.get('res.partner').search(cr,uid,[('parent_id', '=' ,customer_id)])
			partners=self.pool.get('res.partner').browse(cr,uid,p)
			partner =[x.id for x in partners]

			return {'domain': {'attention_id': [('id','in',tuple(partner))],'customer_site_id': [('id','in',tuple(partner))]}}

	def change_sales(self, cr, uid, ids, saleman, context={}):
		res = {}
		if saleman:
			s_man = self.pool.get('res.users').browse(cr, uid, saleman)
			res = {'value':{'sale_group_id':s_man.kelompok_id.parent_id.id}}
		return res

	def adhoc_submit(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'state':'submited'},context=context)
		return res

	def generate_wo_adhoc(self,cr,uid,ids,context={}):
		action = False
		val = self.browse(cr, uid, ids, context={})[0]
		ops = self.browse(cr, uid, ids, context=context)
		obj_wo = self.pool.get('sbm.work.order')

		seq_id = obj_wo.search(cr, uid, [('adhoc_order_request_id','=', val.id)])
		
		if seq_id:
			raise osv.except_osv(_('Warning'),_('Adhoc Order Sudah dibuat Work Order'))

		new_wo_ids = []

		for adhoc in ops:
			prep_wo = {}
			evt_prepare_change = obj_wo.adhoc_order_change(cr, uid, ids, val.id)

			prep_wo = evt_prepare_change['value']
			prep_wo['adhoc_order_request_id']=adhoc.id
			prep_wo['source_type']='adhoc'

			id_wo = obj_wo.create(cr, uid, prep_wo, context=context)


		pool_data=self.pool.get("ir.model.data")
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'sbm_order_handler', "sbm_work_order_form")     
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'sbm.work.order.form'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'sbm.work.order'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = id_wo
		return action


	def adhoc_setdraft(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'state':'draft'},context=context)
		return res

	def adhoc_approve(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'state':'approved'},context=context)
		return res

	def adhoc_validate(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'state':'done'},context=context)
		return res

	def print_adhoc_order_request(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"sbm-adhoc-order-request/print&id="+str(ids[0])+"&uid="+str(uid)
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'   : 'print.out.op',
			'params': {
				'redir'	: urlTo,
				'uid':uid
			},
		}

	def create_adhoc_quotation(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_sale_order = self.pool.get('sale.order')
		obj_sale_order_line = self.pool.get('sale.order.line')
		obj_sale_order_materal_line = self.pool.get('sale.order.material.line')
		obj_sbm_work_order = self.pool.get('sbm.work.order')

		cek_wo=obj_sbm_work_order.search(cr, uid, [('adhoc_order_request_id', '=', ids)])

		location_id=''
		if cek_wo:
			wo_id=obj_sbm_work_order.browse(cr, uid, cek_wo)[0]
			location_id=wo_id.location_id.id
		else:
			raise openerp.exceptions.Warning("Adhoc Order Request Belum Ada Work Order")

		res = {};line = []


		for adhoc_line in val.item_ids:
			material_line =[]

			material_line.append((0,0,{
						'product_id':adhoc_line.item_id.id,
						'desc':adhoc_line.desc,
						'qty':adhoc_line.qty,
						'uom':adhoc_line.uom_id.id,
						'picking_location':location_id
					}))

			for adhoc_line_material in adhoc_line.item_material_ids:
				if adhoc_line_material.item_id.type <> 'consu' or adhoc_line_material.item_id.type <> 'service':
					material_line.append((0,0,{
						'product_id':adhoc_line_material.item_id.id,
						'desc':adhoc_line_material.desc,
						'qty':adhoc_line_material.qty,
						'uom':adhoc_line_material.uom_id.id,
						'picking_location':location_id
					}))
			
			line.append((0,0,{
					'product_id':adhoc_line.item_id.id,
					'name':adhoc_line.desc,
					'product_uom_qty':adhoc_line.qty,
					'product_uom':adhoc_line.uom_id.id,
					'material_lines':material_line
				}))

		# Create Sale Order
		so_id =obj_sale_order.create(cr, uid, {
					'quotation_no':self.pool.get('ir.sequence').get(cr, uid, 'quotation.sequence.type'),
					'partner_id':val.customer_id.id,
					'attention':val.attention_id.id,
					'partner_invoice_id':val.customer_id.id,
					'partner_shipping_id':val.attention_id.id,
					'user_id':val.sales_man_id.id,
					'group_id':val.sale_group_id.id,
					'date':time.strftime('%Y-%m-%d'),
					'due_date':val.due_date,
					'client_order_ref':val.cust_ref_no,
					'from_adhoc':True,
					'pricelist_id':16,
					'scope_work_supra_text':val.scope_of_work,
					'internal_notes':val.term_condition,
					'payment_term':val.term_of_payment.id,
					'term_condition':(4,[val.term_of_payment.id]),
					'order_line':line
					})

		return so_id

	def create_quotation(self, cr, uid, ids, context=None):
		so_id=self.create_adhoc_quotation(cr, uid, ids, context=None)

		if so_id:
			self.write(cr,uid,ids,{'sale_order_id':so_id})

		pool_data=self.pool.get("ir.model.data")
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'sale', "view_order_form")     
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'sale.order.form'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'sale.order'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = so_id
		return action

SBM_Adhoc_Order_Request()


class SBM_Adhoc_Order_Request_Output(osv.osv):
	_name = "sbm.adhoc.order.request.output"
	_columns = {
		'adhoc_order_request_id':fields.many2one('sbm.adhoc.order.request','Adhoc Order Request'),
		'item_id':fields.many2one('product.product',string='Product', required=True),
		'desc':fields.text(string='Description', required=False),
		'qty':fields.float(string='Qty', required=True),
		'uom_id':fields.many2one('product.uom', string='UOM', required=True),
		'item_material_ids':fields.one2many('sbm.adhoc.order.request.output.material', 'adhoc_order_request_output_id',string='Material Lines',ondelete='cascade'),
	}

	def change_item(self, cr, uid, ids, item, context={}):
		product = self.pool.get('product.product').browse(cr, uid, item, context=None)
		return {'value':{'uom_id':product.uom_id.id}}
	_rec_name = 'item_id';

SBM_Adhoc_Order_Request_Output()


class SBM_Adhoc_Order_Request_Output_Material(osv.osv):
	_name = "sbm.adhoc.order.request.output.material"
	_columns = {
		'adhoc_order_request_output_id':fields.many2one('sbm.adhoc.order.request.output','Adhoc Order Request'),
		'item_id':fields.many2one('product.product',string='Product', required=True),
		'desc':fields.text(string='Desc', required=False),
		'qty':fields.float(string='Qty', required=True),
		'uom_id':fields.many2one('product.uom', string='UOM', required=True),
	}


	_rec_name = 'item_id'

	def change_item(self, cr, uid, ids, item, context={}):
		product = self.pool.get('product.product').browse(cr, uid, item, context=None)
		return {'value':{'uom_id':product.uom_id.id}}

SBM_Adhoc_Order_Request_Output_Material()



class SBM_Work_Order(osv.osv):

	def _getRequestNo(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			if item.state == 'draft':
				RequestNo = '/'
			else:
				code_sale =''
				if item.source_type=='internal_request':
					code_sale = 'INTERNAL'
				
				if item.adhoc_order_request_id.id:
					code_sale = item.adhoc_order_request_id.sales_man_id.initial
				elif item.sale_order_id.id:
					code_sale = item.sale_order_id.user_id.initial
				use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
				rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
				vals = self.pool.get('ir.sequence').get(cr, uid, 'perintah.kerja').split('/')
				RequestNo = time.strftime('%y')+item.seq_req_no+'A/SBM-'+item.location_id.code+'-ADM/'+code_sale+'-'+use+'/'+rom[int(vals[2])]+'/'+time.strftime('%y')
			res[item.id] = RequestNo
		return res
	
	def _getWoNo(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			if item.state in ['draft','confirmed']:
				RequestNo = '/'
			else:
				code_sale =''
				if item.source_type=='internal_request':
					code_sale = 'INTERNAL'

				if item.adhoc_order_request_id.id:
					code_sale = item.adhoc_order_request_id.sales_man_id.initial
				elif item.sale_order_id.id:
					code_sale = item.sale_order_id.user_id.initial
				use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
				rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
				vals = self.pool.get('ir.sequence').get(cr, uid, 'perintah.kerja').split('/')
				RequestNo = time.strftime('%y')+item.seq_wo_no+'A/SBM-'+item.location_id.code+'-ADM/'+code_sale+'-'+use+'/'+rom[int(vals[2])]+'/'+time.strftime('%y')
			res[item.id] = RequestNo
		return res

	_name = 'sbm.work.order'
	_columns = {
		'request_no': fields.function(_getRequestNo,method=True,string="Request No",type="char",
			store={
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['work_location'], 20),
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['location_id'], 20),
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['sale_order_id'], 20),
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['adhoc_order_request_id'], 20),
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['state'], 20),
			}),
		'wo_no': fields.function(_getWoNo,method=True,string="SPK No",type="char",
			store={
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['work_location'], 20),
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['location_id'], 20),
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['sale_order_id'], 20),
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['adhoc_order_request_id'], 20),
				'sbm.work.order': (lambda self, cr, uid, ids, c={}: ids, ['state'], 20),
			}),
		'seq_wo_no':fields.char(string='WO Sequence'),
		'seq_req_no':fields.char(string='Request Sequence'),
		'work_location': fields.selection([('workshop', 'Work Shop'),('customersite', 'Customer sITE')], 'Work Location', readonly=True,required=False, states={'draft':[('readonly',False)]}, select=True,track_visibility='onchange'),
		'location_id':fields.many2one('stock.location', string='Resource Location', required=False,track_visibility='onchange',readonly=True, states={'draft':[('readonly',False)]}),
		'customer_id':fields.many2one('res.partner','Customer', domain=[('customer','=',True),('is_company','=',True)],readonly=True, states={'draft':[('readonly',False)]},track_visibility='onchange'),
		'customer_site_id':fields.many2one('res.partner','Customer Work Location',readonly=True, states={'draft':[('readonly',False)]},track_visibility='onchange'),
		'due_date':fields.date(string='Due Date', required=False,readonly=True, states={'draft':[('readonly',False)]}),
		'order_date':fields.date(string='Order Date',readonly=True, states={'draft':[('readonly',False)]}),
		'source_type': fields.selection([('project', 'Project'),('sale_order', 'Sale Order'), ('adhoc','Adhoc'), ('internal_request', 'Internal Request')], 'Source Type', readonly=True,required=False, states={'draft':[('readonly',False)]}, select=True,track_visibility='onchange'),
		'sale_order_id':fields.many2one('sale.order', string='Sale Order', required=False, domain=[('state', 'in', ['progress','manual'])],track_visibility='onchange',readonly=True, states={'draft':[('readonly',False)]}),
		'adhoc_order_request_id':fields.many2one('sbm.adhoc.order.request', required=False, domain=[('state','in',['approved','done'])], string='Adhoc Order Request',readonly=True, states={'draft':[('readonly',False)]}),
		'repeat_ref_id':fields.many2one('sbm.work.order',required=False, string='Repeat Ref',track_visibility='onchange',readonly=True, states={'draft':[('readonly',False)]}),
		'notes':fields.text(string='Notes'),
		'outputs':fields.one2many('sbm.work.order.output', 'work_order_id',string='RAW Materials',ondelete='cascade',readonly=True, states={'draft':[('readonly',False)]}),
		'output_picking_ids':fields.one2many('sbm.work.order.output.picking', 'work_order_id', string='Output Picking',ondelete='cascade',readonly=True, states={'draft':[('readonly',False)]}),
		'state': fields.selection([
			('draft', 'Draft'),
			('confirmed','Confirmed'),
			('approved','Approved'),
			('approved2','Second Approved'),
			('approved3','Validate'),
			('done', 'Done'),
			('cancel', 'Cancel'),
			], 'Status', readonly=True, select=True, track_visibility='onchange'
		),
		'approver':fields.many2one('res.users',string='Approver'),
		'approver2':fields.many2one('res.users',string='Validator'),
		'approver3':fields.many2one('res.users',string='General Approver'),

	}

	_inherit = ['mail.thread']

	_rec_name = 'request_no'

	_defaults = {
		'state': 'draft',
		'request_no':'/',
		'wo_no':'/',
	}

	_track = {
		'state':{
			'SBM_Work_Order.spk_pack_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirmed',
			'SBM_Work_Order.spk_pack_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
			'SBM_Work_Order.spk_pack_approved2': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved2',
			'SBM_Work_Order.spk_pack_approved3': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved3',
			'SBM_Work_Order.spk_pack_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
			'SBM_Work_Order.spk_pack_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
		},
	}

	def set_request_no(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]

		SPK = self.pool.get('sbm.work.order')
		seq_no = self.pool.get('ir.sequence').get(cr, uid, 'sbm.work.order')

		return SPK.write(cr,uid,val.id,{'seq_req_no':seq_no})


	def set_wo_no(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]

		SPK = self.pool.get('sbm.work.order')
		wo_no = self.pool.get('ir.sequence').get(cr, uid, 'sbm.work.order.wo.no')

		return SPK.write(cr,uid,val.id,{'seq_wo_no':wo_no})

	def sale_order_change(self, cr, uid, ids, sale, context=None):
		so_line = self.pool.get('sale.order.line')
		so_material_line = self.pool.get('sale.order.material.line')
		work_order = self.pool.get('sbm.work.order')
		work_order_output = self.pool.get('sbm.work.order.output')
		work_order_material = self.pool.get('sbm.work.order.output.raw.material')

		res = {}; line = []
		if sale:
			order = self.pool.get('sale.order').browse(cr, uid, sale)

			for x in order.order_line:
				if x.material_lines == []:
					raise openerp.exceptions.Warning("SO Material Belum di Definisikan")

				so = so_material_line.search(cr, uid, [('sale_order_line_id', '=', x.id)])
				no = 1;
				for m in so_material_line.browse(cr,uid,so):
					
					nilai=0
					cek_wo=work_order_output.search(cr, uid, [('sale_order_material_line', '=', m.id)])
					for n_material in work_order_output.browse(cr, uid, cek_wo):
						if n_material.work_order_id.state <> 'cancel':
							nilai += n_material.qty
					if m.qty > nilai:
						if m.product_id.type <> 'service':
							if m.product_id.supply_method == 'produce':
								line.append((0,0,{
									'no': no,
									'item_id' : m.product_id.id,
									'desc': m.desc,
									'qty': m.qty-nilai,
									'uom_id': m.uom.id,
									'sale_line_id':x.id,
									'sale_order_material_line': m.id
								}))
						elif m.product_id.type == 'service':
							line.append((0,0,{
								'no': no,
								'item_id' : m.product_id.id,
								'desc': m.desc,
								'qty': m.qty-nilai,
								'uom_id': m.uom.id,
								'sale_line_id':x.id,
								'sale_order_material_line': m.id
							}))
					no +=1
			if line == []:
				raise openerp.exceptions.Warning("Item Sales Order Tidak Ditemukan")

			res['customer_id'] = order.partner_id.id
			res['due_date'] = order.due_date
			res['order_date'] = order.date_order
			res['outputs'] = line
		else:
			res['customer_id'] = False
			res['due_date'] = False
			res['order_date'] = False
			res['outputs'] = False

		return  {'value': res}

	def adhoc_order_change(self, cr, uid, ids, adhoc_id, context=None):
		adhoc_request = self.pool.get('sbm.adhoc.order.request')
		adhoc_request_line = self.pool.get('sbm.adhoc.order.request.output')
		adhoc_request_material = self.pool.get('sbm.adhoc.order.request.output.material')
		
		work_order = self.pool.get('sbm.work.order')
		work_order_output = self.pool.get('sbm.work.order.output')
		work_order_material = self.pool.get('sbm.work.order.output.raw.material')

		res = {}; line = []
		if adhoc_id:
			adhoc = adhoc_request.browse(cr, uid, adhoc_id)
			no_line=1

			for x in adhoc.item_ids:
				adhoc_material = adhoc_request_material.search(cr, uid, [('adhoc_order_request_output_id', '=', x.id)])
				material_line = []
				no_material = 1
				nilai_line = 0

				for m in adhoc_request_material.browse(cr,uid,adhoc_material):
					
					nilai_material = 0	

					ceK_n_material = work_order_material.search(cr, uid, [('adhoc_material_id', '=', m.id)])

					for n_material in work_order_material.browse(cr, uid, ceK_n_material):
						nilai_material += n_material.qty

					if m.qty > nilai_material:
						material_line.append((0,0,{
							'no': no_material,
							'item_id' : m.item_id.id,
							'desc': m.desc,
							'qty': m.qty - nilai_material,
							'uom_id': m.uom_id.id,
							'adhoc_material_id':m.id
						}))

						no_material+=1

				cek_n_line = work_order_output.search(cr, uid, [('adhoc_output_id', '=', x.id)])

				for n_line in work_order_output.browse(cr, uid, cek_n_line):
					nilai_line += n_line.qty


				if x.qty >= nilai_line:
					line.append((0,0,{
						'no': no_line,
						'item_id' : x.item_id.id,
						'desc': x.desc,
						'qty': x.qty - nilai_line,
						'uom_id': x.uom_id.id,
						'adhoc_output_id':x.id,
						'raw_materials': material_line
					}))

					no_line +=1

			if not len(line):
				raise openerp.exceptions.Warning("Item Adhoc Order Tidak Ditemukan")

			res['customer_id'] = adhoc.customer_id.id
			res['outputs'] = line
		else:
			res['customer_id'] = False
			res['outputs'] = False

		return {'value': res}

	def validate(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]

		work_order = self.pool.get('sbm.work.order')
		work_order_line = self.pool.get('sbm.work.order.output')
		work_order_material = self.pool.get('sbm.work.order.output.raw.material')

		adhoc = self.pool.get('sbm.adhoc.order.request')
		adhoc_line = self.pool.get('sbm.adhoc.order.request.output')
		adhoc_material = self.pool.get('sbm.adhoc.order.request.output.material')

		# Jika Adhoc Order Request
		if val.adhoc_order_request_id.id:
			cek_adhoc = work_order.search(cr, uid, [('adhoc_order_request_id', '=', [val.adhoc_order_request_id.id])])

			# validasi Jika Adhoc Sudah Ada
			if cek_adhoc:
				for x in work_order.browse(cr, uid, cek_adhoc):
					if x.state == 'draft' and val.id <> x.id:
						raise openerp.exceptions.Warning("Adhoc Order Request Unique")

			# Cek Line
			for c in val.outputs:
				if c.qty == 0.00:
					raise openerp.exceptions.Warning("Work Order Line Tidak Boleh 0")

				# Cek Material
				for m in c.raw_materials:
					if m.qty == 0.00:
						raise openerp.exceptions.Warning("Work Order Line Material Tidak Boleh 0")

		# Validasi Sales Order
		if val.sale_order_id.id:
			cek_sale_order = work_order.search(cr, uid, [('sale_order_id', '=', [val.sale_order_id.id])])
			if cek_sale_order:
				for x in work_order.browse(cr, uid, cek_sale_order):
					if x.state == 'draft' and val.id <> x.id:
						raise openerp.exceptions.Warning("Sale Order Unique")

			# Cek Line
			for c in val.outputs:
				if c.qty == 0.00:
					raise openerp.exceptions.Warning("Work Order Line Tidak Boleh 0")

				if c.item_id.type <> 'service':
					if c.item_id.supply_method == 'buy':
						if c.item_id.track_production == False:
							if c.item_id.track_incoming == False:
								if c.item_id.track_outgoing==False:
									raise openerp.exceptions.Warning("Item " + c.item_id.default_code + ' No Process')

				# Cek Material
				for m in c.raw_materials:
					if m.qty == 0.00:
						raise openerp.exceptions.Warning("Work Order Line Material Tidak Boleh 0")
		return True

	def set_confirm(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'confirmed'})
		return res

	def set_approved(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'approved'})
		return res

	def set_approved2(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'approved2'})
		return res

	def set_approved3(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'approved3'})
		return res

	def set_to_done(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'done'})
		return res

	def set_to_draft(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'draft'})
		return res

	def set_to_cancel(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'cancel'})
		return res

	def work_order_confirm(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		validasi = self.validate(cr, uid, ids, context=None)
		if validasi == True:
			if val.seq_req_no == False:
				self.set_request_no(cr, uid, ids, context=None)

			self.set_confirm(cr, uid, ids, context=None)

		return True

	def work_order_check(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		if val.seq_wo_no == False:
			self.set_wo_no(cr, uid, ids, context=None)

		self.set_approved(cr, uid, ids, context=None)

		res = self.write(cr, uid, ids, {'approver': uid})
		return res

	def work_order_set_draft(self, cr, uid, ids, context=None):
		res = self.set_to_draft(cr, uid, ids, context=None)
		return res

	def work_order_validate(self, cr, uid, ids, context=None):
		self.set_approved2(cr, uid, ids, context=None)
		res = self.write(cr, uid, ids, {'approver2': uid})
		return res

	def work_order_process(self, cr, uid, ids, context=None):
		self.create_picking(cr, uid, ids, context=None)
		self.set_approved3(cr, uid, ids, context=None)
		res = self.write(cr, uid, ids, {'approver3': uid})
		return True

	def work_order_finish(self, cr, uid, ids, context=None):
		picking = self.transfer_output_picking(cr, uid, ids, context=None)
		if picking == True:
			self.set_to_done(cr, uid, ids, context=None)
		return True

	def work_order_cancel(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		stock_picking = self.pool.get('stock.picking')
		raw_material = self.pool.get('sbm.work.order.output.picking')

		data = raw_material.search(cr, uid, [('work_order_id', '=', ids)])

		if data:
			picking_id = raw_material.browse(cr, uid, data)[0].picking_id.id
			
			# Cancel Picking
			stock_picking.action_cancel(cr, uid, [picking_id])

		self.set_to_cancel(cr, uid, ids, context=None)

		return True

	def cancel_output_picking(self, cr, uid, ids, context=None):

		return True

	def cek_product_batch(self, cr, uid, ids, context=None):
		obj_product = self.pool.get('product.product')
		obj_batch=self.pool.get('stock.production.lot')

		cek = obj_product.browse(cr, uid, ids)
		if cek.track_production == True or cek.track_incoming == True or cek.track_outgoing == True:

			lot_name_ws = cek.default_code+'-WS'
			get_lot = obj_batch.search(cr, uid, [('product_id','=',cek.id), ('name','=',lot_name_ws)])
			if not get_lot:
				# set new serial
				prodlot_obj_id = obj_batch.create(
					cr, uid, 
					{
						'name': lot_name_ws, 
						'product_id': cek.id,
						'desc': 'Manufacture Lot',
					}, 
					context=context
				)
			else:
				prodlot_obj_id = get_lot[0]
		
		return prodlot_obj_id




	def create_picking(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]

		stock_picking = self.pool.get('stock.picking')
		stock_location = self.pool.get('stock.location')
		stock_move = self.pool.get('stock.move')
		work_order = self.pool.get('sbm.work.order')
		work_order_line = self.pool.get('sbm.work.order.output')

		picking_type = 'internal'
		seq_obj_name =  'stock.picking.' + picking_type

		set_loc = stock_location.search(cr, uid, [('name','=', 'MANUFACTURE')])

		loc_id = stock_location.browse(cr, uid, ids, set_loc)[0].id
		origin = False
		if val.adhoc_order_request_id.id:
			origin = 'Adhoc Order Request '+val.adhoc_order_request_id.name
		elif val.sale_order_id.id:
			origin = val.sale_order_id.name

		# Create Stock Picking 
		picking = stock_picking.create(cr, uid, {
					# 'name':self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
					'name':'INT/WO/'+val.wo_no[:7],
					'origin':origin,
					'partner_id':val.customer_id.id,
					'move_type':'direct',
					'invoice_state':'none',
					'auto_picking':False,
					'type':picking_type,
					'sale_id':val.sale_order_id.id,
					'state':'draft'
					})

		# Create Stock Move
		for line in val.outputs:
			# Cek Product Batch 
			if line.item_id.track_production == True or line.item_id.track_incoming == True or line.item_id.track_outgoing == True:
				batch_id = self.cek_product_batch(cr, uid, line.item_id.id, context=None)
			else:
				batch_id = False

			move_id = stock_move.create(cr,uid,{
				'name' : line.desc,
				'origin':origin,
				'product_uos_qty':line.qty,
				'product_uom':line.uom_id.id,
				'product_qty':line.qty,
				'product_uos':line.uom_id.id,
				'partner_id':val.customer_id.id,
				'product_id':line.item_id.id,
				'auto_validate':False,
				'location_id' :46,
				'company_id':1,
				'prodlot_id':batch_id,
				'picking_id': picking,
				'state':'draft',
				'location_dest_id' :val.location_id.id
				},context=context)

			# Create Output Picking
			self.create_output_picking(cr, uid, ids, picking, move_id, line.id, context=None)


			for x in line.raw_materials:
				# Cek Product Batch 
				if x.item_id.track_production == True or x.item_id.track_incoming == True or x.item_id.track_outgoing == True:
					batch_id_detail = self.cek_product_batch(cr, uid, x.item_id.id, context=None)
				else:
					batch_id_detail = False

				move_detail_id = stock_move.create(cr,uid,{
					'name' : x.desc,
					'origin':origin,
					'product_uos_qty':x.qty,
					'product_uom':x.uom_id.id,
					'product_qty':x.qty,
					'product_uos':x.uom_id.id,
					'partner_id':val.customer_id.id,
					'product_id':x.item_id.id,
					'auto_validate':False,
					'location_id' :val.location_id.id,
					'company_id':1,
					'prodlot_id':batch_id_detail,
					'picking_id': picking,
					'state':'draft',
					'location_dest_id' :46
					},context=context)

		stock_picking.action_assign(cr, uid, [picking])

		return True

	def create_output_picking(self, cr, uid, ids, picking, move, output_id, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		output_picking = self.pool.get('sbm.work.order.output.picking')
		res = output_picking.create(cr, uid, {
				'work_order_output_id': output_id,
				'picking_id':picking,
				'move_id':move,
				'work_order_id':val.id
				})

		return res


	def transfer_output_picking(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		stock_picking = self.pool.get('stock.picking')
		raw_material = self.pool.get('sbm.work.order.output.picking')

		data = raw_material.search(cr, uid, [('work_order_id', '=', ids)])

		for x in raw_material.browse(cr, uid, data):
			if x.picking_id.state <> 'cancel':
				# Update Done Picking & Move
				stock_picking.action_move(cr, uid, [x.picking_id.id])
		return True


	def print_work_order(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"sbm-work-order/print&id="+str(ids[0])+"&uid="+str(uid)
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.out.op',
			'params': {
				'redir'	: urlTo,
				'uid':uid
			},
		}

SBM_Work_Order()


class SBM_Work_Order_Output(osv.osv):

	def _getWOType(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for data in self.browse(cr,uid,ids,context):
			res[data.id] = data.work_order_id.source_type

		return res

	def _getType(self,cr,uid,context={}):
		im_r = self.pool.get('sbm.work.order')._getType(cr,uid,context)
		return im_r

	_name = 'sbm.work.order.output'
	_columns = {
		'no':fields.float(string='No', required=False),
		'work_order_id':fields.many2one('sbm.work.order','Work Order No', required=False, ondelete="CASCADE", onupdate="CASCADE"),
		'item_id':fields.many2one('product.product', string='Product', domain=[('active', '=', True), ('sale_ok','=',True)], required=True),
		'desc':fields.text(string='Description', required=False),
		'qty':fields.float(required=True, string='Qty'),
		'uom_id':fields.many2one('product.uom', required=True, string='UOM'),
		'raw_materials':fields.one2many('sbm.work.order.output.raw.material', 'work_order_output_id', string='Raw Materials',ondelete='cascade',onupdate="CASCADE"),
		'attachment_ids': fields.many2many('ir.attachment', 'work_order_rel','work_order_id', 'attachment_id', 'Attachments'),
		'output_picking_ids':fields.one2many('sbm.work.order.output.picking', 'work_order_output_id', string='Output Picking',ondelete='cascade',onupdate="CASCADE"),
		'adhoc_output_id':fields.many2one('sbm.adhoc.order.request.output',string='Adhoc Output', required=False),
		'sale_line_id': fields.many2one('sale.order.line', "Sale Item", required=False),
		'sale_order_material_line':fields.many2one('sale.order.material.line',string='Line Materials', required=False),
		'wo_type':fields.function(_getWOType,store=False,string="WO Type",type="char"),
	}

	_rec_name = 'item_id'

	def default_get(self, cr, uid, fields, context=None):
		if context is None:
			context = {}
		
		res = super(SBM_Work_Order_Output, self).default_get(cr, uid, fields, context=context)
		res.update({'wo_type': context.get('type')})
		return res

	def change_item(self, cr, uid, ids, item, context={}):
		product = self.pool.get('product.product').browse(cr, uid, item, context=None)
		return {'value':{'uom_id':product.uom_id.id}}

	def check_item_material(self, cr, uid, ids, item, context={}):

		return {'value':{'sale_line_material_id':False}}

SBM_Work_Order_Output()	



class SBM_Work_Order_Output_Picking(osv.osv):
	_name = 'sbm.work.order.output.picking'
	_columns = {
		'work_order_output_id':fields.many2one('sbm.work.order.output', required=True, string='Output'),
		'work_order_id':fields.many2one('sbm.work.order', string='Work Order'),
		'picking_id':fields.many2one('stock.picking', string='Picking'),
		'move_id':fields.many2one('stock.move', string='Move'),
	}


SBM_Work_Order_Output_Picking()	



class SBM_Work_Order_Output_Raw_Material(osv.osv):
	_name = 'sbm.work.order.output.raw.material'
	_columns = {
		'work_order_output_id':fields.many2one('sbm.work.order.output', required=True, string='Output'),
		'item_id':fields.many2one('product.product',required=True, string='Product'),
		'desc':fields.text(string='Description'),
		'qty':fields.float(string='Qty', required=True),
		'uom_id':fields.many2one('product.uom', required=True, string='UOM'),
		'customer_material':fields.boolean(string='Customer Materials'),
		'adhoc_material_id':fields.many2one('sbm.adhoc.order.request.output.material', string='Adhoc Materials', required=False),
	}


	def change_item(self, cr, uid, ids, item, context={}):
		product = self.pool.get('product.product').browse(cr, uid, item, context=None)
		return {'value':{'uom_id':product.uom_id.id}}


SBM_Work_Order_Output_Raw_Material()


class SBM_Work_Order_Line_Files(osv.osv):
	_name = 'sbm.work.order.line.files'
	_columns = {
		'name':fields.char('Name', required=True),
		'file':fields.binary('File  Doc'),
		'work_order_output_id':fields.many2one('sbm.work.order.output',string='Output'),
	}

SBM_Work_Order_Line_Files()


class Sale_order(osv.osv):	
	_inherit ='sale.order'

	_columns ={
		'from_adhoc':fields.boolean('From Adhoc'),
		'wo_ids':fields.one2many('sbm.work.order','sale_order_id',string='Work Order'),
		'adhoc_ids':fields.one2many('sbm.adhoc.order.request','sale_order_id', string='Adhoc Order Request'),
	}

Sale_order()


class order_preparation(osv.osv):
	_inherit = "order.preparation"
	_description = "Order Packaging"
	_columns = {
		'sale_id': fields.many2one('sale.order', 'Sale Order', required=False, readonly=True, domain=[
			'|','|',('quotation_state','=','win'),('state','in',['progress','manual']) , '&', ('from_adhoc','=',True),'&',('quotation_state','=','confirmed'),('state','=','draft')
		], states={'draft': [('readonly', False)]}),
	}


order_preparation()