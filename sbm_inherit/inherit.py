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
class stock_picking(osv.osv):
	def open_full_record(self, cr, uid, ids, context=None):
		data= self.browse(cr, uid, ids, context=context)
		# print "======================================",data[0].backorder_id
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'action_id':588,
			'view_id':960,
			'res_model': self._name,
			'res_id': data[0].backorder_id.id,
			'target': 'current',
			'context': context,  # May want to modify depending on the source/destination
		}
	_inherit = 'stock.picking'
	_columns = {
		'cust_doc_ref' : fields.char('External Doc Ref',200,required=False,store=True),
		'lbm_no' : fields.char('LBM No',200,required=False,store=True),
	}


	
stock_picking()

class stock_picking_in(osv.osv):
	_inherit = 'stock.picking.in'
	_table="stock_picking"
	_columns = {
		'cust_doc_ref' : fields.char('External Doc Ref',200,required=False,store=True),
		'lbm_no' : fields.char('LBM No',200,required=False,store=True),
	}
	# def __init__(self, pool, cr):
	# 	super(StockPickingIn, self).__init__(pool, cr)
	# 	self._columns['cust_doc_ref'] = self.pool['stock.picking']._columns['cust_doc_ref']

	def action_process(self, cr, uid, ids, context=None):
		# picking_obj = self.browse(cr, uid, ids, context=context)
		picking_obj=self.pool.get('stock.picking.in').browse(cr, uid, ids)
		# print "pickingobject.custdocref ====== > ",str(picking_obj[0].cust_doc_ref)

		# if(picking_obj[0].backorder_id == False):
		# 	raise osv.except_osv(('Warning !!!'),('Please Change Other Doc No Ref Field..!!'))
		# el
		# print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>POBJ",picking_obj[0].backorder_id.name
		# print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<docRef",picking_obj[0].cust_doc_ref
		# if picking_obj[0].backorder_id.name not is None:
			# if picking is not partial that not have backorder
			# check if cust doc is same with back order cust doc ref

		if(picking_obj[0].cust_doc_ref is None or picking_obj[0].cust_doc_ref is False):
			raise osv.except_osv(('Warning !!!'), ('Plase Fill "External Doc Ref" Field!!'))
		else:
			if picking_obj[0].backorder_id.cust_doc_ref == picking_obj[0].cust_doc_ref:
				raise osv.except_osv(('Warning !!!'), ('External Doc Ref can\'t same with backorder External Doc Ref, Please Change External Doc Reference Field !'))
			else:
				return super(stock_picking_in, self).action_process(cr, uid, ids, context)
				
	
stock_picking_in()


# INHERIT FOR
# 1. TOTAL DISCOUNT
# 2. DESCRIPTION LINE MANY2ONE RELATED
class PurchaseOrder(osv.osv):
	_inherit='purchase.order'
	# _columns={
	# 	'bank_statement_lines':fields.one2many('account.bank.statement.line','po_id',string="First Payments"),
	# }


	def _get_total_discount(self, cr, uid, ids, name, arg, context=None):
		dis = {}
		

		discount=0
		totaldiscount=0
		
		orders= self.browse(cr, uid, ids, context=context)
		for order in orders:
			dis[order.id]=order.amount_bruto-order.amount_untaxed
		print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",dis
		return dis


	def _get_amount_bruto(self,cr,uid,ids,name,arg,context=None):
		orders= self.browse(cr, uid, ids, context=context)
		total = {}
		for order in orders:
			total[order.id] = 0
			for line in order.order_line:
				subtotal = line.product_qty*line.price_unit
				total[order.id] = total[order.id]+subtotal

		return total

	def _default_total_discount(self,cr,uid,context=None):
		res = 0
		return res

	_columns = {
		'total_discount': fields.function(
			_get_total_discount,string="Total Discount",type="float",store=False
		),
		'amount_bruto':fields.function(
			_get_amount_bruto,
			string="SubTotal",
			type="float",
			store=False
		),
		'description': fields.related('order_line','name', type='text', string='Description',store=False),
	}
	_defaults = {
		'total_discount': _default_total_discount
	}
PurchaseOrder()

class PurchaseOrderLine(osv.osv):
	_inherit='purchase.order.line'
	# _name='purchase.order.line'

class SpecialWorkOrder(osv.osv):
	_inherit = 'perintah.kerja'
	name = 'special.work.order'
	_columns = {
		'special': fields.boolean('Special WO'),
		'pr_id':fields.many2one('pr',string='PR',required=False, domain=[('state','=','confirm')]),
	}
	
	def pr_change(self, cr, uid, ids, pr):
		if pr:
			res = {}; line = []
			obj_spr = self.pool.get('pr').browse(cr, uid, pr)
			res['kontrak'] = obj_spr.ref_pr
			res['partner_id'] = obj_spr.customer_id.id
			res['kontrakdate'] = obj_spr.tanggal
			res['workshop'] = obj_spr.location
			return  {'value': res}
		return True


SpecialWorkOrder()


