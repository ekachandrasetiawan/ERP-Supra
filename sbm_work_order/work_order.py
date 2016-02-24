import time
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _


class SBM_Adhoc_Order_Request(osv.osv):
	_name = "sbm.adhoc.order.request"
	_columns = {
		'name' : fields.char(string='No',required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'customer_id':fields.many2one('res.partner','Customer', required=True, domain=[('customer','=',True),('is_company','=',True)],readonly=True, states={'draft':[('readonly',False)]}),
		'attention_id':fields.many2one('res.partner','Attention', readonly=True, states={'draft':[('readonly',False)]}),
		'customer_site_id':fields.many2one('res.partner','Customer Site', readonly=True, states={'draft':[('readonly',False)]}),
		'cust_ref_type': fields.selection([('pr', 'Purchase Requisition'),('mail', 'Email Customer')], 'Customer Ref', readonly=True,required=True, states={'draft':[('readonly',False)]}, select=True,track_visibility='onchange'),
		'cust_ref_no' : fields.char(string='Cust Ref No',required=True,track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]}),
		'sale_group_id':fields.many2one('group.sales','Sales Group',required=True,track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]}),
		'sales_man_id':fields.many2one('res.users', string='Sales', required=True,track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]}),
		'due_date':fields.date('Due Date', readonly=True, states={'draft':[('readonly',False)]}),
		'item_ids':fields.one2many('sbm.adhoc.order.request.output','adhoc_order_request_id', 'Detail Item',readonly=True, states={'draft':[('readonly',False)]}),
		'wo_ids':fields.one2many('sbm.work.order','adhoc_order_request_id', 'Work Order ID',readonly=True,track_visibility='onchange', states={'draft':[('readonly',False)]}),
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

	def adhoc_submit(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'state':'submited'},context=context)
		return res

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
			'tag'	: 'print.adhoc.order.request',
			'params': {
				'redir'	: urlTo,
				'uid':uid
			},
		}

SBM_Adhoc_Order_Request()


class SBM_Adhoc_Order_Request_Output(osv.osv):
	_name = "sbm.adhoc.order.request.output"
	_columns = {
		'adhoc_order_request_id':fields.many2one('sbm.adhoc.order.request','Adhoc Order Request'),
		'item_id':fields.many2one('product.product',string='Product', required=True),
		'desc':fields.text(string='Description', required=False),
		'qty':fields.float(string='Qty', required=True),
		'uom_id':fields.many2one('product.uom', string='UOM', required=True),
		'item_material_ids':fields.one2many('sbm.adhoc.order.request.output.material', 'adhoc_order_request_output_id',string='Material Lines')
	}

	def change_item(self, cr, uid, ids, item, context={}):
		product = self.pool.get('product.product').browse(cr, uid, item, context=None)
		return {'value':{'desc': '[' + product.default_code + ']' + 	product.name, 'uom_id':product.uom_id.id}}


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

SBM_Adhoc_Order_Request_Output_Material()



