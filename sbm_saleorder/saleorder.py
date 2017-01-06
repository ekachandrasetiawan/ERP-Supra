import calendar
import time
import netsvc
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
from osv import osv, fields


class SaleOrder(osv.osv):

	def action_create_pb(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_saleorder', 'wizard_create_pb_form')
		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'wizard_create_pb_form',
			'res_model': 'wizard.create.pb',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}

	_inherit = 'sale.order'

	def action_create_pb_subcount(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_saleorder', 'wizard_create_pb_subcount_form')
		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'wizard_create_pb_subcount_form',
			'res_model': 'wizard.create.pb.subcount',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}


SaleOrder()


class WizardCreatePB(osv.osv_memory):
	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		so_ids = context.get('active_ids', [])
		active_model = context.get('active_model')
		res = super(WizardCreatePB, self).default_get(cr, uid, fields, context=context)
		if not so_ids or len(so_ids) != 1:
			return res
		so_id, = so_ids
		if so_id:
			res.update(so_id=so_id)
			so = self.pool.get('sale.order').browse(cr, uid, so_id, context=context)
			linesData = []
			linesData += [self._load_so_line(cr, uid, l) 
			for l in so.order_line 
				if l.state not in ('done','cancel')]
			res.update(lines=linesData)
		return res

	def _load_so_line(self, cr, uid, line):
		so_item = {
			'so_line_id'		: line.id,
			'product_id'		: line.product_id.id,
			'description'		: line.name,
			'uom'				: line.product_uom.id,
			'qty'				: line.product_uom_qty,
		}
		return so_item

	def request_create_pb(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]
		sale_order = self.pool.get("sale.order")
		pembelian_barang = self.pool.get('pembelian.barang')
		detail_pb = self.pool.get('detail.pb')
		
		sale=val.so_id
		
		if sale.due_date:
			duedate=sale.due_date
		else:
			duedate=time.strftime("%Y-%m-%d")

		empl=self.pool.get('hr.employee').search(cr,uid,[('user_id', '=' ,uid)])
		employee=self.pool.get('hr.employee').browse(cr,uid,empl)[0]

		sid = pembelian_barang.create(cr, uid, {
										'name':'/',
										'proc_type':'sales',
										'source_model':'sales',
										'employee_id':employee.id,
										'department_id':employee.department_id.id,
										'spk_no':sale.client_order_ref,
										'tanggal':time.strftime("%Y-%m-%d"),
										'ref_pb':sale.client_order_ref,
										'duedate':duedate,
										'notes':val.note,
										'state':'draft'
									   })
		for line in val.lines:
			detail_pb.create(cr, uid, {
										 'name':line.product_id.id,
										 'desc':line.description,
										 'detail_pb_id':sid,
										 'part_number':line.product_id.default_code,
										 'jumlah_diminta':line.qty,
										 'satuan':line.uom.id,
										 'sale_line_ids':line.so_line_id.id,
										 'sale_order_material_line_id':line.id,
										 })


		pool_data=self.pool.get("ir.model.data")
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'sbm_purchase', "view_pb_form")     
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'pembelian.barang.form'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'pembelian.barang'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = sid
		return action

	_name="wizard.create.pb"
	_description="Wizard Create Purchase Requisition"
	_columns = {
		'so_id':fields.many2one('sale.order',string="Sales Order",required=True),
		'lines':fields.one2many('wizard.create.pb.line','lines_id',string="Lines"),
		'note':fields.text('Note',required=True,help="Reason why item(s) want to be cancel"),
	}
	_rec_name="so_id"


WizardCreatePB()


class WizardCreatePBLine(osv.osv_memory):
	_name="wizard.create.pb.line"
	_description="Wizard Create Purchase Requisition Line"
	_columns={
		'lines_id':fields.many2one('wizard.create.pb',string="Wizard",required=True,ondelete='CASCADE',onupdate='CASCADE'),
		'so_line_id':fields.many2one('sale.order.line','Item Line',required=True),
		'product_id':fields.many2one('product.product',string="Product",required=True),
		'description':fields.text('Desc'),
		'qty':fields.float('Qty',required=True),
		'uom':fields.many2one('product.uom',string="Unit of Measure",required=True),
		'unit_price':fields.float('Unit Price'),
		'discount_amount':fields.float('Discount (Amount)'),
		'discount_percent':fields.float('Discount (Percentage)'),
		'subtotal':fields.float('Subtotal'),
	}
	_rec_name = 'lines_id'

WizardCreatePBLine()


