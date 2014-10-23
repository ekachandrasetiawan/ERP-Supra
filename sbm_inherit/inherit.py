from datetime import datetime
from stock import stock
import math
import time
import netsvc
from osv import osv, fields
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.account import account_invoice
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
	_name='purchase.order'
	



	def _get_total_discount(self, cr, uid, ids, name, arg, context=None):
		dis = {}
		

		discount=0
		totaldiscount=0 
		amount_untaxed=0
		
		orders= self.browse(cr, uid, ids, context=context)
		for order in orders:
			dis[order.id]=order.amount_bruto-order.amount_untaxed
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


#For Bank Statment Size

class account_bank_statement_line(osv.osv):
	_name = "account.bank.statement.line"
	_inherit = "account.bank.statement.line"
	_columns={
		'ref': fields.text('Reference'),
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
	def actionFakturPrint(self,cr,uid,ids,context=None):
		# pick = self.browse(cr,uid,ids)
		# print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>CALLLLEDDD"
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"account-invoice/print&id="+str(ids[0])
		print "<<<<<<<<<<<<<<<<<<<<<<<<<<<",urlTo
		return {
			'type': 'ir.actions.act_url',
			'target': 'new',
			'url': urlTo,
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
				# if not res[inv.id]:
				# 	res[inv.id]=0

				# if line.account_id.id == acc_discount_id:
				# 	res[inv.id]+=line.price_subtotal
				# else:
				# 	res[inv.id]+=0
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
	}

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
		'stock_available': fields.function(_get_stock, fnct_search=_stock_search, type="float", string="Available", select=True, help="Current quantity of products with this Serial Number available in company warehouses", digits_compute=dp.get_precision('Product Unit of Measure')),
    }
    _defaults = {
        'quantity': 1.0,
    }
    def _dumy_getStock(self,cr,uid,ids,context=None):
    	return 1000
    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False,
                        loc_id=False, product_id=False, uom_id=False,context=None):
    	if prodlot_id == False:
    		return False
    	else:
	    	hasil=self.pool.get('stock.production.lot').browse(cr,uid,[prodlot_id])[0]
	    	return {'value':{'desc':hasil.desc,'stock_available':self.pool.get('stock.move.split.lines')._dumy_getStock(cr,uid,ids,context)}}
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
		

	# def submit(self,cr,uid,ids,context=None):

# class stock_picking(osv.osv):
# 	_inherit = "stock.picking"
# 	_name = "stock.picking"
# 	def do_partial(self, cr, uid, ids, partial_datas, context=None):
# 		""" Makes partial picking and moves done.
# 		@param partial_datas : Dictionary containing details of partial picking
# 			like partner_id, partner_id, delivery_date,
# 				delivery moves with product_id, product_qty, uom
# 		@return: Dictionary of values
# 		"""
# 		if context is None:
# 			context = {}
# 		else:
# 			context = dict(context)
# 		res = {}
# 		move_obj = self.pool.get('stock.move')
# 		product_obj = self.pool.get('product.product')
# 		currency_obj = self.pool.get('res.currency')
# 		uom_obj = self.pool.get('product.uom')
# 		sequence_obj = self.pool.get('ir.sequence')
# 		wf_service = netsvc.LocalService("workflow")
# 		for pick in self.browse(cr, uid, ids, context=context):
# 			new_picking = None
# 			complete, too_many, too_few = [], [], []
# 			move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
# 			for move in pick.move_lines:
# 				if move.state in ('done', 'cancel'):
# 					continue
# 				partial_data = partial_datas.get('move%s'%(move.id), {})
# 				product_qty = partial_data.get('product_qty',0.0)
# 				move_product_qty[move.id] = product_qty
# 				product_uom = partial_data.get('product_uom',False)
# 				product_price = partial_data.get('product_price',0.0)
# 				product_currency = partial_data.get('product_currency',False)
# 				prodlot_id = partial_data.get('prodlot_id')
# 				prodlot_ids[move.id] = prodlot_id
# 				product_uoms[move.id] = product_uom
# 				partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
# 				if move.product_qty == partial_qty[move.id]:
# 					complete.append(move)
# 				elif move.product_qty > partial_qty[move.id]:
# 					too_few.append(move)
# 				else:
# 					too_many.append(move)

