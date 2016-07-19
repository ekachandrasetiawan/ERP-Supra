from datetime import datetime
import math
import time
import netsvc
from osv import osv, fields


# Model Rent Requisition
class RentRequisition (osv.osv):
	_name = 'rent.requisition'

	# CONTOH FIELD FUNCTION
	# def _date_(self, cr, uid, ids, fields, arg, context):
	# 	x={}
	# 	for record in self.browse(cr, uid, ids):
	# 		if record.due_date :
	# 			a = datetime.strptime(record.due_date, "%Y-%m-%d")
	# 			b = a.strftime("%m")
	# 			x[record.id] = b
	# 	return x

	_columns = {
		'name': fields.char('Req No',40, required=True),
		'ref_no': fields.char('Ref No.',20,required=True),
		'spk_no': fields.char('SPK No',40,required=True),
		'date_create': fields.date('Date Input',readonly=True),
		'due_date': fields.date('Due Date'),
		# 'date_start' : fields.date('Start on',required=True),
		'date_expire' : fields.date('Until',required=False),
		'employee_id': fields.many2one('hr.employee','Request By',required=True,ondelete='cascade'),
		'department_id': fields.many2one('hr.department','Dept/Section',required=False,ondelete='cascade'),
		'customer_id': fields.many2one('res.partner','Project',required=True, ondelete='cascade',domain=[('customer','=',True)]),
		'type': fields.selection(
			(
				('tools','Tools'),('car','Car')
			),
			'Item Type'
		),
		'notes': fields.text('Notes',select=True),
		'state': fields.selection((('draft','Draft'),('check','Check'),('confirm','Confirm'),('purchase','Purchase'),('done','Done')),'State'),
		'details': fields.one2many('rent.requisition.detail','rent_requisition_id','Details'),

		# 'orders' : fields.one2many('purchase.order','origin')


		# 'test' : fields.function(_date_, type='char', string='date copy'),

	}
	def _employee_get(obj, cr, uid, context=None):
	    if context is None:
	        context = {}
	    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
	    if ids:
	        return ids[0]
	    return False

	_defaults={
		'name': '/',
		'state': 'draft',
		'date_create': time.strftime('%Y-%m-%d'),
		'employee_id': _employee_get
	}

	# def setProduct(self,cr,uid,ids, pid):
	# 	pb_id = self.pool.get('rent.requisition').browse(cr,uid, pid)
	
	def chooseEmployee(self,cr, uid, ids, eid):
		employee = self.pool.get('hr.employee').browse(cr,uid,eid)
		# print "0000000000000000000000000000------------",employee.department_id.id
		return {'value': {'department_id':employee.department_id.id}}
		# return {'test': context}

	def confirm2(self,cr,uid,ids,context=None):
#		val = self.browse(cr, uid, ids)[0]
#		usermencet = self.pool.get('res.user')
#		if val.employee_id.parent_id.id != uid :
#			raise osv.except_osv(('Perhatian..!!'), ('Harus Atasannya langsung ..'))
#		cr.execute('Update detail_pb Set state=%s Where detail_pb_id=%s', ('onproses',ids[0]))
		return self.write(cr,uid,ids,{'state':'purchase'})

	def create(self,cr,uid,vals,context=None):
		vals['name']=self.pool.get('ir.sequence').get(cr,uid,'rent.requisition')
		return super(RentRequisition, self).create(cr,uid,vals,context=context)

	# def onChangeType(self,cr,uid,ids,type,context=None):
		# return {'value':{'notes':type}}

	#action tombol Ok
	# def setOk(self,cr,uid,ids,context=None):
	# 	return self.write(cr,uid,ids,{'state':'confirm'})

	def setCheck(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'check'})

	def setConfirm(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]
		usermencet = self.pool.get('res.user')
#		if val.employee_id.parent_id.id != uid :
#			raise osv.except_osv(('Perhatian..!!'), ('Harus Atasannya langsung ..'));
		return self.write(cr,uid,ids,{'state':'confirm'})

	def setPurchase(self,cr,uid,ids,context=None):
		selfData = self.browse(cr,uid,ids,context=context)[0]
		detailIds = []
		for d in selfData.details:
			detailIds.append(d.id)
		
		self.pool.get('rent.requisition.detail').write(cr,uid,detailIds,{'state':'confirm'})
		return self.write(cr,uid,ids,{'state':'purchase'})

	def setDone(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'done'})

	
	# def printRentRequisition(self,cr,uid,ids,context=None):
	# 	if context is None:
	# 		context = {}
	# 	datas = {'ids': context.get('active_ids', [])}
	# 	datas['model'] = 'rent.requisition'
	# 	datas['form'] = self.read(cr, uid, ids)[0]
		
	# 	return {
	# 		'type': 'ir.actions.report.xml',
	# 		'report_name': 'print.pbrent',
	# 		'report_type': 'webkit',
	# 		'datas': datas,
 	#  }
		

