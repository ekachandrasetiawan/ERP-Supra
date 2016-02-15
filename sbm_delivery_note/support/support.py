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
						if dn.state == "done":
							shipped_qty+=dn_material.qty
					
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
				order_preparation_id = self.pool.get("order.preparation").search(cr,uid,[('prepare_lines','=',op_lines.id)])
				order_preparation = self.pool.get("order.preparation").browse(cr,uid,order_preparation_id)
				
				for op in order_preparation:
					
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