class SpecialDN(osv.osv):
	_inherit = 'delivery.note'
	_columns = {
		'special': fields.boolean('Special WO'),
		# 'work_order_id': fields.many2one('perintah.kerja',string="SPK",store=True,required=False,domain=[('special','=',True)])
		'work_order_id': fields.many2one('perintah.kerja',string="SPK",store=True,required=False),
		# 'pb_id' : fields.many2one('purchase.requisition.subcont','No PB',readonly=True),
		'work_order_in': fields.many2one('perintah.kerja.internal',string="SPK Internal")
	}

	def spk_change(self, cr, uid, ids, spk):
		if spk:
			res = {}; line = []
			obj_spk = self.pool.get('perintah.kerja').browse(cr, uid, spk)
			res['poc'] = obj_spk.kontrak
			res['partner_id'] = obj_spk.partner_id.id
			res['partner_shipping_id'] = obj_spk.partner_id.id
			return  {'value': res}
		return True

	def spk_change_internal(self, cr, uid, ids, spk):
		if spk:
			res = {}; line = []
			obj_spk = self.pool.get('perintah.kerja.internal').browse(cr, uid, spk)
			res['poc'] = obj_spk.kontrak
			res['partner_id'] = obj_spk.partner_id.id
			res['partner_shipping_id'] = obj_spk.partner_id.id
			return  {'value': res}
		return True


SpecialDN()

# class tesAccountInvoice(osv.osv):
# 	_inherit = 'account.invoice'
	
# 	def _getR():
# 		return "a"
	
# 	_columns={
# 		'tes':fields.function(_getR,string="Tes",store=False,required=False)
# 	}






