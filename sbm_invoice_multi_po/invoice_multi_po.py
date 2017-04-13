import time

from openerp.osv import fields, osv
from openerp import netsvc
from openerp import pooler
from openerp.osv.orm import browse_record, browse_null
from openerp.tools.translate import _

class invoice_multi_po(osv.osv_memory):
	_name = "invoice.multi.po"
	_description = "Invoice Multi PO"

	def fields_view_get(self, cr, uid, view_id=None, view_type='form',
						context=None, toolbar=False, submenu=False):
		if context is None:
			context={}
		
		if context.get('active_model','') == 'purchase.order' and len(context['active_ids']) < 2:
			raise osv.except_osv(_('Warning!'),
			_('Please select multiple order to merge in the list view.'))
		else:
			
			if context.get('active_model','') == 'purchase.order' and len(context['active_ids']) > 1:
				partner = []
				pricelist = []
				for x in context['active_ids']:
					data =self.pool.get('purchase.order').browse(cr,uid,x)

					partner+=[data.partner_id.id]
					pricelist+=[data.pricelist_id.id]

				cekpartner  = []
				for val in partner:
					if val == partner[0]:
						cekpartner += [val]

				cekpricelist  = []
				for val_pricelist in pricelist:
					if val_pricelist == pricelist[0]:
						cekpricelist += [val_pricelist]

				# Cek Partner Harus Sama
				if len(context['active_ids']) <> len(cekpartner):
					raise osv.except_osv(_('Warning!'),
					_('Invoice tidak dapat dibuat untuk beberapa supplier'))
				
				# Cek Pricelist Harus Sama
				if len(context['active_ids']) <> len(cekpricelist):
					raise osv.except_osv(_('Warning!'),
					_('Invoice tidak dapat dibuat untuk beberapa Pricelist'))
				
				# Cek Validasi PO Apakah sudah memiliki Invoice
				for x in context['active_ids']:
					cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", [x])
					invoice = map(lambda x: x[0], cr.fetchall())

					inv =self.pool.get('purchase.order').browse(cr,uid,x)
					data_invoice =self.pool.get('account.invoice').browse(cr,uid,invoice)

					no_kwitansi = ''
					for c in data_invoice:
						if c.kwitansi == False:
							no_kwitansi = ''
						else:
							no_kwitansi += c.kwitansi + ', '

					if invoice:
						raise osv.except_osv(_('Warning!'),
						_('Purchase Order ' + inv.name[:6] + ' Sudah Memiliki Invoice Dengan No "' + no_kwitansi + '"'))		

		return super(invoice_multi_po, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
	
	def merge_orders_invoice(self, cr, uid, ids, context=None):
		fiscal_position_id=False
		order_obj = self.pool.get('purchase.order')
		accinv_obj = self.pool.get('account.invoice')
		accinv_line_obj = self.pool.get('account.invoice.line')
		invoice_rel = self.pool.get('purchase.invoice.rel')
		account_tax = self.pool.get('account.tax')
		account_fiscal_position = self.pool.get('account.fiscal.position')
		if context is None:
			context = {}

		partner = []
		currency_id = []
		amount_untaxed = 0
		amount_tax = 0
		amount_total =0 
		no_po = ''

		line_id = []
		tax_id = []

		for x in context['active_ids']:
			data =self.pool.get('purchase.order').browse(cr,uid,x)
			no_po += data.name + ', '
			partner+=[data.partner_id.id]
			amount_untaxed += data.amount_untaxed
			amount_tax += data.amount_tax
			amount_total += data.amount_total
			currency_id += [data.pricelist_id.id]

			for line in data.order_line:
				line_id += [line.id]
				tax_id += [line.product_id.supplier_taxes_id]
		
		line = self.pool.get('purchase.order.line').browse(cr,uid,line_id[0])	
		
		data_partner= self.pool.get('res.partner').browse(cr,uid,partner[0])
		currency =self.pool.get('product.pricelist').browse(cr,uid, currency_id[0])

		desc = 'Merge PO Dalam 1 Invoice ' + data_partner.name + ' Dengan No PO ' + no_po
		
		sid = accinv_obj.create(cr, uid, {
								'account_id': 119,
								'company_id':1,
								'currency_id':currency.currency_id.id,
								'partner_id':partner[0],
								'user_id':uid,
								'reference_type':'none',
								'journal_id':2,
								'amount_tax':amount_tax,
								'state':'draft',
								'type':'in_invoice',
								'date_invoice':time.strftime("%Y-%m-%d"),
								'amount_untaxed':amount_untaxed,
								'name':desc,
								'sent':False,
								'commercial_partner_id':partner[0],
								'faktur_pajak_no':'0000000000000000'
							   })

		taxes = account_tax.browse(cr, uid, map(lambda line: line.id,line.product_id.supplier_taxes_id))
		fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
		taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
		accinv_line_obj.create(cr, uid, {
								 'origin':desc,
								 'uos_id':1,
								 'account_id':46,
								 'name':desc,
								 'sequence':10,
								 'invoice_id':sid,
								 'price_unit':amount_untaxed,
								 'price_subtotal':amount_untaxed,
								 'company_id':1,
								 'discount':0.00,
								 'quantity':1.00,
								 'partner_id':partner[0],
								 'invoice_line_tax_id': [(6,0,taxes_ids)],
								 })

		# Daftarkan Ke Purchase Invoice Rel
		for y in context['active_ids']:
			cr.execute('insert into purchase_invoice_rel (purchase_id,invoice_id) values (%s,%s)', (y, sid))

		pool_data=self.pool.get("ir.model.data")
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'account', "invoice_supplier_form")     
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'account.invoice.supplier.form'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'account.invoice'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = sid
		return action

