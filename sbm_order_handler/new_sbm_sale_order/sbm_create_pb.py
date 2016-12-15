import time

from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.osv.orm import browse_record, browse_null
from openerp.tools.translate import _


class purchase_requisition(osv.osv):
	_inherit = 'pembelian.barang'
	_columns={
		'destination_location_request_id': fields.many2one('stock.location', "Destination Location", required=False),
		'department_id':fields.many2one('hr.department','Department',readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'proc_type':fields.selection([('sales','Sales Order/Project/Work Order'),('internal','Internal/Consumable')],'Proc Type',required=True),
	}

	def submit(self,cr,uid,ids,context={}):
		val = self.browse(cr, uid, ids)[0]

		context.update(action_state='submit')
		
		if val.proc_type == 'sales':
			sequence = 'SBM/PB/S/' + time.strftime('%y') + self.pool.get('ir.sequence').get(cr, uid, 'pembelian.barang.sales')
		else:
			sequence = 'SBM/PB/I/' + time.strftime('%y') + self.pool.get('ir.sequence').get(cr, uid, 'pembelian.barang.internal')

		return self.write(cr,uid,ids,{'state':'confirm','name':sequence},context=context)

purchase_requisition()

class create_pb_material_line(osv.osv_memory):
	_name = "create.pb.material.line"
	_description = "Create PB Sale Order Material Line"
	_columns = {
		'name':fields.char(string='Sale Order'),
		'client_order_ref':fields.char(string='Customer Reference'),
		'detail_ids':fields.one2many('create.pb.detail.material.line','detail_id', 'Detail ID'),
	}

	def default_get(self, cr, uid, fields, context=None):
		if context is None: 
			context = {}

		active_ids = context['active_ids']
		active_model = context.get('active_model')

		res = super(create_pb_material_line, self).default_get(cr, uid, fields, context=context)
		
		so_name = ''
		po_no = ''
		linesData = []
		if active_ids:
			if context.get('active_model','') == 'sale.order.material.line' and len(context['active_ids']) > 0:
				so_id = []
				for x in context['active_ids']:
					data =self.pool.get('sale.order.material.line').browse(cr,uid,x)
					so_id += [data.sale_order_id.id]

					linesData += [self._load_so_line(cr, uid, data)]

				for y in set(so_id):
					line =self.pool.get('sale.order').browse(cr,uid,y)
					so_name += str(line.name + ',')
					po_no += str(line.client_order_ref + ',')

			res.update(name=so_name[:-1])
			res.update(client_order_ref=po_no[:-1])
			res.update(detail_ids=linesData)

		return res

	def _load_so_line(self, cr, uid, line):
		so_item = {
			'product_id'		: line.product_id.id,
			'qty'				: line.qty,
			'uom'				: line.uom.id,
		}

		return so_item

	def create_pb(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		pb_obj = self.pool.get('pembelian.barang')
		pb_detail_obj = self.pool.get('detail.pb')

		if context is None:
			context = {}

		empl=self.pool.get('hr.employee').search(cr,uid,[('user_id', '=' ,uid)])
		employee=self.pool.get('hr.employee').browse(cr,uid,empl)[0]

		if not employee.id:
			raise osv.except_osv(('Information..!!'), ('User Tidak di Daftarkan di Employee ..'))

		duedate = ''
		for x in context['active_ids']:
			data =self.pool.get('sale.order.material.line').browse(cr,uid,x)
			duedate = data.sale_order_id.due_date

		if duedate == False:
			duedate = time.strftime('%Y-%m-%d')
		pb_id = pb_obj.create(cr, uid, {
								'name': '/',
								'spk_no':val.client_order_ref,
								'tanggal':time.strftime('%Y-%m-%d'),
								'proc_type':'sales',
								'duedate':duedate,
								'employee_id':employee.id,
								'department_id':employee.department_id.id,
								'ref_pb':val.name,
								'source_location_request_id':12
							})

		for line in val.detail_ids:
			pb_detail_obj.create(cr, uid, {
										 'name':line.product_id.id,
										 'part_no':line.product_id.default_code,
										 'jumlah_diminta':line.qty,
										 'satuan':line.uom.id,
										 'keterangan':line.notes,
										 'detail_pb_id':pb_id
										 })

		pool_data=self.pool.get("ir.model.data")
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'sbm_purchase', "view_pb_form")     
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'pembelian.barang.view.pb.form'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'pembelian.barang'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = pb_id
		return action
		
create_pb_material_line()


class create_pb_detail_material_line(osv.osv_memory):
	_name = "create.pb.detail.material.line"
	_description = "Create PB Detail Sale Order Material Line"
	_columns = {
		'detail_id':fields.many2one('create.pb.material.line', required=False,readonly=True),
		'product_id':fields.many2one('product.product',string='Product', required=True),
		'qty':fields.float(string='Qty', required=True),
		'uom':fields.many2one('product.uom','UOM'),
		'notes':fields.text(string='Notes', required=False),
	}
		
create_pb_detail_material_line()