class PurchaseOrderFullInvoice(osv.osv):
	_inherit='purchase.order'
	# def action_invoice_create(self, cr, uid, ids, context=None):
	# 	print "OVERRIDEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
	# 	return False

	# def action_invoice_create(self, cr, uid, ids, context=None):
	# 	return super(purchase_order, self).action_invoice_create(cr, uid, ids, context)

	# BUTTON FULL INVOICE APPEND disc_amount data
	def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
		# print [(6, 0, [x.id for x in order_line.taxes_id])]
		return {
			'name': order_line.name,
			'account_id': account_id,
			'price_unit': order_line.price_unit or 0.0,
			'quantity': order_line.product_qty,
			'product_id': order_line.product_id.id or False,
			'uos_id': order_line.product_uom.id or False,
			'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
			'account_analytic_id': order_line.account_analytic_id.id or False,
			# 'amount_discount':order_line.discount_nominal
		}
	def _prepare_inv_line_for_discount(self, cr, uid, account_id,discountNominal, invoiceLineTaxId, context=None):
		
		return {
			'name': "Discount",
			'account_id': account_id,
			'price_unit': discountNominal or 0.0,
			'quantity': 1,
			'invoice_line_tax_id': invoiceLineTaxId
		}
	def _makeInvoiceLine(self,cr,uid,taxesId,acc_discount_id,discountNominal,context=None):
		if context is None:
			context = {}
		journal_obj = self.pool.get('account.journal')
		inv_obj = self.pool.get('account.invoice')
		inv_line_obj = self.pool.get('account.invoice.line')

		invoiceLineTaxId = taxesId
		inv_line_discount_data = self._prepare_inv_line_for_discount(cr, uid, acc_discount_id, discountNominal, invoiceLineTaxId, context=context)
		
		return inv_line_obj.create(cr, uid, inv_line_discount_data, context=context)
		

	def action_invoice_create(self, cr, uid, ids, context=None):
		# print ">>>>>>>>>>>>>>>>>>>>>>.<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
		"""Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
		:param ids: list of ids of purchase orders.
		:return: ID of created invoice.
		:rtype: int
		"""
		if context is None:
			context = {}
		journal_obj = self.pool.get('account.journal')
		inv_obj = self.pool.get('account.invoice')
		inv_line_obj = self.pool.get('account.invoice.line')

		res = False
		uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
		for order in self.browse(cr, uid, ids, context=context):
			context.pop('force_company', None)
			if order.company_id.id != uid_company_id:
				#if the company of the document is different than the current user company, force the company in the context
				#then re-do a browse to read the property fields for the good company.
				context['force_company'] = order.company_id.id
				order = self.browse(cr, uid, order.id, context=context)
			pay_acc_id = order.partner_id.property_account_payable.id
			journal_ids = journal_obj.search(cr, uid, [('type', '=', 'purchase'), ('company_id', '=', order.company_id.id)], limit=1)
			if not journal_ids:
				raise osv.except_osv(_('Error!'),
					_('Define purchase journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))

			# generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
			inv_lines = []
			# state for check is all has vat in
			allWithPPN = True
			listInvPPN = {"vat":[],"nonVat":[]}
			for po_line in order.order_line:
				print po_line.id,"<<<<<<<<<<<<<<<<<<<<<<<"
				if not po_line.taxes_id:
					allWithPPN=False
					listInvPPN["nonVat"].append(po_line.id)
				else:
					listInvPPN["vat"].append(po_line.id)

				acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
				inv_line_data = self._prepare_inv_line(cr, uid, acc_id, po_line, context=context)
				inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
				inv_lines.append(inv_line_id)

				po_line.write({'invoice_lines': [(4, inv_line_id)]}, context=context)
				print ">>>>>>>>>>",inv_line_id,">>>>>>>>>>>>>>>>>>>>>>>>>",po_line.taxes_id

			
			# print listInvPPN
			# START AUTOMATIC CONVERT DISCOUNT TO NOMINAL
			acc_discount_id=271 #DISCOUNT PEMBELIAN
			# IF ALL LINE WITH PPN THEN WE JUST ONLY CREATE 1 INVOICE LINE
			# print order.total_discount,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
			if order.total_discount != 0.0:

				if allWithPPN:
					invoiceLineTaxId = [(6,0,[1])]
					# inv_line_discount_data = self._prepare_inv_line_for_discount(cr, uid, acc_discount_id, (0-order.total_discount), invoiceLineTaxId, context=context)
					# inv_line_discount_id = inv_line_obj.create(cr, uid, inv_line_discount_data, context=context)
					
					inv_line_discount_id = self._makeInvoiceLine(cr,uid,invoiceLineTaxId,acc_discount_id,(0-order.total_discount))
					inv_lines.append(inv_line_discount_id)


				else:
					totalDiscount2 = {"vat":0,"nonVat":0}
					# LOOP EACH LINE WITH VAT
					for discountWithVAT in self.pool.get('purchase.order.line').browse(cr,uid,listInvPPN['vat']):
						# COUNT
						totalDiscount2['vat']+= (discountWithVAT.price_unit*discountWithVAT.product_qty)-discountWithVAT.price_subtotal
					# MAKE INVOICE LINE
					totalDiscount2['vat']= 0 - totalDiscount2['vat']
					if totalDiscount2['vat']!=0:
						inv_line_discount_id = self._makeInvoiceLine(cr,uid,[(6,0,[1])],acc_discount_id,totalDiscount2['vat'])
						inv_lines.append(inv_line_discount_id)

					for discountWithoutVAT in self.pool.get('purchase.order.line').browse(cr,uid,listInvPPN['nonVat']):
						print discountWithoutVAT
						totalDiscount2['nonVat']+=(discountWithoutVAT.price_unit*discountWithoutVAT.product_qty)-discountWithoutVAT.price_subtotal

					totalDiscount2['nonVat']= 0 - totalDiscount2['nonVat']
					if totalDiscount2['nonVat'] != 0:
						inv_line_discount_id = self._makeInvoiceLine(cr,uid,[],acc_discount_id,totalDiscount2['nonVat'])
						inv_lines.append(inv_line_discount_id)

				

			# print "ADDDDD DISCOUNTTTTTTTTTTTTTT>>>>>>>>>>>>>>>>>",inv_line_discount_id

			# get invoice data and create invoice
			inv_data = {
				'name': order.partner_ref or order.name,
				'reference': order.partner_ref or order.name,
				'account_id': pay_acc_id,
				'type': 'in_invoice',
				'partner_id': order.partner_id.id,
				'currency_id': order.pricelist_id.currency_id.id,
				'journal_id': len(journal_ids) and journal_ids[0] or False,
				'invoice_line': [(6, 0, inv_lines)],
				'origin': order.name,
				'fiscal_position': order.fiscal_position.id or False,
				'payment_term': order.payment_term_id.id or False,
				'company_id': order.company_id.id,
			}
			inv_id = inv_obj.create(cr, uid, inv_data, context=context)

			# compute the invoice
			inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)

			# Link this new invoice to related purchase order
			order.write({'invoice_ids': [(4, inv_id)]}, context=context)
			res = inv_id
		return res
		# return  False

# END FOR FINANCE DISCOUNT AMOUNT


# class MergePickings(osv.osv):
# 	_inherit='merge.pickings'



# FOR FINANCE DISCOUNT AMOUNT
class account_invoice_line(osv.osv):
	def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		# print 'OVERIDEDDDDDD==================================>>>>>>>>'
		# TEST AJA lagi
		res = {}
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		for line in self.browse(cr, uid, ids):
			if line.discount!=0.0:
				# print 'DISCOUNT %'
				price = line.price_unit * (1-(line.discount or 0.0)/100.0)
			elif line.amount_discount!=0.0:
				# print "DISCOUNT AMOUNT"
				price = line.price_unit - (line.amount_discount/line.quantity)
			else:
				price = line.price_unit
			
			
			taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			res[line.id] = taxes['total']
			if line.invoice_id:
				cur = line.invoice_id.currency_id
				res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
		return res


	_name='account.invoice.line'
	_inherit='account.invoice.line'
	_columns={
		'amount_discount':fields.float('Amount Discount',required=False),
		'price_subtotal': fields.function(_amount_line, string='Amount', type="float",digits_compute= dp.get_precision('Account'), store=True),
	}

# INHERIT CLASS FOR ACCOUNT BANK STATEMENT LINE
# For Bank Statment Size
class account_bank_statement_line(osv.osv):
	_name = "account.bank.statement.line"
	_inherit = "account.bank.statement.line"
	_columns={
		'ref': fields.text('Reference'),
		'po_id':fields.many2one('purchase.order',string="PO"),
	}

class wizard_suplier_first_payment(osv.osv_memory):
	_name = 'wizard.supplier.first.payment'
	_description = 'Supplier DP with Bank Statement'
	_columns = {
		'name':fields.char('Reference',required=True),
		'po_id':fields.many2one('purchase.order','PO No',required=True),
		'journal_id': fields.many2one('account.journal', 'Journal', required=True,domain=[('type','=','bank')]),
		'payment_date':fields.date('Date',required=True),
		'period_id': fields.many2one('account.period', 'Period', required=True),
		'obi':fields.char('OBI',required=True),
		'ref':fields.text('Reference'),
		'voucher_code':fields.char('No Cek/Giro'),
		'method':fields.selection([('cash','Cash'),('cek','Cheques'),('giro','Giro'),('transfer','Transfer')],string="Payment Method",required=True),
		'rate':fields.float('BI Rate'),
		'partner_id': fields.many2one('res.partner',required=True,string="Supplier",domain=[('supplier','=',True)]),
		'account_id':fields.many2one('account.account',string="Account",required=True),
		'amount':fields.float(string="Amount",required=True),
	}
	_defaults={
		'account_id':69
	}

	def check(self,cr,uid,values,context=None):
		val = self.browse(cr, uid, values)[0]
		# print val,"<<<<<<<<<<<<<<<<<<<<<<<<<VAL"
		# print wVal
		# print ids

		# print 111111
		acc_bs = self.pool.get('account.bank.statement')
		acc_bs_line = self.pool.get('account.bank.statement.line')

		po = self.pool.get('purchase.order')

		acc1 = acc_bs.create(cr,uid,{
			'name' : val.name,
			'date' : val.payment_date,
			'journal_id' : val.journal_id.id,
			
			'period_id' : val.period_id.id
		},context)
		amount = val.amount
		if amount > 0:
			amount = -(val.amount)

		acc11 = acc_bs_line.create(cr,uid,{
			'date' : val.payment_date,
			'name' : val.obi,
			'ref' : val.ref,
			'code_voucher' : val.voucher_code,
			'method' : val.method,
			'kurs' : val.rate,
			'partner_id' : val.partner_id.id,
			'type':'supplier',
			'sequence':0,
			'account_id' : val.account_id.id,
			'amount' : amount,
			'po_id' : val.po_id.id,
			'statement_id':acc1
		})
		# print acc1,"*********************"
		# print acc11,"********************"
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_bank_statement_form')
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'account.bank.statement.form',
			'res_model': 'account.bank.statement',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'res_id':acc1,
			'domain': "[('id','=',"+str(acc1)+")]",
		}
		
	def on_change_po_id(self,cr,uid,ids,po_id):
		res = {}
		po_obj = self.pool.get('purchase.order')
		browse = po_obj.browse(cr,uid,po_id)
		

		return {
			'value':{
				'partner_id':browse.partner_id.id
			}
		}
	