invoice_multi_po()


class purchase_order(osv.osv):
	_inherit = 'purchase.order'

	def action_invoice_create(self, cr, uid, ids, context=None):
		obj_pick = self.pool.get('stock.picking')

		cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", ids)
		invoice = map(lambda x: x[0], cr.fetchall())

		data_invoice =self.pool.get('account.invoice').browse(cr,uid,invoice)

		id_pick=obj_pick.search(cr,uid,[('purchase_id', '=' ,ids)])
		picking =obj_pick.browse(cr,uid,id_pick)

		no_kwitansi = ''

		for x in picking:
			if x.invoice_id.kwitansi:
				no_kwitansi = x.invoice_id.kwitansi
			if x.invoice_id.id:
				raise osv.except_osv(_('Warning!'),
				_('Purchase Order Sudah Memiliki Invoice Dari Consolidate Picking Dengan No ' + no_kwitansi))

		
		for c in data_invoice:
			if c.kwitansi:
				no_kwitansi += c.kwitansi + ', '

		if invoice:
			raise osv.except_osv(_('Warning!'),
			_('Purchase Order Sudah Memiliki Invoice ' + no_kwitansi))


		print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

		return super(purchase_order,self).action_invoice_create(cr,uid,ids,context=context)

class purchase_partial_invoice(osv.osv_memory):
	_inherit = "purchase.partial.invoice"

	def create_invoices(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		obj_pick = self.pool.get('stock.picking')

		purchase_ids = context.get('active_ids', [])

		# Cek dari Stock Picking 
		id_pick=obj_pick.search(cr,uid,[('purchase_id', '=' ,purchase_ids)])
		picking =obj_pick.browse(cr,uid,id_pick)

		no_kwitansi = ''

		for x in picking:
			if x.invoice_id.kwitansi:
				no_kwitansi = x.invoice_id.kwitansi
			if x.invoice_id.id:
				raise osv.except_osv(_('Warning!'),
				_('Purchase Order Sudah Memiliki Invoice Dari Consolidate Picking Dengan No ' + no_kwitansi))


		# Cek Total di PO 
		po =self.pool.get('purchase.order').browse(cr,uid,purchase_ids)[0]
		total_po = po.amount_total

		# Akumulasi Nilai Yang diminta dengan yang sudah di buat Invoice
		cek_total = (total_po * val.amount) / 100

		cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", purchase_ids)
		invoice = map(lambda x: x[0], cr.fetchall())

		if invoice:		
			total_invoice = 0
			for x in invoice:
				inv =self.pool.get('account.invoice').browse(cr,uid,x)
				total_invoice += inv.amount_total

			akumulasi_total = total_invoice + cek_total
			if total_invoice == total_po:
				raise osv.except_osv(_('Warning!'),
				_('Purchase Order Sudah Tidak Bisa Dibuat Invoice'))
			elif akumulasi_total > total_po:
				raise osv.except_osv(_('Warning!'),
				_('Nilai Persentase yang Anda Input Terlalu Besar, Total Invoice Sudah Melebih Nilai PO '))

		return super(purchase_partial_invoice,self).create_invoices(cr,uid,ids,context=context)

class merge_pickings(osv.osv_memory):
	_inherit = "merge.pickings"

	_columns = {
		'picking_ids': fields.many2many('stock.picking','merge_do_picking_rel','merge_do_id','picking_id','Pickings', required=True, domain="[('state', '=', 'done'), ('type', '=', type), ('partner_id', '=', partner_id),('invoice_state', '=', '2binvoiced')]"),
	}

	def type_change(self, cr, uid, ids, tipe):
		domain = {'partner_id': [('customer', '=', True)]}
		if tipe == 'in':
			domain = {'partner_id': [('supplier', '=', True)]}
		return {'value':{'picking_ids':None, 'partner_id': None}, 'domain': domain}


	def merge_orders(self, cr, uid, ids, context={}):
		pool_data = self.pool.get('ir.model.data')
		journal_obj = self.pool.get('account.journal')
		pool_invoice = self.pool.get('account.invoice')
		pool_picking = self.pool.get('stock.picking')
		pool_partner = self.pool.get('res.partner')
		pool_invoice_line = self.pool.get('account.invoice.line')

		data = self.browse(cr, uid, ids, context=context)[0]
		picking_ids = [x.id for x in data['picking_ids']]
		partner_obj = data['partner_id']
		print data,"=++++++++++++++++++++++"
		# Valisasi Invoice Picking Cek Po apakah sudah ada Invoice
		for x in picking_ids:
			pick =pool_picking.browse(cr,uid,x)
			invoice = []
			print pick.purchase_id.id,"::::::::::::::::::"
			if pick.purchase_id.id:
				print "AAAAAAAA"
				cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", [pick.purchase_id.id])
				invoice = map(lambda x: x[0], cr.fetchall())
			
			if invoice:
				raise osv.except_osv(_('Warning!'),
				_('Picking '+ pick.name +' dari PO ' + pick.purchase_id.name[:6] + ' Tidak Dapat Di Buat Invoice Dari Consolidate Picking'))


		
		alamat = pool_partner.address_get(cr, uid, [partner_obj.id],['contact', 'invoice'])
		address_contact_id = alamat['contact']
		address_invoice_id = alamat['invoice']
			   
		picking = pool_picking.browse(cr, uid, picking_ids[0], context=context)
		namepick = False
		origin = False
		if data.type == 'out':
			type_inv = 'out_invoice'
			account_id = partner_obj.property_account_receivable.id
			curency = picking.sale_id.pricelist_id.currency_id.id
			journal_ids = journal_obj.search(cr, uid, [('type','=','sale'),('company_id', '=', 1)], limit=1)


			origin = ''
			namepick = ''
			for picking in pool_picking.browse(cr, uid, picking_ids, context=context):
				if picking.note_id.id:
					origin += picking.origin +':'+ (picking.note_id.name)[:7] + ', '
				else:
					origin += picking.origin+ ', '

				namepick += picking.sale_id.client_order_ref + ', '

		elif data.type == 'in':
			type_inv = 'in_invoice'
			account_id = partner_obj.property_account_payable.id
			curency = picking.purchase_id.pricelist_id.currency_id.id
			journal_ids = journal_obj.search(cr, uid, [('type','=','purchase'),('company_id', '=', 1)], limit=1)
		
		if not journal_ids:
			raise osv.except_osv(('Error !'), ('There is no sale/purchase journal defined for this company'))            

		invoice_id = pool_invoice.create(cr, uid, {
			'name': namepick[:-2] if namepick else 'Merged Invoice for '+ partner_obj.name + ' on ' + time.strftime('%Y-%m-%d %H:%M:%S'),
			# 'name': 'Merged Invoice for '+ partner_obj.name + ' on ' + time.strftime('%Y-%m-%d %H:%M:%S'),
			'type': type_inv,
			'account_id': account_id,
			'partner_id': partner_obj.id,
			'journal_id': journal_ids[0] or False,
			'address_invoice_id': address_invoice_id,
			'address_contact_id': address_contact_id,
			'date_invoice': time.strftime('%Y-%m-%d'),
			'user_id': uid,
			'origin':origin[:-2] if origin else False,
			'currency_id': curency or False,
			'picking_ids': [(6,0, picking_ids)]})
		

		# Daftarkan Ke Purchase Invoice Rel
		add_po_id = []
		for y in picking_ids:
			pick2 =pool_picking.browse(cr,uid,y)
			add_po_id += [pick2.purchase_id.id]

		
		#convert list into set
		cek_unique = set(add_po_id)

		#convert back to list
		add_po_id = list(cek_unique)

		# Filter PO ID yang sama, Handle jika Multi Picking dari PO yang sama
		unique_list = [
		e
		for i, e in enumerate(add_po_id)
			if add_po_id.index(e) == i
		]

		if data.type=='in':
			for a in add_po_id:
				cr.execute('insert into purchase_invoice_rel (purchase_id,invoice_id) values (%s,%s)', (a, invoice_id))
		
		for picking in pool_picking.browse(cr, uid, picking_ids, context=context):
			pool_picking.write(cr, uid, [picking.id], {'invoice_state': 'invoiced', 'invoice_id': invoice_id}) 
			for move_line in picking.move_lines:
				disc_amount = 0
				if data.type == 'out':
					price_unit = pool_picking._get_price_unit_invoice(cr, uid, move_line, 'out_invoice')
					tax_ids = pool_picking._get_taxes_invoice(cr, uid, move_line, 'out_invoice')
					line_account_id = move_line.product_id.product_tmpl_id.property_account_income.id or move_line.product_id.categ_id.property_account_income_categ.id
				elif data.type == 'in':
					price_unit = pool_picking._get_price_unit_invoice(cr, uid, move_line, 'in_invoice')
					tax_ids = pool_picking._get_taxes_invoice(cr, uid, move_line, 'in_invoice')
					line_account_id = move_line.product_id.product_tmpl_id.property_account_expense.id or move_line.product_id.categ_id.property_account_expense_categ.id
					disc_amount = move_line.purchase_line_id.discount_nominal
				discount = pool_picking._get_discount_invoice(cr, uid, move_line)
				 
				origin = picking.origin +':'+ (picking.name).strip()
				#origin = (picking.delivery_note).strip() +';'+ (picking.name).strip()
				if picking.note_id:
					# search op line id by move line ID
					
					cekopline=self.pool.get('order.preparation.line').search(cr,uid,[('move_id', '=' ,move_line.id)])

					op_line=self.pool.get('order.preparation.line').browse(cr,uid,cekopline)
					
					if op_line:
						for opl in op_line:
							#Search DN Line ID By OP Line ID
							cek=self.pool.get('delivery.note.line').search(cr,uid,[('op_line_id', '=' ,opl.id)])
							product_dn=self.pool.get('delivery.note.line').browse(cr,uid,cek)[0]

							if cek:
								pool_invoice_line.create(
									cr, uid, 
									{
										'name': product_dn.name,
										'picking_id': picking.id,
										'origin': origin,
										'uos_id': move_line.product_uos.id or move_line.product_uom.id,
										'product_id': move_line.product_id.id,
										'price_unit': price_unit,
										'discount': discount,
										'quantity': move_line.product_qty,
										'invoice_id': invoice_id,
										'invoice_line_tax_id': [(6, 0, tax_ids)],
										'account_analytic_id': pool_picking._get_account_analytic_invoice(cr, uid, picking, move_line),
										'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, partner_obj.property_account_position, line_account_id),
										'amount_discount':disc_amount
									}
								)
							else:
								raise osv.except_osv(('Perhatian..!!'), ('No Delivery Note Tidak Ditemukan'))
						# end for
					else:
						pool_invoice_line.create(
							cr, uid, 
							{
								# 'name': picking.origin +':'+ (picking.name).strip(), #move_line.name,
								'name': move_line.name,
								'picking_id': picking.id,
								'origin': origin,
								'uos_id': move_line.product_uos.id or move_line.product_uom.id,
								'product_id': move_line.product_id.id,
								'price_unit': price_unit,
								'discount': discount,
								'quantity': move_line.product_qty,
								'invoice_id': invoice_id,
								'invoice_line_tax_id': [(6, 0, tax_ids)],
								'account_analytic_id': pool_picking._get_account_analytic_invoice(cr, uid, picking, move_line),
								'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, partner_obj.property_account_position, line_account_id),
								'amount_discount':disc_amount
							}
						)
				else:
					pool_invoice_line.create(
						cr, uid, 
						{
							# 'name': picking.origin +':'+ (picking.name).strip(), #move_line.name,
							'name': move_line.name,
							'picking_id': picking.id,
							'origin': origin,
							'uos_id': move_line.product_uos.id or move_line.product_uom.id,
							'product_id': move_line.product_id.id,
							'price_unit': price_unit,
							'discount': discount,
							'quantity': move_line.product_qty,
							'invoice_id': invoice_id,
							'invoice_line_tax_id': [(6, 0, tax_ids)],
							'account_analytic_id': pool_picking._get_account_analytic_invoice(cr, uid, picking, move_line),
							'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, partner_obj.property_account_position, line_account_id),
							'amount_discount':disc_amount
						}
					)
		pool_invoice.button_compute(cr, uid, [invoice_id], context=context, set_total=False)           
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'account', "invoice_form")
		if data.type == 'in':
			action_model,action_id = pool_data.get_object_reference(cr, uid, 'account', "invoice_supplier_form")
		 
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'Merged Invoice'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'account.invoice'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = invoice_id
		return action


merge_pickings()


class account_invoice(osv.osv):
	
	_inherit = 'account.invoice'

	def unlink(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]

		id_pick=self.pool.get("stock.picking").search(cr,uid,[('invoice_id', '=' ,val.id)])
		picking =self.pool.get("stock.picking").browse(cr,uid,id_pick)

		if picking:
			for x in picking:
				self.pool.get("stock.picking").write(cr, uid, [x.id], {'invoice_state': '2binvoiced'})

		return super(account_invoice, self).unlink(cr, uid, ids, context=context)

account_invoice()