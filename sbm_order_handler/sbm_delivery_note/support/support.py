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

class order_preparation_line(osv.osv):
	_inherit = "order.preparation.line"

	_columns ={
	'no_op': fields.related('preparation_id','name', type='char',string="No OP" ,relation='order.preparation'),
	'status': fields.related('preparation_id','state', type='char',string="Status" ,relation='order.preparation'),
	}

class delivery_note(osv.osv):
	_inherit = "delivery.note"

	def create_invoice_dn(self,cr,uid,ids,context={}):
		dn = self.browse(cr,uid,ids,context)[0] #objek delivery Note id dari ids
		isi_noteline=[]
		op = self.pool.get('order.preparation').browse(cr,uid,dn.prepare_id.id)#browse objek Order Preparation id dari dn.prepare_id.id
		so = self.pool.get('sale.order').browse(cr,uid,op.sale_id.id)#browse objek sale order id dari op.sale_id.id
		localtime = time.asctime( time.localtime(time.time()) )#waktu Local
		local_month = "0"+str(time.localtime(time.time()).tm_mon)#waktu local month
		

		act_inv = self.pool.get('account.invoice') #objek account invoice
		act_inv_line = self.pool.get('account.invoice.line')#objek account invoice line
		

		if dn.picking_id: # cek apa ada picking_id di delivery note ada 

			sp = self.pool.get('stock.picking').browse(cr,uid,dn.picking_id.id)#browse objek stock.picking dari dn.picking_id.id
			
			print "masukkk sini 2 "
			if sp.invoice_id: # cek apakah ada invoice id di stock picking
				print "testtt masu2"
				if sp.invoice_id.state != 'cancel': # cek apakah invoice state tidak sama dengan cancel
				
					raise osv.except_osv(_('Warning'),_('Invoice dari Delivery note sudah pernah terbentuk \n'+'Id :'+str(sp.invoice_id.id)+"\nNo Kwitansi :"+str(sp.invoice_id.kwitansi)+"\n No Faktur :"+str(sp.invoice_id.faktur_pajak_no))) #warning

		else: 
			self.write(cr,uid,ids,{'picking_id':op.picking_id.id}) #mengedit jika picking tidak ada 
			dn = self.browse(cr,uid,ids,context)[0] #objek delivery Note yang baru id dari ids 
			sp = self.pool.get('stock.picking').browse(cr,uid,dn.picking_id.id)#browse objek stock.picking dari dn.picking_id.id yang baru
			print "masukkk sini "
			if sp.invoice_id: #cek apakah ada invoice id di stock_picking
				print "testtt masu"
				if sp.invoice_id.state != 'cancel':  #  
					raise osv.except_osv(_('Warning'),_('Invoice dari Delivery note sudah pernah terbentuk\n'+'Id :'+str(sp.invoice_id.id)+"\nNo Kwitansi :"+str(sp.invoice_id.kwitansi)+"\n No Faktur :"+str(sp.invoice_id.faktur_pajak_no))) #warning

		#mengecek id invoice di so dan jika ada dan state invoicenya selain cancel muncul warning dan di putus 
		#{
		if so.invoice_ids:
			for this_invoice_so in so.invoice_ids:
				if this_invoice_so.state != 'cancel':
					raise osv.except_osv(_('Warning'),_('Invoice dari sale order sudah terbentuk\n'+'Id :'+str(this_invoice_so.id)+"\nNo Kwitansi :"+str(this_invoice_so.kwitansi)+"\n No Faktur :"+str(this_invoice_so.faktur_pajak_no))) #}

		#nilai yang akan di input di invoice
		for note_lines in dn.note_lines:
			# nilai yang akan di input ke invoice line
			isi_noteline.append((0,0,{
			'product_id':note_lines.product_id.id, #dari product account invoice line
			'quantity':note_lines.product_qty, #dari qty account invoice line
			'price_unit':note_lines.sale_line_id.price_unit, #dari price sale order line
			'uos_id':note_lines.product_uom.id,#dari uom account invoice line
			
			'name':note_lines.product_id.name#dari nama  product di note_lines
			})) 
		values_invoice={ 
			'partner_id':dn.partner_id.id,# dari dn customer
			'journal_id':1, #isinya sales journal idr
			'account_id':56, # isinya 111401 Piutang usaha
			'currency_id':so.pricelist_id.id, # dari so Currency nya
			'date_invoice':localtime, # waktu hari ini di local komputer
			'tax_period':local_month,# waktu bulan ini
			'company_id':1,# default PT SupraBakti Mandiri
			'group_id':so.group_id.id,# group sales dari so
			'user_id':so.user_id.id,#  sales person dari so
			'origin':dn.name,# delivery note 
			'name':dn.poc,# Customer Reference dari dn
			'invoice_line':isi_noteline
		}
		
		create_invoice =act_inv.create(cr, uid, values_invoice, context=None) # untuk membuat Invoice blm termasuk invoice line
	
		#perulangan untuk masuk ke delivery note_lines
		
		



		
		self.pool.get('stock.picking').write(cr,uid,dn.picking_id.id,{'invoice_id':create_invoice,'invoice_state':'invoiced'})
		mod_obj = self.pool.get('ir.model.data') #objek ir_model_data
		res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')#mencari view id di objek ir.model.data
		res_id = res and res[1] or False,
		return {
			'name': _('Customer Invoices'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [res_id],
			'res_model': 'account.invoice',
			'context': "{'type':'out_invoice'}",
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id':create_invoice #id invoice untuk di tampilin
		
		}
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

	def _date_order(self,cr,uid,ids,name,args,context={}):
		res={}
		for material in self.browse(cr,uid,ids):
			
			res[material.id]=material.sale_order_id.date_order
		return res

	def _due_date(self,cr,uid,ids,name,args,context={}):
		res={}
		for material in self.browse(cr,uid,ids):
			
			res[material.id]=material.sale_order_id.due_date
	
		return res

	def _delivery_note(self,cr,uid,ids,name,args,context={}):
		
		id_dn=[] # untuk menampung id dn 
		#browse data material
		material = self.browse(cr,uid,ids)[0]
		
		#kondisi untuk mengecek Op_lines
		if material.op_lines:
			#perulangan op_lines
			for loop_lines in material.op_lines:
				#mencari id order preparation berdasarkan 'prepare_lines','=',loop_lines.id
				order_preparation_id = self.pool.get("order.preparation").search(cr,uid,[('prepare_lines','=',loop_lines.id)])
				#browse order preparation berdasarka order_preparation_id
				order_preparation = self.pool.get("order.preparation").browse(cr,uid,order_preparation_id)
				for op in order_preparation:
					#mencari id dari delivery note
					delivery_note_id = self.pool.get("delivery.note").search(cr,uid,[('prepare_id','=',op.id)])
					
					#menambahkan data ke id_dn
					id_dn.append(delivery_note_id[0])
		res = dict([(id, id_dn) for id in ids])
	
	
		return res

	_columns = {
		'op_lines':fields.one2many('order.preparation.line','sale_line_material_id',string="Order Preparation Lines"),
		'shipped_qty':fields.function(_count_shipped_qty,string="Shipped Qty",store=False),
		'returned_qty':fields.function(_count_returned_qty, string="Returned Qty", store=False),
		'on_process_qty':fields.function(_count_process_qty, string="On process Qty", store=False),
		'date_order':fields.function(_date_order, string="Date Order",type="date", store=False),
		'due_date':fields.function(_due_date, string="Due Date",type="date", store=False),
		'delivery_note':fields.function(_delivery_note,string="Delivery Note",type="one2many",relation="delivery.note", store=False)
	

		}

sale_order_material_line()