class account_invoice(osv.osv):
	def actionTest(self,cr,uid,ids,context=None):
		# pick = self.browse(cr,uid,ids)
		# print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>CALLLLEDDD"
		return {

			'type': 'ir.actions.act_url',
			'target': 'new',
			'url': 'http://www.google.com',
			
		}
	def actionPrintCustInv(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"account-invoice/print-invoice&id="+str(ids[0])
		
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'account.invoice.print.faktur',
			'params': {
				'redir'	: urlTo
			},
		}
	def actionPrintFaktur(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"account-invoice/print&id="+str(ids[0])
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'account.invoice.print.faktur',
			'params': {
				# 'id'	: ids[0],
				'redir'	: urlTo
			},
		}


	def _get_total_discount(self,cr,uid,ids,name,arg,context=None):
		# get total discount from line
		acc_discount_id=271
		invoices = self.pool.get('account.invoice')
		# line = self.pool.get('account.invoice.line').search(cr, uid, [('account_id', '=', acc_discount_id)])
		

		
		res = {}

		discount=0
		totaldiscount=0 
		amount_untaxed=0
		
		invoices= self.browse(cr, uid, ids, context=context)
		for inv in invoices:
			res[inv.id]=0
			for line in inv.invoice_line:
				if line.account_id.id==acc_discount_id:
					res[inv.id]+=line.price_subtotal

		return res


	_name='account.invoice'
	_inherit='account.invoice'
	_columns={
		'total_discount':fields.function(_get_total_discount,string='Total Discount',required=False,store=False),
	}


