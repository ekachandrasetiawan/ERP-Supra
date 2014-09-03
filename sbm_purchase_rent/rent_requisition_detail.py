import time
import netsvc
from osv import osv, fields


# Model Rent Requisition
class RentRequisitionDetail (osv.osv):
	_name = 'rent.requisition.detail'
	_columns = {
		'name'					: fields.many2one('product.product','Product',domain = [('is_rent_item','=',True)]),
		'qty'						: fields.float('Qty',required=True),
		'uom'						: fields.many2one('product.uom','Satuan'),
		'notes'					: fields.text('Notes'),
		'rent_requisition_id': fields.many2one('rent.requisition','Rent Requisition',ondelete='cascade'),
		'state': fields.selection(
			(
				('draft','Draft'),
				('confirm','Confirm'),
				('process','Process'),
				('done','Done'),
			),'State'
		)
	}

	def _getUnit(obj, cr, uid, context=None):
		if context is None:
			context = {}
		uomid = obj.pool.get('product.uom').search(cr,uid,[('name','=','Unit(s)')],context=context)
		if uomid:
			return uomid[0]
		return False

	_defaults = {
		'qty'						: 1.00,
		'uom'						: _getUnit,
		'state'					: 'draft',
	}
RentRequisitionDetail()


class Wizard_Rent_Requisition_Detail(osv.osv_memory):
	_name = 'wizard.rent.requisition.detail'
	_columns ={
		'suplier':fields.many2one('res.partner','Supplier', required=True, domain=[('supplier','=',True)]),
		'product':fields.many2one('product.product','Product'),
		'qty': fields.integer('Qty'),
		# 'price_unit': fields.float('Unit Price',required=True),
		'product_uom' : fields.many2one('product.uom','Satuan'),
		'pb_line_id' 	: fields.many2one('rent.requisition.detail','Line Requisition Detail'),
		'detail_pb_id': fields.many2one('wizard.po.rent', 'Detail PO', required=True, ondelete='cascade'),
		# 'contract_id' : fields.many2one('purchase.order.contract.data','Contract',ondelete="Cascade"),
		'po_will_be_print' : fields.integer('PO will Be Printed',required=True)
	}
	_defaults = {
		'po_will_be_print': 1,
	}
	
	# def setProduct(self,cr,uid,ids, pid):
	# 	pb_id = self.pool.get('rent.requisition').browse(cr,uid, pid) 
	# 	product =[x.name.id for x in pb_id.details]

	# 	if len(product) == 1:
	# 		return {
	# 			'value': {
	# 				'product': product[0],
	# 				'qty': pb_id.details[0].qty
	# 			}
	# 		}
	# 	else:
	# 		return {'productnya': len(product),'domain': {'product': [('id','in',tuple(product))]}}
	
	def setQty(self,cr,uid,ids, pid, pb):
		pb_id = self.pool.get('rent.requisition').browse(cr,uid, pb) 
		pb_product = self.pool.get('rent.requisition').browse(cr,uid, pid)
		cek=self.pool.get('rent.requisition.detail').search(cr,uid,[('rent_requisition_id', '=' ,pb_id.id),('name', '=' ,pid)])
		hasil=self.pool.get('rent.requisition.detail').browse(cr,uid,cek)[0]
		return {'value':{ 'qty':hasil.jumlah_diminta} }
Wizard_Rent_Requisition_Detail()