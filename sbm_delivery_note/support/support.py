from datetime import datetime
from stock import stock
import math
import time
import webbrowser
import netsvc
import openerp.exceptions
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class delivery_note(osv.osv):
	_inherit = "delivery.note"

	def create_invoice_dn(self,cr,uid,ids,context={}):
		dn = self.browse(cr,uid,ids,context)[0] #objek delivery Note
		op = self.pool.get('order.preparation').browse(cr,uid,dn.prepare_id.id)#objek Order Preparation
		so = self.pool.get('sale.order').browse(cr,uid,op.sale_id.id)#objek sale order
		
		localtime = time.asctime( time.localtime(time.time()) )#waktu Local
		local_month = "0"+str(time.localtime(time.time()).tm_mon)
		

		act_inv = self.pool.get('account.invoice')
		act_inv_line = self.pool.get('account.invoice.line')
	


		#create account invoice
		values_invoice={ 
			'partner_id':dn.partner_id.id,
			'journal_id':1,
			'account_id':56,
			'currency_id':so.pricelist_id.id,
			'date_invoice':localtime,
			'tax_period':local_month,
			'company_id':1,
			'group_id':so.group_id.id,
			'user_id':so.user_id.id,
			'origin':dn.name,
			'name':dn.poc,

		}
		create_invoice =act_inv.create(cr, uid, values_invoice, context=None)
		#
		# index_note_line = 1
		for note_lines in dn.note_lines:
			# index_order_line = 1
			# for order_line in so.order_line:
			# 	if index_note_line == index_order_line:
			values_invoice_line = {
			'product_id':note_lines.product_id.id,
			'quantity':note_lines.product_qty,
			'price_unit':note_lines.sale_line_id.product_uom_qty,
			'uos_id':note_lines.product_uom.id,
			
			'invoice_id':create_invoice,
			'name':note_lines.product_id.name
			}
			# 		index_order_line += 1
			# 	index_order_line += 1
			# index_note_line += 1
			print note_lines.sale_line_id,"sale id"
			create_invoice_line = act_inv_line.create(cr,uid, values_invoice_line , context=None)


		print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
				
		# sale_order=self.browse(cr,uid,ids)[0]
		return {}

class sale_order_material_line(osv.osv):


	_inherit = 'sale.order.material.line'


	def _count_shipped_qty(self, cr, uid, ids, name, args, context={}):
		res={}
		#Browse ke sale order material line #
		for item in self.browse(cr,uid,ids,context=context):
			shipped_qty=0
			#perulangan op_lines di sale order material line#
			for op_lines in item.op_lines:
				#mencari id delivery note line material berdasarkan op_line_id sama dengan op_line di sale order material line #
				delivery_note_line_material_id = self.pool.get("delivery.note.line.material").search(cr,uid,[('op_line_id','=',op_lines.id)])
				#browse delivery note line material berdasarkan delivery_note_line_material_id#
				delivery_note_line_material = self.pool.get("delivery.note.line.material").browse(cr,uid,delivery_note_line_material_id)
				#perulangan delivery_note_line_material#
				for dn_material in delivery_note_line_material:
					#mencari delivery_note_line.id berdasarkan note_lines_material di dn_material.id #
					delivery_note_line_id = self.pool.get("delivery.note.line").search(cr,uid,[('note_lines_material','in',dn_material.id)])
					#mencari delivery_note.id berdasarkan not_lines di delivery_note_line_id#
					delivery_note_id = self.pool.get("delivery.note").search(cr,uid,[('note_lines','in',delivery_note_line_id)])
					#browse delivery note berdasarkan delivery_note_id#
					delivery_note = self.pool.get("delivery.note").browse(cr,uid,delivery_note_id)
					
					for dn in delivery_note:
					#kondisi di mana state sama dengan done yang berada di delivery_note maka shipped_qty di tambah quantity yang ada di delivery note material qty	
						if dn.state == "done" or dn.state=="refunded":
							shipped_qty+=dn_material.qty
					shipped_qty = shipped_qty - dn_material.refunded_item
					
			res[item.id]=shipped_qty
		return res

	def _count_returned_qty(self, cr, uid, ids, name, args, context={}):
		res={}
		#perulangan Browse ke sale order material line #
		for item in self.browse(cr,uid,ids,context=context):
			# kondisi di mana op_line kosong maka res = 0
			if item.op_lines ==[]:
				res[item.id] =0
			else:
				#jika ada
				for op_lines in item.op_lines:
					#mencari id delivery note line material berdasarkan op_line_id sama dengan op_line di sale order material line #
					delivery_note_line_material_id = self.pool.get("delivery.note.line.material").search(cr,uid,[('op_line_id','=',op_lines.id)])
					#browse delivery note line material berdasarkan delivery_note_line_material_id#
					delivery_note_line_material = self.pool.get("delivery.note.line.material").browse(cr,uid,delivery_note_line_material_id)
					#perulangan delivery_note_line_material#
					#kondisi jika delivery_note_line_material tidak ada
					if delivery_note_line_material ==[]:
						res[item.id] =0
					else: #kondisi jika ada
						for i in delivery_note_line_material:
							res[item.id] =i.refunded_item
		return res #output returned_qty sama dengan refunded_item di delivery note material

	def _count_process_qty(self,cr,uid,ids,name,args,context={}):
		res={}
		for item in self.browse(cr,uid,ids,context=context):
			on_process_qty=0
			for op_lines in item.op_lines:
				#mencari id order preparation berdasarkan id op_lines di material lines
				order_preparation_id = self.pool.get("order.preparation").search(cr,uid,[('prepare_lines','=',op_lines.id)])
				#browse order preparation berdasarka order_preparation_id
				order_preparation = self.pool.get("order.preparation").browse(cr,uid,order_preparation_id)
				#mencari id delivery note material note lines material berdasarkan id op_lines
				delivery_note_line_material_id = self.pool.get("delivery.note.line.material").search(cr,uid,[('op_line_id','=',op_lines.id)])
			
				delivery_note_line_material = self.pool.get("delivery.note.line.material").browse(cr,uid,delivery_note_line_material_id)
				for op in order_preparation:
					if delivery_note_line_material:
						for dn_material in delivery_note_line_material:
							delivery_note_line_id = self.pool.get("delivery.note.line").search(cr,uid,[('note_lines_material','in',dn_material.id)])
						#mencari delivery_note.id berdasarkan not_lines di delivery_note_line_id#
							delivery_note_id = self.pool.get("delivery.note").search(cr,uid,[('note_lines','in',delivery_note_line_id)])
							#browse delivery note berdasarkan delivery_note_id#
							delivery_note = self.pool.get("delivery.note").browse(cr,uid,delivery_note_id)
							for dn in delivery_note:
							#kondisi di mana state sama dengan done yang berada di delivery_note maka shipped_qty di tambah quantity yang ada di delivery note material qty	
								if op.state != "draft" or op.state != "cancel":
									
									if dn.state != "done":
										on_process_qty+=op_lines.product_qty
					else:
						if op.state != "draft" or op.state != "cancel":
							on_process_qty+=op_lines.product_qty

			res[item.id]=on_process_qty
		
		return res


	_columns = {
		'op_lines':fields.one2many('order.preparation.line','sale_line_material_id',string="Order Preparation Lines"),
		'shipped_qty':fields.function(_count_shipped_qty,string="Shipped Qty",store=False),
		'returned_qty':fields.function(_count_returned_qty, string="Returned Qty", store=False),
		'on_process_qty':fields.function(_count_process_qty, string="On process Qty", store=False)
		}

sale_order_material_line()