class account_invoice_tax(osv.osv):
	def compute(self, cr, uid, invoice_id, context=None):
		# print ">?>>>>>>>>>>>>>>>>>COMPUTEEEEE<<<<<<<<<<<<<<<<<<<<<<<<<<"
		tax_grouped = {}
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
		cur = inv.currency_id
		company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
		for line in inv.invoice_line:
			if line.discount!=0.0:
				# print 'DISCOUNT %'
				price = line.price_unit * (1-(line.discount or 0.0)/100.0)
			elif line.amount_discount!=0.0:
				# print "DISCOUNT AMOUNT"
				price = line.price_unit - (line.amount_discount/line.quantity)
			else:
				price = line.price_unit
			for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, line.product_id, inv.partner_id)['taxes']:
				val={}
				val['invoice_id'] = inv.id
				val['name'] = tax['name']
				val['amount'] = tax['amount']
				val['manual'] = False
				val['sequence'] = tax['sequence']
				val['base'] = cur_obj.round(cr, uid, cur, tax['price_unit'] * line['quantity'])

				if inv.type in ('out_invoice','in_invoice'):
					val['base_code_id'] = tax['base_code_id']
					val['tax_code_id'] = tax['tax_code_id']
					val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
					val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
					val['account_id'] = tax['account_collected_id'] or line.account_id.id
					val['account_analytic_id'] = tax['account_analytic_collected_id']
				else:
					val['base_code_id'] = tax['ref_base_code_id']
					val['tax_code_id'] = tax['ref_tax_code_id']
					val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
					val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
					val['account_id'] = tax['account_paid_id'] or line.account_id.id
					val['account_analytic_id'] = tax['account_analytic_paid_id']

				key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
				if not key in tax_grouped:
					tax_grouped[key] = val
				else:
					tax_grouped[key]['amount'] += val['amount']
					tax_grouped[key]['base'] += val['base']
					tax_grouped[key]['base_amount'] += val['base_amount']
					tax_grouped[key]['tax_amount'] += val['tax_amount']

		for t in tax_grouped.values():
			t['base'] = cur_obj.round(cr, uid, cur, t['base'])
			t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
			t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
			t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
		return tax_grouped

	_name='account.invoice.tax'
	_inherit='account.invoice.tax'

class SaleOrderLine(osv.osv):
	_name = 'sale.order.line'
	_inherit = 'sale.order.line'
	_columns = {
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True, required=True),
	}
	_order = 'sequence ASC'
SaleOrderLine()

class AccountBankStatement(osv.osv):
	def _getSubTotal(self, cr, uid, ids, name, arg, context=None):
		res = {}

		
		
		accounts= self.browse(cr, uid, ids, context=context)
		for account in accounts:
			# dis[order.id]=order.amount_bruto-order.amount_untaxed
			res[account.id] = 0
			# print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>..'
			for line in account.line_ids:
				res[account.id] += line.amount
				# print "<<<<<<<<<<<<<",line.amount
		return res

	_name = 'account.bank.statement'
	_inherit = 'account.bank.statement'
	_columns = {
		'subtotal':fields.function(_getSubTotal,string='Total',required=False,store=False),
	}

# class OrderPreparation(osv.osv):
# 	_inherit = 'order.preparation'
# 	_name = 'order.preparation'
# 	

class DeliveryNote(osv.osv):
	
	_description = 'Delivery Note'
	_name = 'delivery.note'
	_inherit = ['delivery.note','mail.thread']
	_track = {
		'partner_shipping_id':{

		},
		'delivery_date':{

		}
	}

class SerialNumber(osv.osv):
	_description = 'Serial Number'
	_name = 'stock.production.lot'
	_inherit= 'stock.production.lot'
	_columns = {
		'desc':fields.text('Description'),
		'exp_date':fields.date('Exp Date'),
	}

class split_in_production_lot(osv.osv_memory):
	_name = "stock.move.split"
	_inherit = "stock.move.split"
	_description = "Stock move Split"

	def split_lot(self, cr, uid, ids, context=None):
		""" To split a lot"""
		if context is None:
			context = {}
		res = self.split(cr, uid, ids, context.get('active_ids'), context=context)
		return {'type': 'ir.actions.act_window_close'}

	def split(self, cr, uid, ids, move_ids, context=None):
		""" To split stock moves into serial numbers

		:param move_ids: the ID or list of IDs of stock move we want to split
		"""
		if context is None:
			context = {}
		assert context.get('active_model') == 'stock.move',\
			 'Incorrect use of the stock move split wizard'
		inventory_id = context.get('inventory_id', False)
		prodlot_obj = self.pool.get('stock.production.lot')
		inventory_obj = self.pool.get('stock.inventory')
		move_obj = self.pool.get('stock.move')
		new_move = []
		for data in self.browse(cr, uid, ids, context=context):
			for move in move_obj.browse(cr, uid, move_ids, context=context):
				move_qty = move.product_qty
				quantity_rest = move.product_qty
				uos_qty_rest = move.product_uos_qty
				new_move = []
				if data.use_exist:
					lines = [l for l in data.line_exist_ids if l]
				else:
					lines = [l for l in data.line_ids if l]
				total_move_qty = 0.0
				for line in lines:
					quantity = line.quantity
					total_move_qty += quantity
					if total_move_qty > move_qty:
						raise osv.except_osv(_('Processing Error!'), _('Serial number quantity %d of %s is larger than available quantity (%d)!') \
								% (total_move_qty, move.product_id.name, move_qty))
					if quantity <= 0 or move_qty == 0:
						continue
					quantity_rest -= quantity
					uos_qty = quantity / move_qty * move.product_uos_qty
					uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
					if quantity_rest < 0:
						quantity_rest = quantity
						self.pool.get('stock.move').log(cr, uid, move.id, _('Unable to assign all lots to this move!'))
						return False
					default_val = {
						'product_qty': quantity,
						'product_uos_qty': uos_qty,
						'state': move.state
					}
					if quantity_rest > 0:
						current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
						if inventory_id and current_move:
							inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
						new_move.append(current_move)

					if quantity_rest == 0:
						current_move = move.id
					prodlot_id = False
					if data.use_exist:
						prodlot_id = line.prodlot_id.id
						desc = line.prodlot_id.desc
						move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'name' : desc, 'state':move.state})
					if not prodlot_id:
						prodlot_id = prodlot_obj.create(cr, uid, {
							'name': line.name,
							'desc':line.desc,
							'exp_date':line.exp_date,
							'product_id': move.product_id.id},
						context=context)

						move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'state':move.state})

					move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'state':move.state})

					update_val = {}
					if quantity_rest > 0:
						update_val['product_qty'] = quantity_rest
						update_val['product_uos_qty'] = uos_qty_rest
						update_val['state'] = move.state
						move_obj.write(cr, uid, [move.id], update_val)

		return new_move