#  Wizard Create PB Subcount

class WizardCreatePBSubcount(osv.osv_memory):

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		so_ids = context.get('active_ids', [])
		active_model = context.get('active_model')
		res = super(WizardCreatePBSubcount, self).default_get(cr, uid, fields, context=context)
		if not so_ids or len(so_ids) != 1:
			return res
		so_id, = so_ids
		if so_id:
			res.update(so_id=so_id)
			so = self.pool.get('sale.order').browse(cr, uid, so_id, context=context)
			linesData = []
			linesData += [self._load_so_line(cr, uid, l) 
			for l in so.order_line 
				if l.state not in ('done','cancel')]
			res.update(lines=linesData)
		return res

	def _load_so_line(self, cr, uid, line):
		so_item = {
			'so_line_id'		: line.id,
			'product_id'		: line.product_id.id,
			'description'		: line.name,
			'uom'				: line.product_uom.id,
			'qty'				: line.product_uom_qty,
		}		
		return so_item

	def request_create_pb_subcount(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]
		sale_order = self.pool.get("sale.order")
		obj_prs = self.pool.get('purchase.requisition.subcont')
		obj_prs_line = self.pool.get('purchase.requisition.subcont.line')

		sale=val.so_id
		if sale.due_date:
			duedate=sale.due_date
		else:
			duedate=time.strftime("%Y-%m-%d")
		sid = obj_prs.create(cr, uid, {
										'name':self.pool.get('ir.sequence').get(cr, uid, 'purchase.requisition.subcont'),
										'user_id': uid,
										# 'spk_no':sale.client_order_ref,
										'date_start':time.strftime("%Y-%m-%d"),
										'ref_pb':sale.client_order_ref,
										'date_end':duedate,
										'description':sale.note
									   })
		
		for line in val.lines:
			obj_prs_line.create(cr, uid, {
										 'name':line.product_id.id,
										 'detail_pb_id':sid,
										 'part_number':line.product_id.default_code,
										 'jumlah_diminta':line.qty,
										 'satuan':line.uom.id,
										 'keterangan':line.description,
										 'sale_line_ids':line.so_line_id.id
										 })


		pool_data=self.pool.get("ir.model.data")
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'ad_purchase_subcont', "view_purchase_requisition_subcont_form")     
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'pembelian.barang.form'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'pembelian.barang'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = sid
		return action

	_name="wizard.create.pb.subcount"
	_description="Wizard Create Purchase Requisition Subcount"
	_columns = {
		'so_id':fields.many2one('sale.order',string="Sales Order",required=True),
		'lines':fields.one2many('wizard.create.pb.line.subcount','lines_id',string="Lines"),
		'note':fields.text('Note',required=True,help="Reason why item(s) want to be cancel"),
	}
	_rec_name="so_id"


WizardCreatePBSubcount()


class WizardCreatePBLineSubcount(osv.osv_memory):
	_name="wizard.create.pb.line.subcount"
	_description="Wizard Create Purchase Requisition Line Subcount"
	# def setproduct(self,cr,uid,ids, so_line_id):
	# 	print '=================LINE ID==========',so_line_id
	# 	if so_line_id:
	# 		# ceklineID=self.pool.get('sale.order').search(cr,uid,[('id', '=' ,so_line_id)])
	# 		so_line=self.pool.get('sale.order').browse(cr,uid,so_line_id)
	# 		print '===============CEK ================',so_line.order_id
	# 		# products=self.pool.get('sale.order').browse(cr,uid,so_line.order_id)
	# 		# pn = products.default_code
	# 		# product =[x.id for x in hasil]
	# 		return {'domain': {'variants': [('id','in',tuple(product))]}}

	_columns={
		'lines_id':fields.many2one('wizard.create.pb.subcount',string="Wizard",required=False,ondelete='CASCADE',onupdate='CASCADE'),
		'so_line_id':fields.many2one('sale.order.line','Item Line',required=False),
		'product_id':fields.many2one('product.product',string="Product",required=True),
		'description':fields.text('Desc'),
		'request':fields.text('Request'),
		'qty':fields.float('Qty',required=False),
		'uom':fields.many2one('product.uom',string="Unit of Measure",required=False),
		'unit_price':fields.float('Unit Price'),
		'discount_amount':fields.float('Discount (Amount)'),
		'discount_percent':fields.float('Discount (Percentage)'),
		'subtotal':fields.float('Subtotal'),
	}
	_rec_name = 'lines_id'


WizardCreatePBLine()