RentRequisition()

class Wizard_Rent_PO(osv.osv_memory):
	_name = 'wizard.po.rent'
	_rec_name = 'req_ref';
	_columns ={
		'req_ref':fields.many2one('rent.requisition','Requisition Reference', required=True, domain=[('state','=',[('purchase')])]),
		# 'name':fields.many2one('res.partner','Supplier', required=True, domain=[('supplier','=',True)]),
		'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=True),
		# 'product':fields.many2one('product.product','Product', required=True,),
		# 'price_unit': fields.float('Unit Price',required=True),
		# 'qty':fields.integer('Qty', required=True,),
		'due_date': fields.date('Due Date',required=True),
		'detail_pb_ids': fields.one2many('wizard.rent.requisition.detail', 'detail_pb_id', 'Rent Requisition Detail'),
	}
	
	_defaults = {
		# 'qty':1
	}

	def setProduct(self,cr,uid,ids, pid):
		pb_id = self.pool.get('rent.requisition').browse(cr,uid, pid)

		details = []
		for d in pb_id.details:
			details.append({
				'product':d.name.id,
				'qty':d.qty,
				# 'price_unit': 0,
				'product_uom': d.uom.id,
				'pb_line_id': d.id ,
				# 'suplier' : 992, #for test
			})
			print "-------------------------",d.id

		# if len(product) == 1:
		return {
			'value': {
				'due_date': pb_id.due_date,
				'detail_pb_ids': details
			}
		}

	# for detail in val.detail_pb_ids:
	# 	suppliers[detail.suplier.id] = []
	# 	print "===========================",detail
	# for detail in val.detail_pb_ids:
	# 	suppliers[detail.suplier.id].append(detail)

	def create_po(self,cr,uid,ids,context=None):
		val = self.browse(cr,uid,ids)[0]
		suppliers = {}
		# for i in range(0,3):
		# 	print i
		# print "===+++++++++++++++++++==="
		for detail in val.detail_pb_ids:
			# print "============================",detail.po_will_be_print
			# make suppier dictionary
			if detail.suplier.id not in suppliers:
				suppliers[detail.suplier.id] = {}
				suppliers[detail.suplier.id][detail.po_will_be_print] = []
			if detail.po_will_be_print not in suppliers[detail.suplier.id]:
				suppliers[detail.suplier.id][detail.po_will_be_print] = []

			suppliers[detail.suplier.id][detail.po_will_be_print].append(detail)


		# print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",suppliers
		newPO = self.pool.get("purchase.order")
		newDetailPO = self.pool.get("purchase.order.line")
		listId = []
		for supplierId,eachSupplier in suppliers.items():
			for printQty, detailsPO in eachSupplier.items():
				# print printQty
				# Determine po
				# print detailsPO
				
				# print "=================DETAILSPO==============="
				# print type(printQty)
				# LOOP QTY
				for i in range(0,printQty):
					# print i
					if detailsPO[0].suplier.term_payment:
						termpayment = detailsPO[0].suplier.term_payment
					else:
						termpayment = ""
					newPOValue = {
						'name'				:	str(int(time.time())) + str(i),
						'date_order'		:	time.strftime('%Y-%m-%d'),
						'pricelist_id'		:	val.pricelist_id.id,
						'partner_id'		:	supplierId,
						'location_id'		:	12,
						'origin'				:	val.req_ref.name,
						'term_of_payment'	:	termpayment,
						'type_permintaan'	: '2',
						'jenis'				: 'loc'

					}
					# if first po then set duedate base on input
					if i==0: 
						newPOValue['duedate'] = val.due_date
					else:
						newPOValue['duedate'] = time.strftime('%Y-%m-%d')

					idPO = newPO.create(
						cr,
						uid,
						newPOValue
					)
					print idPO
					listId.append(idPO)
					# LOOP DETAILS
					for detailPO in detailsPO:
						print "################################################",detailPO.pb_line_id.id
						newDetailPO.create(
							cr,
							uid,
							{
								'date_planned'		: time.strftime("%Y-%m-%d"),
								'order_id'			: idPO,
								'name'				: detailPO.product.name,
								'product_id'		: detailPO.product.id,
								'product_qty'		: detailPO.qty,
								'product_uom'		: detailPO.product.uom_id.id,
								'price_unit'		: 0,
								'line_pb_rent_id'	: detailPO.pb_line_id.id,

							}
						)
		# print "===============================================================",suppliers
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'purchase', 'purchase_order_tree')
		return {
			'view_mode': 'tree',
			'view_id': (view_id,'View'),
			'view_type': 'tree',
			'res_model': 'purchase.order',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': "[('id','in',"+str(listId)+")]",
		}
		return True

Wizard_Rent_PO()



class InheritPO(osv.osv):
	_inherit = 'purchase.order.line'
	_columns = {
		'line_pb_rent_id' : fields.many2one('rent.requisition.detail','Line Requisition'),
	}
InheritPO()