split_in_production_lot()


class stock_move_split_lines_exist(osv.osv_memory):
	_name = "stock.move.split.lines"
	_inherit = "stock.move.split.lines"
	_description = "Stock move Split lines"


	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		reads = self.read(cr, uid, ids, ['name', 'prefix', 'ref'], context)
		res = []
		for record in reads:
			name = record['name']
			prefix = record['prefix']
			if prefix:
				name = prefix + '/' + name
			if record['ref']:
				name = '%s [%s]' % (name, record['ref'])
			res.append((record['id'], name))
		return res

	def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
		args = args or []
		ids = []
		if name:
			ids = self.search(cr, uid, [('prefix', '=', name)] + args, limit=limit, context=context)
			if not ids:
				ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
		else:
			ids = self.search(cr, uid, args, limit=limit, context=context)
		return self.name_get(cr, uid, ids, context)
		
	def _get_stock(self, cr, uid, ids, context=None):
		""" Gets stock of products for locations
		@return: Dictionary of values
		"""
		if context is None:
			context = {}
		if 'location_id' not in context:
			locations = self.pool.get('stock.location').search(cr, uid, [('usage', '=', 'internal')], context=context)
		else:
			locations = context['location_id'] and [context['location_id']] or []

		if isinstance(ids, (int, long)):
			ids = [ids]

		res = {}.fromkeys(ids, 0.0)
		if locations:
			cr.execute('''select
					prodlot_id,
					sum(qty)
				from
					stock_report_prodlots
				where
					location_id IN %s and prodlot_id IN %s group by prodlot_id''',(tuple(locations),tuple(ids),))
			res.update(dict(cr.fetchall()))

		return 100

	def _stock_search(self, cr, uid, obj, name, args, context=None):
		""" Searches Ids of products
		@return: Ids of locations
		"""
		locations = self.pool.get('stock.location').search(cr, uid, [('usage', '=', 'internal')])
		cr.execute('''select
				prodlot_id,
				sum(qty)
			from
				stock_report_prodlots
			where
				location_id IN %s group by prodlot_id
			having  sum(qty) '''+ str(args[0][1]) + str(args[0][2]),(tuple(locations),))
		res = cr.fetchall()
		ids = [('id', 'in', map(lambda x: x[0], res))]
		return ids

	_columns = {
		'name': fields.char('Serial Number', size=64),
		'quantity': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
		'wizard_id': fields.many2one('stock.move.split', 'Parent Wizard'),
		'wizard_exist_id': fields.many2one('stock.move.split', 'Parent Wizard (for existing lines)'),
		'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number'),
		'desc':fields.text('Description'),
		'exp_date':fields.date('Exp Date'),
		'stock_available': fields.float('Stock Available'),
	}
	_defaults = {
		'quantity': 0.0,
	}
	def _dumy_getStock(self,cr,uid,ids,prodlot_id,context=None):
		stock = 10
		return stock
	def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False,
						loc_id=False, product_id=False, uom_id=False,context=None):
		if prodlot_id == False:
			return False
		else:
			# print '=======================PROUDCT QTY=============',product_qty
			hasil=self.pool.get('stock.production.lot').browse(cr,uid,[prodlot_id])[0]

			if product_qty > hasil.stock_available:
				raise openerp.exceptions.Warning('Stock Available Tidak Mencukupi')
				return {'value':{'quantity':0}}

			return {'value':{'desc':hasil.desc,'exp_date':hasil.exp_date,'stock_available':hasil.stock_available}}
		return self.pool.get('stock.move').onchange_lot_id(cr, uid, [], prodlot_id, product_qty,
						loc_id, product_id, uom_id, context)