# 				# Average price computation
# 				if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
# 					product = product_obj.browse(cr, uid, move.product_id.id)
# 					move_currency_id = move.company_id.currency_id.id
# 					context['currency_id'] = move_currency_id
# 					qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

# 					if product.id not in product_avail:
# 						# keep track of stock on hand including processed lines not yet marked as done
# 						product_avail[product.id] = product.qty_available

# 					if qty > 0:
# 						new_price = currency_obj.compute(cr, uid, product_currency,
# 								move_currency_id, product_price, round=False)
# 						new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
# 								product.uom_id.id)
# 						if product_avail[product.id] <= 0:
# 							product_avail[product.id] = 0
# 							new_std_price = new_price
# 						else:
# 							# Get the standard price
# 							amount_unit = product.price_get('standard_price', context=context)[product.id]
# 							new_std_price = ((amount_unit * product_avail[product.id])\
# 								+ (new_price * qty))/(product_avail[product.id] + qty)
# 						# Write the field according to price type field
# 						product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

# 						# Record the values that were chosen in the wizard, so they can be
# 						# used for inventory valuation if real-time valuation is enabled.
# 						move_obj.write(cr, uid, [move.id],
# 								{'price_unit': product_price,
# 								 'price_currency_id': product_currency})

# 						product_avail[product.id] += qty



# 			for move in too_few:
# 				product_qty = move_product_qty[move.id]
# 				if not new_picking:
# 					new_picking_name = pick.name
# 					self.write(cr, uid, [pick.id], 
# 							   {'name': sequence_obj.get(cr, uid,
# 											'stock.picking.%s'%(pick.type)),
# 							   })
# 					new_picking = self.copy(cr, uid, pick.id,
# 							{
# 								'name': new_picking_name,
# 								'move_lines' : [],
# 								'state':'draft',
# 							})
# 				if product_qty != 0:
# 					defaults = {
# 							'product_qty' : product_qty,
# 							'product_uos_qty': product_qty, #TODO: put correct uos_qty
# 							'picking_id' : new_picking,
# 							'state': 'assigned',
# 							'move_dest_id': False,
# 							'price_unit': move.price_unit,
# 							'product_uom': product_uoms[move.id]
# 					}
# 					prodlot_id = prodlot_ids[move.id]
# 					if prodlot_id:
# 						defaults.update(prodlot_id=prodlot_id)
# 					move_obj.copy(cr, uid, move.id, defaults)
# 				move_obj.write(cr, uid, [move.id],
# 						{
# 							'product_qty': move.product_qty - partial_qty[move.id],
# 							'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
# 							'prodlot_id': False,
# 							'tracking_id': False,
# 						})

# 			if new_picking:
# 				move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
# 			for move in complete:
# 				defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
# 				if prodlot_ids.get(move.id):
# 					defaults.update({'prodlot_id': prodlot_ids[move.id]})
# 				move_obj.write(cr, uid, [move.id], defaults)
# 			for move in too_many:
# 				product_qty = move_product_qty[move.id]
# 				defaults = {
# 					'product_qty' : product_qty,
# 					'product_uos_qty': product_qty, #TODO: put correct uos_qty
# 					'product_uom': product_uoms[move.id]
# 				}
# 				prodlot_id = prodlot_ids.get(move.id)
# 				if prodlot_ids.get(move.id):
# 					defaults.update(prodlot_id=prodlot_id)
# 				if new_picking:
# 					defaults.update(picking_id=new_picking)
# 				move_obj.write(cr, uid, [move.id], defaults)

# 			# At first we confirm the new picking (if necessary)
# 			if new_picking:
# 				wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
# 				# Then we finish the good picking
# 				self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
# 				self.action_move(cr, uid, [new_picking], context=context)
# 				wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
# 				wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
# 				delivered_pack_id = pick.id
# 				back_order_name = self.browse(cr, uid, delivered_pack_id, context=context).name
# 				self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (back_order_name), context=context)
# 			else:
# 				self.action_move(cr, uid, [pick.id], context=context)
# 				wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
# 				delivered_pack_id = pick.id

# 			delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
# 			old_picking = self.browse(cr,uid,new_picking)
# 			# res[pick.id] = {'delivered_picking': delivered_pack.id or False}
# 			res[old_picking.id] = {'delivered_picking': old_picking.id or False}
# 			print res,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"

# 		return False