class SBM_Work_Order(osv.osv):
	_name = 'sbm.work.order'
	_columns = {
		'request_no':fields.char(string='WO Request No', required=True),
		'wo_no':fields.char(string='Order No'),
		'work_location': fields.selection([('workshop', 'Work Shop'),('customersite', 'Customer SITE')], 'Work Location', readonly=True,required=True, states={'draft':[('readonly',False)]}, select=True,track_visibility='onchange'),
		'location_id':fields.many2one('stock.location', string='Internal Handler Location', required=True),
		'customer_id':fields.many2one('res.partner','Customer', domain=[('customer','=',True),('is_company','=',True)],readonly=True, states={'draft':[('readonly',False)]}),
		'customer_site_id':fields.many2one('res.partner','Customer Work Location',readonly=True, states={'draft':[('readonly',False)]}),
		'due_date':fields.date(string='Due Date', required=True),
		'order_date':fields.date(string='Order Date'),
		'source_type': fields.selection([('project', 'Project'),('sale_order', 'Sale Order'), ('adhoc','Adhoc'), ('internal_request', 'Internal Request')], 'Source Type', readonly=True,required=True, states={'draft':[('readonly',False)]}, select=True,track_visibility='onchange'),
		'sale_order_id':fields.many2one('sale.order', string='Sale Order', required=False),
		'adhoc_order_request_id':fields.many2one('sbm.adhoc.order.request', required=False, domain=[('state','in',['approved','done'])], string='Adhoc Order Request'),
		'repeat_ref_id':fields.many2one('sbm.work.order',required=False, string='Repeat Ref'),
		'notes':fields.text(string='Notes'),
		'outputs':fields.one2many('sbm.work.order.output', 'work_order_id',string='RAW Materials'),
		'output_picking_ids':fields.one2many('sbm.work.order.output.picking', 'work_order_id', string='Output Picking'),
		'state': fields.selection([
			('draft', 'Draft'),
			('confirmed','Confirmed'),
			('approved','Approved'),
			('approved2','Second Approved'),
			('approved3','Validate'),
			('done', 'Done'),
			], 'Status', readonly=True, select=True, track_visibility='onchange'
		),
		'approver':fields.many2one('res.users',string='Approver'),
		'approver2':fields.many2one('res.users',string='Validator'),
		'approver3':fields.many2one('res.users',string='General Approver'),

	}

	_inherit = ['mail.thread']

	_rec_name = 'request_no'

	_sql_constraints = [
		('wi_no_unique', 'unique (wo_no)', 'The Work Order Number must be unique !')
	]

	_defaults = {
		'state': 'draft',
		'request_no':'/',
	}
	
SBM_Work_Order()


class SBM_Work_Order_Output(osv.osv):
	_name = 'sbm.work.order.output'
	_columns = {
		'no':fields.float(string='No', required=False),
		'work_order_id':fields.many2one('sbm.work.order','Work Order No', required=True),
		'item_id':fields.many2one('product.product', string='Product', domain=[('active', '=', True), ('sale_ok','=',True)], required=True),
		'desc':fields.text(string='Description', required=False),
		'qty':fields.float(required=True, string='Qty'),
		'uom_id':fields.many2one('product.uom', required=True, string='UOM'),
		'raw_materials':fields.one2many('sbm.work.order.output.raw.material', 'work_order_output_id', string='Raw Materials'),
		'raw_files':fields.one2many('sbm.work.order.line.files','work_order_output_id', string='Raw Files'),
		'output_picking_ids':fields.one2many('sbm.work.order.output.picking', 'work_order_output_id', string='Output Picking'),
		'adhoc_output_ids':fields.many2one('sbm.adhoc.order.request.output',string='Adhoc Output', required=False),

	}

	_rec_name = 'item_id'

SBM_Work_Order_Output()	



class SBM_Work_Order_Output_Picking(osv.osv):
	_name = 'sbm.work.order.output.picking'
	_columns = {
		'work_order_output_id':fields.many2one('sbm.work.order.output', required=True, string='Output'),
		'work_order_id':fields.related('sbm.work.order','work_order_id', string='Work Order'),
		'picking_id':fields.many2one('stock.picking', string='Picking'),
		'raw_material_moves':fields.one2many('sbm.work.order.output.move', 'work_order_output_picking_id',string='Materials'),
	}


SBM_Work_Order_Output_Picking()	



class SBM_Work_Order_Output_Move(osv.osv):
	_name = 'sbm.work.order.output.move'
	_columns = {
		'work_order_output_picking_id':fields.many2one('sbm.work.order.output.picking', required=True, string='WO Output Picking'),
		'move_id':fields.many2one('stock.move', string='Move'),
		'wo_raw_material_id':fields.many2one('sbm.work.order.output.raw.material', required=True, string='Raw Materials'),
	}


SBM_Work_Order_Output_Move()



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

SBM_Work_Order_Output_Raw_Material()



class SBM_Work_Order_Line_Files(osv.osv):
	_name = 'sbm.work.order.line.files'
	_columns = {
		'name':fields.char('Name', required=True),
		'file':fields.binary('File  Doc'),
		'work_order_output_id':fields.many2one('sbm.work.order.output',string='Output'),
	}

SBM_Work_Order_Line_Files()