# ---------------------------------------------
# OVERRIDE INTERMAL MOVE REDIRECT ON DO PARTIAL
# ---------------------------------------------
class stock_picking(osv.osv):
	_inherit = "stock.picking"
	_name = "stock.picking"
	def do_partial(self, cr, uid, ids, partial_datas, context=None):
		pick = self.browse(cr,uid,ids)
		# print pick[0].name;
		if pick[0].name==False:
			# GENERATE NUMBER
			self.generateSeq(cr,uid,ids,context)

		return super(stock_picking,self).do_partial(cr,uid,ids,partial_datas,context)
	def generateSeq(self,cr,uid,ids,context=None):
		pick = self.browse(cr,uid,ids)

		if pick[0].name == False:
			newPickName = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking')
			return self.write(cr,uid,ids,{'name':newPickName})
		else:
			raise osv.except_osv(('Error !!!'), ('Can\'t Update Squence'))
			return False


class stock_move(osv.osv):
	
	_inherit = 'stock.move'
	_order = 'no ASC'


class bom(osv.osv):
	def checkUniqueByProduct(self,cr,uid,prod_id):
		objs = self.search(cr,uid,[('product_id', '=', prod_id)])
		return objs

	def create(self,cr,uid,vals,context=None):
		
		if self.checkUniqueByProduct(cr,uid,vals.get('product_id')):
			res = False
			raise osv.except_osv(('Error !!!'), ('Can\'t Create new BOM, BOM has been Exist!!!'))
		else:
			res = super(bom,self).create(cr,uid,vals,context)
		return res
	_inherit='mrp.bom'

class account_move_line(osv.osv):
	_inherit = "account.move.line"
	_columns={
		'ref': fields.related('move_id', 'ref', string='Reference', type='text', store=True),
		'name': fields.char('Name', required=True),
	}

class PurchaseOrderWithDP(osv.osv):
	_inherit = 'purchase.order'
	_columns = {
		'bank_statement_lines':fields.one2many('account.bank.statement.line','po_id',string="First Payments"),
	}

class AccountVoucher(osv.osv):
	_inherit = 'account.voucher'


#Module Cancel Item in Purchase Order

class ClassName(osv.osv):
	
	def action_cancel_item(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_inherit', 'wizard_po_cancel_item_form')

		print "<<<<<<<<<<<<<<<<<<<<",view_id

		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'wizard_po_cancel_item_form',
			'res_model': 'wizard.po.cancel.item',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}
	_inherit = 'purchase.order'

class WizardPOCancelItem(osv.osv_memory):

	def default_get(self, cr, uid, fields, context=None):
		print "CALLLLEDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
		if context is None: context = {}
		po_ids = context.get('active_ids', [])
		active_model = context.get('active_model')
		res = super(WizardPOCancelItem, self).default_get(cr, uid, fields, context=context)
		if not po_ids or len(po_ids) != 1:
			# Partial Picking Processing may only be done for one picking at a time
			return res
		po_id, = po_ids
		if po_id:
			res.update(po_id=po_id)
			po = self.pool.get('purchase.order').browse(cr, uid, po_id, context=context)
			linesData = []
			linesData += [self._load_po_line(cr, uid, l) for l in po.order_line if l.state not in ('done','cancel')]
			res.update(lines=linesData)
		print res,",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
		return res

	def _load_po_line(self, cr, uid, line):
		po_item = {
			'line_id'			: line.id,
			'product_id'		: line.product_id.id,
			'description'		: line.name,
			'uom'				: line.product_uom.id,
			'qty'				: line.product_qty,
			'unit_price'		: line.price_unit,
			'discount_amount'	: line.discount_nominal,
			'discount_percent'	: line.discount,
			'subtotal'			: line.price_subtotal,
		}
		
		return po_item

	def request_cancel_item(self,cr,uid,ids,context=None):
		print "CALLING request_cancel_item method"
		data = self.browse(cr,uid,ids,context)[0]

		polc = self.pool.get('purchase.order.line.cancel')
		# we need to check INVOICES
		# call po
		po = data.po_id
		inv_ids=[] #INVOICE WHERE STATE NOT DRAFT OR CANCEL
		inv_ids+= [self.pool.get('account.invoice').browse(cr,uid,invoice.id,context) for invoice in po.invoice_ids if invoice.state not in ('draft','cancel')]
		# print "INVOICESSS",inv_ids
		if len(po.order_line) == len(data.lines):
			raise osv.except_osv(('Error !!!'),('Tidak diperbolehkan mencancel semua item..!!Silahkan mengcancel PO!'))
		newIds = []
		for line in data.lines:
			cancelItems = {
				'po_id':po.id,
				'po_line_id':line.line_id.id,
				'product_id':line.product_id.id,
				'description':line.description,
				'qty':line.qty,
				'uom':line.uom.id,
				'unit_price':line.unit_price,
				'discount_amount':line.discount_amount,
				'discount_percent':line.discount_percent,
				'subtotal':line.subtotal,
				'state':'draft',
				'note':data.note,
			}
			# make sure po line id is unique
			check = self.pool.get('purchase.order.line.cancel').search(cr,uid,[('po_line_id','=',line.line_id.id)])
			if check:
				raise osv.except_osv(('Error !!!'),('TIdak bisa mencancel item "',str(line.product_id.name),'"..!!'))
			newIds+=[polc.create(cr,uid,cancelItems,context)]
			print newIds,"------------------------------------------"
		# print "NEW IDS ",newIds

		# redir
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_inherit', 'view_po_line_cancel_tree')

		return {
			'view_mode': 'tree',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'view_po_line_cancel_tree',
			'res_model': 'purchase.order.line.cancel',
			'type': 'ir.actions.act_window',
			'target': 'current',
			# 'domain': "[('id','in',"+newIds+")]",
			'domain': [('id','in',newIds)]
		}



	_name="wizard.po.cancel.item"
	_description="Wizard Cancel Item On P.O"
	_columns = {
		'po_id':fields.many2one('purchase.order',string="Purchase Order",required=True),
		'lines':fields.one2many('wizard.po.cancel.item.line','w_id',string="Lines"),
		'note':fields.text('Note',required=True,help="Reason why item(s) want to be cancel"),
	}
	_rec_name="po_id"


class WizardPOCancelItemLine(osv.osv_memory):
	_name="wizard.po.cancel.item.line"
	_description="Line Wizard Cancel Item On P.O"
	_columns={
		'w_id':fields.many2one('wizard.po.cancel.item',string="Wizard",required=True,ondelete='CASCADE',onupdate='CASCADE'),
		'line_id':fields.many2one('purchase.order.line','Item Line',required=True),
		'product_id':fields.many2one('product.product',string="Product",required=True),
		'description':fields.text('Desc'),
		'qty':fields.float('Qty',required=True),
		'uom':fields.many2one('product.uom',string="Unit of Measure",required=True),
		'unit_price':fields.float('Unit Price'),
		'discount_amount':fields.float('Discount (Amount)'),
		'discount_percent':fields.float('Discount (Percentage)'),
		'subtotal':fields.float('Subtotal'),
	}
	_rec_name = 'w_id'

class PurchaseOrderLineCancel(osv.osv):
	def confirm_cancel(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		idsToConfirm = context['active_ids']

		# set state to approved
		self.write(cr,uid,idsToConfirm,{'state':'approved','approved_by':uid});
		lineToCancel = []
		poToUpdate = []
		cancel_notes = ""
		for cancelItem in self.browse(cr,uid,idsToConfirm,context):
			line = self.pool.get('purchase.order.line').browse(cr,uid,cancelItem.po_line_id,context)
			# print line.name
			lineToCancel+=[line.id]
			poToUpdate+=[line.order_id]
			cancelNotes = cancelItem.note
		print lineToCancel

		# search stock move
		moveObj = self.pool.get('stock.move')
		movesIdToUnlink = moveObj.search(cr,uid,[('purchase_line_id','in',lineToCancel)])

		self.pool.get('purchase.order.line').unlink(cr,uid,lineToCancel)
		self.pool.get('purchase.order').button_dummy(cr,uid,poToUpdate,context)
		# moveObj.unlink(cr,uid,movesIdToUnlink)
		moveObj.write(cr,uid,movesIdToUnlink,{'state':'cancel','cancel_notes':cancelNotes})



	
	_name = 'purchase.order.line.cancel'
	_description = "Purchase Order Line Cancel"
	
	_columns={
		'po_id':fields.many2one('purchase.order',string="PO No.",required=True,ondelete='CASCADE',onupdate='CASCADE'),
		'po_line_id':fields.integer("Line ID",required=True),
		'product_id':fields.many2one('product.product',string="Product",required=True),
		'description':fields.text('Desc'),
		'qty':fields.float('Qty',required=True),
		'uom':fields.many2one('product.uom',string="Unit of Measure",required=True),
		'unit_price':fields.float('Unit Price'),
		'discount_amount':fields.float('Discount (Amount)'),
		'discount_percent':fields.float('Discount (Percentage)'),
		'subtotal':fields.float('Subtotal'),
		'note':fields.text('Notes',required=True),
		'state':fields.selection([('draft','draft'),('rfa','Waiting Approval'),('approved','Approved')],string="State"),
		'approved_by':fields.many2one('res.users',string="Approved By",ondelete="CASCADE",onupdate='CASCADE'),

	}
	_rec_name = 'po_line_id'
	_default={
		'state':'draft',
	}
	_sql_constraints = [
		('unique_line_id', 'unique(po_line_id)', "Tidak bisa mencancel item yang sama lebih dari 1X!!!"),
	]

class stock_move(osv.osv):
	
	_inherit = 'stock.move'
	_columns = {
		'cancel_notes':fields.text('Cancel Notes',required=False)
	}
	
# Fixing bug min_date on picking when null it will be filled timestamp
class stock_picking(osv.osv):
	_inherit = 'stock.picking'
	_columns = {
		# 'min_date': fields.function(get_min_max_date, fnct_inv=_set_minimum_date, multi="min_max_date", store=True, type='datetime', string='Scheduled Time', select=1, help="Scheduled time for the shipment to be processed"),
		'min_date':fields.datetime(string="Delivery Date",help="Delivered Date shipment",required=False)
	}