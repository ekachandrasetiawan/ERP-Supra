import re
import math
import time
import netsvc
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta

class djp_tax_rate(osv.osv):

	_name = 'djp.tax.rate'
	_columns = {
		'start_active_on':fields.date('Start Active On',required=True),
		'active_till_on':fields.date('Active Untill ON', required=True),
		'currency_id': fields.many2one('res.currency',string="Currency",required=True,ondelete="CASCADE",onupdate="CASCADE"),
		'rate': fields.float(string="Rate",required=True,digits=(5,4)),
		'state':fields.selection([('draft','Draft'),('done','Activated'),('cancel','Canceled')]),
	}

	def action_activate(cr,uid,ids,context={}):
		res = True
		return self.write(cr,uid,ids,{'state':'done'},context=context)
	def action_cancel(cr,uid,ids,context={}):
		res = True
		return self.write(cr,uid,ids,{'state':'cancel'},context=context)

class account_invoice(osv.osv):
	def actionPrintFaktur(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"account-invoice/print-e-faktur&id="+str(ids[0])+"&uid="+str(uid)

		for browse in self.browse(cr,uid,ids):
			if browse.partner_id.npwp == '11111111111111111111':
				raise osv.except_osv(_('Error!'),_('NPWP Customer = '+browse.partner_id.npwp+'\r\nTolong Update NPWP terlebih dahulu. Jika Customer ini tidak mempunyai NPWP tolong Update NPWP menjadi 00.000.000.0-000.000'))
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.out',
			'params': {
				# 'id'	: ids[0],
				'redir'	: urlTo
			},
		}
	def _amount_all_main(self, cr, uid, ids, field_name, args, context=None):
		print "Call _amount_all_main---->>>>>>>>",field_name
		user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		res = {}
		for invoice in self.browse(cr, uid, ids, context=context):
			if invoice.currency_id.id  == user.company_id.currency_id.id:
				tax_rate = 1
			else:
				tax_rate = invoice.pajak
				# if tax_rate <=1:
				# 	raise osv.except_osv(_('Error'),('Please Define Tax Rate!'))

			res[invoice.id] = {
				'total_bruto_main':0.0,
				'amount_untaxed_main': 0.0,
				'amount_tax_main': 0.0,
				'amount_total_main': 0.0,
				# 'total_discount': 0.0,
				'total_discount_main': 0.0,
				'ppn_amount_tax_main': 0.0,

			}
			a=1
			for line in invoice.invoice_line:
				res[invoice.id]['total_bruto_main'] += line.amount_bruto_main

				res[invoice.id]['total_discount_main'] += line.amount_discount_main
				
				res[invoice.id]['amount_untaxed_main'] += line.sub_total_main
				
				res[invoice.id]['amount_tax_main'] += line.tax_amount_main

				res[invoice.id]['ppn_amount_tax_main'] += line.ppn_tax_amount_main

				
				a=a+1

			# res[invoice.id]['total_bruto_main'] = round(res[invoice.id]['total_bruto_main'],dec_precision)
			# res[invoice.id]['total_discount_main'] = round(res[invoice.id]['total_discount_main'],dec_precision)
			# res[invoice.id]['amount_untaxed_main'] = round(res[invoice.id]['amount_untaxed_main'],dec_precision)
			# res[invoice.id]['amount_tax_main'] = math.floor(res[invoice.id]['amount_tax_main'])
			# res[invoice.id]['amount_total_main'] = round((res[invoice.id]['amount_tax_main'] + res[invoice.id]['amount_untaxed_main']),dec_precision)
			# rounding with floor method
			res[invoice.id]['total_bruto_main'] = math.floor(res[invoice.id]['total_bruto_main'])
			res[invoice.id]['total_discount_main'] = math.floor(res[invoice.id]['total_discount_main'])
			res[invoice.id]['amount_untaxed_main'] = math.floor(res[invoice.id]['amount_untaxed_main'])
			res[invoice.id]['amount_tax_main'] = math.floor(res[invoice.id]['amount_tax_main'])
			res[invoice.id]['ppn_amount_tax_main'] = math.floor(res[invoice.id]['ppn_amount_tax_main'])


			res[invoice.id]['amount_total_main'] = math.floor((res[invoice.id]['amount_tax_main'] + res[invoice.id]['amount_untaxed_main']))



			# if invoice.pajak<=1.00:
			# 	for line in invoice.invoice_line:
			# 		res[invoice.id]['total_bruto_main'] += line.amount_bruto_main
			# 		res[invoice.id]['total_discount_main'] += line.amount_discount
			# 	for line in invoice.invoice_line:
			# 		res[invoice.id]['amount_untaxed_main'] += line.price_subtotal
			# 	for line in invoice.tax_line:
			# 		res[invoice.id]['amount_tax_main'] += line.amount
			# 	res[invoice.id]['amount_total_main'] = res[invoice.id]['amount_tax_main'] + res[invoice.id]['amount_untaxed_main']
			# else: 
			# 	for line in invoice.invoice_line:
			# 		# res[invoice.id]['total_discount'] += round(line.amount_discount)
			# 		res[invoice.id]['total_discount_main'] += line.amount_discount*invoice.pajak
			# 	for line in invoice.invoice_line:
			# 		res[invoice.id]['amount_untaxed_main'] += line.price_subtotal*invoice.pajak
			# 	for line in invoice.tax_line:
			# 		res[invoice.id]['amount_tax_main'] += line.amount*invoice.pajak
				
		print "RESSSSSSSSSSS AMOUNT_ALL_MAIN",res
		return res
	def _get_invoice_by_line(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('account.invoice.line').browse(cr,uid,ids,context=context):
			result[line.invoice_id.id] = True

		return result.keys()

	_inherit = "account.invoice"
	_columns = {
		'invoice_line_main': fields.one2many('account.invoice.line', 'invoice_id', 'Invoice Lines Main'),
		'total_bruto_main': fields.function(
			_amount_all_main,
			string="Total",
			store={
				'account.invoice':(lambda self, cr, uid, ids, c={}: ids, ['pajak','currency_id','invoice_line'], 93),
				'account.invoice.line': (_get_invoice_by_line,['price_unit','quantity','discount','amount_discount','invoice_line_tax_id'],93)
			},

			multi="all",
		),
		'total_discount_main': fields.function(
			_amount_all_main, 
			string='Total Discount (Main Currency)', 
			store={
				'account.invoice':(lambda self, cr, uid, ids, c={}: ids, ['pajak','currency_id','invoice_line'], 93),
				'account.invoice.line': (_get_invoice_by_line,['price_unit','quantity','discount','amount_discount','invoice_line_tax_id'],93)
			}, 
			multi="all",
		),
		'amount_untaxed_main': fields.function(
			_amount_all_main, 
			string='Subtotal (Main Currency)', 
			track_visibility='always',
			store={
				'account.invoice':(lambda self, cr, uid, ids, c={}: ids, ['pajak','currency_id','invoice_line'], 93),
				'account.invoice.line': (_get_invoice_by_line,['price_unit','quantity','discount','amount_discount','invoice_line_tax_id','tax_amount','tax_amount_main'],93)
			},
			multi="all",
		),
		'amount_tax_main': fields.function(
			_amount_all_main, 
			string='Tax (Main Currency)',
			store={
				'account.invoice':(lambda self, cr, uid, ids, c={}: ids, ['pajak','currency_id','invoice_line'], 93),
				'account.invoice.line': (_get_invoice_by_line,['price_unit','quantity','discount','amount_discount','invoice_line_tax_id','tax_amount','tax_amount_main'],93),
				# 'account.invoice.line.tax.amount': (),
			},
			multi="all",
		),

		'ppn_amount_tax_main': fields.function(
			_amount_all_main, 
			string='Tax - PPN Only(Main Currency)',
			store={
				'account.invoice':(lambda self, cr, uid, ids, c={}: ids, ['pajak','currency_id','invoice_line'], 93),
				'account.invoice.line': (_get_invoice_by_line,['price_unit','quantity','discount','amount_discount','invoice_line_tax_id','tax_amount','tax_amount_main'],93)
			},
			multi="all",
		),
		'amount_total_main': fields.function(
			_amount_all_main, 
			string='Total (Main Currency)',
			store={
				'account.invoice':(lambda self, cr, uid, ids, c={}: ids, ['pajak','currency_id','invoice_line'], 93),
				'account.invoice.line': (_get_invoice_by_line,['price_unit','quantity','discount','amount_discount','invoice_line_tax_id','tax_amount','tax_amount_main'],93)
			},
			multi="all",
		),
	}

	def _get_default_pajak(cr,uid,context={}):
		res = 1
		
		return res
	# _defaults = {
	# 	'pajak':_get_default_pajak
	# }

	def onchange_curr(cr,uid,ids,context={}):
		return False


	# def write(self,cr,uid,ids,vals,context={}):
	# 	line_obj = self.pool.get('account.invoice.line')
	# 	line_tax = self.pool.get('account.invoice.tax')
	# 	if 'pajak' in vals:
	# 		pajak=vals['pajak']
	# 		for invoice in self.browse(cr, uid, ids, context=context):
	# 			if pajak==0.0:
	# 				for line in invoice.invoice_line:
	# 					unit_price_main = round(line.price_unit)
	# 					amount_discount_main = round(line.amount_discount)
	# 					sub_total_main = round(line.price_unit*line.quantity)-amount_discount_main
						
	# 					# Update Invoice Line
	# 					line_obj.write(cr, uid, [line.id], {'unit_price_main': unit_price_main})
	# 					line_obj.write(cr, uid, [line.id], {'sub_total_main': unit_price_main})
	# 					line_obj.write(cr, uid, [line.id], {'amount_discount_main': amount_discount_main})
	# 			else:
	# 				for line in invoice.invoice_line:
	# 					unit_price_main = round(line.price_unit*pajak)
	# 					amount_discount_main = round(line.amount_discount*pajak)
	# 					sub_total_main = round((line.price_unit*line.quantity)*pajak)-amount_discount_main
						
	# 					# Update Line Invoice dikali dengan Rate Tax
	# 					line_obj.write(cr, uid, [line.id], {'unit_price_main': unit_price_main})
	# 					line_obj.write(cr, uid, [line.id], {'sub_total_main': sub_total_main})
	# 					line_obj.write(cr, uid, [line.id], {'amount_discount_main': amount_discount_main})

	# 				for linetax in invoice.tax_line:
	# 					base_main = round(linetax.base*pajak)
	# 					tax_main = round(linetax.amount*pajak)

	# 					# Update Line tax Invoice dikali dengan Rate
	# 					line_tax.write(cr, uid, [linetax.id], {'base_main': base_main})
	# 					line_tax.write(cr, uid, [linetax.id], {'tax_main': tax_main})

	# 	return super(account_invoice, self).write(cr, uid, ids, vals, context=context)
		
account_invoice()


class account_invoice_line(osv.osv):

	
	_inherit = "account.invoice.line"
	_description = "Invoice Line"
	def _get_line_tax_amount_values(self,cr,uid,line_record,tax_record):
		ailta = self.pool.get('account.invoice.line.tax.amount')
		conditions = [('invoice_line_id','=',line_record.id),('tax_id','=',tax_record.id)]
		
		ids = ailta.search(cr,uid,conditions,{})
		
		if len(ids)==1:
			rec = ailta.browse(cr,uid,ids,{})
			return rec[0]
		elif len(ids)>1:
			raise osv.except_osv(_("Error"),_('Error'))
			return False
		else:
			return False

	def _count_tax_obj(self,tax_obj,line_obj,sub_total_main,dp=5):
		exp =re.compile('PPN',re.IGNORECASE) 

		tax_amount_main=0.0
		tax_amount = 0.0
		ppn_tax_amount_main=0.0
		if tax_obj.type=='percentage':
			tax_amount+=round(line_obj.price_subtotal*tax_obj.amount,dp)
			tax_amount_main += round(sub_total_main*tax_obj.amount,dp)

			# if PPN tax
			if exp.match(tax_obj.name):
				ppn_tax_amount_main += round(sub_total_main*tax_obj.amount,dp)

		elif tax_obj.type=='fixed':
			tax_amount+=round(tax_obj.amount,dp)
			tax_amount_main += round(tax_obj.amount,dp)
			# find ppn
			if exp.match(tax_obj.name):
				ppn_tax_amount_main += round(sub_total_main*tax_obj.amount,dp)
		else:
			tax_amount+=round(line_obj.price_subtotal*tax_obj.amount,dp)
			tax_amount_main += round(sub_total_main*tax_obj.amount,dp)
			# if PPN
			if exp.match(tax_obj.name):
				ppn_tax_amount_main += round(sub_total_main*tax_obj.amount,dp)

		return {
			'tax_amount':tax_amount,
			'tax_amount_main':tax_amount_main,
			'ppn_tax_amount_main':ppn_tax_amount_main
		}

	def _get_convert_main_currency(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		print field_name,'_____________________________'
		
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		dec_precision_tax_line = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
		inv_lines = self.browse(cr,uid,ids,context=context)
		user = self.pool.get('res.users').browse(cr, uid, uid, {})

		for line in inv_lines:
			
			tax_rate = 1 if line.invoice_id.pajak <= 1 else line.invoice_id.pajak
			tax_amount=0.00
			tax_amount_main = 0.00
			ppn_tax_amount_main = 0.00
			amount_discount = 0.00
			price_subtotal = 0.00
			price_subttoal_netto = 0.00
			
			if not line.invoice_id:
				print "Invoice Tidak Ada",line.id
				continue
			else:
				print "Ada invoice",line.id,' Invoice #',line.invoice_id.id
			
			if line.invoice_id.currency_id.id  == user.company_id.currency_id.id:
				unit_price_main = line.price_unit

				amount_bruto_main = line.amount_bruto
				
				sub_total_main = line.price_subtotal
				print line.sub_total_main,"<<<>>>",line.price_subtotal
				amount_discount_main = line.amount_discount_main

				# sub_total_netto_main = sub_total_main
			else: 
				unit_price_main = round(tax_rate*line.price_unit,dec_precision)

				amount_bruto_main = round(unit_price_main*line.quantity,dec_precision)
				
				amount_discount_main = 0.00
				if line.amount_discount:
					if line.discount:
						amount_discount_main = round(amount_bruto_main*(line.discount/100),dec_precision)
					else:
						amount_discount_main = round(line.amount_discount * tax_rate,dec_precision)
				else:
					if line.discount:
						amount_discount_main = round(amount_bruto_main*(line.discount/100),dec_precision)

				sub_total_main = amount_bruto_main-amount_discount_main
				# sub_total_netto_main = tax_rate

			# count price_subtotal
			price_subtotal = round((line.amount_bruto-line.amount_discount),2)



			# for tax in line.tax_amount_ids:
			# 	print "Test Tax Line ",line.id,"---->>>>>>>>>>>>>>>",tax.tax_amount

			# count tax
			# print "SUBTOTAL_MAIN_______________________",sub_total_main
			exp =re.compile('PPN',re.IGNORECASE)
			for tax in line.invoice_line_tax_id:
				exist_tax_amount_obj = self._get_line_tax_amount_values(cr,uid,line,tax)
				# if has account invoice line tax amount obj
				if exist_tax_amount_obj:

					if exist_tax_amount_obj.is_manual:
						print "ADA account invoice line tax amount dan Manual"
						# write if account.invoice.line.tax.amount is_manual == true
						tax_amount += exist_tax_amount_obj.tax_amount
						# tax amount main
						tax_amount_main += exist_tax_amount_obj.tax_amount_main
					
						if exp.match(tax.name):
							ppn_tax_amount_main += tax_amount_main
						print tax_amount_main,"--<><>--<><>"
					else:
						print "ADA account invoice line tax amount dan Tidak Manual"
						print exist_tax_amount_obj.tax_amount_main
						countedTax = self._count_tax_obj(tax,line,sub_total_main,dp=dec_precision_tax_line)
						tax_amount += countedTax['tax_amount']
						tax_amount_main += countedTax['tax_amount_main']
						ppn_tax_amount_main += countedTax['ppn_tax_amount_main']
						
				else:
					print "TIDAK ADA account invoice line tax amount------"
					# if tax.type=='percentage':
					# 	tax_amount+=round(line.price_subtotal*tax.amount,dec_precision_tax_line)
					# 	tax_amount_main += round(sub_total_main*tax.amount,dec_precision_tax_line)

					# 	# if PPN tax
					# 	if exp.match(tax.name):
					# 		ppn_tax_amount_main += round(sub_total_main*tax.amount,dec_precision_tax_line)

					# elif tax.type=='fixed':
					# 	tax_amount+=round(tax.amount,dec_precision_tax_line)
					# 	tax_amount_main += round(tax.amount,dec_precision_tax_line)
					# 	# find ppn
					# 	if exp.match(tax.name):
					# 		ppn_tax_amount_main += round(sub_total_main*tax.amount,dec_precision_tax_line)
					# else:
					# 	tax_amount+=round(line.price_subtotal*tax.amount,dec_precision_tax_line)
					# 	tax_amount_main += round(sub_total_main*tax.amount,dec_precision_tax_line)
					# 	# if PPN
					# 	if exp.match(tax.name):
					# 		ppn_tax_amount_main += round(sub_total_main*tax.amount,dec_precision_tax_line)
					print '<<<<<<',sub_total_main
					countedTax = self._count_tax_obj(tax,line,sub_total_main,dp=dec_precision_tax_line)
					tax_amount += countedTax['tax_amount']
					tax_amount_main += countedTax['tax_amount_main']
					ppn_tax_amount_main += countedTax['ppn_tax_amount_main']
					print 'Counted Tax--->>>>',countedTax
				# end if
			
			# count price_subtotal_netto
			price_subtotal_netto = price_subtotal + tax_amount

			
			
			sub_total_netto_main = sub_total_main + tax_amount_main
			
			
			res[line.id] = {
				'unit_price_main': unit_price_main,
				'amount_bruto_main': amount_bruto_main,
				'sub_total_main': sub_total_main,
				'amount_discount_main': amount_discount_main,
				'tax_amount': tax_amount,
				'tax_amount_main': tax_amount_main,
				'ppn_tax_amount_main': ppn_tax_amount_main,
				'price_subtotal':price_subtotal,
				'price_subtotal_netto':price_subtotal_netto,
				'sub_total_netto_main': sub_total_netto_main,
			}

		print "Result OF _get_convert_main_currency_________________________________________",field_name,res
		return res
	def _get_invoice_line_by_invoice(self, cr, uid, ids, context=None):
		
		result = {}
		for inv in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
			for line in inv.invoice_line:
				result[line.id] = True
		return result.keys()


	def _get_invoice_line_by_line_tax_amount(self, cr, uid, ids, context=None):
		
		result = {}
		for inv in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
			for line in inv.invoice_line:
				for lta in line.tax_amount_ids:
					result[lta.invoice_line_id] = True
		return result.keys()

	

	# def _get_price_subtotal_group(self, cr, uid, ids, prop, unknow_none, unknow_dict):
	
	# 	res = super(account_invoice_line,self)._amount_line(cr,uid,ids,prop,unknow_none,unknow_dict)
	# 	dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
	# 	# TEST AJA lagi
	# 	res = {}
	# 	tax_obj = self.pool.get('account.tax')
	# 	# cur_obj = self.pool.get('res.currency')
	# 	for line in self.browse(cr, uid, ids):
	# 		if line.amount_discount!=0.0:
	# 			price = line.price_unit - (line.amount_discount/line.quantity)
	# 		elif line.discount!=0.0:
	# 			# amount discount null/0.0 but discount percentage is set,, then system will warn the user to make sure the nominal of discount
	# 			raise osv.except_osv(_('Error!'),_('Discount on percentage is defined but the nominal is not defined,,Please fill the discount on nominal field, based on discount percentage of total price or Contact your System Administrator!'))
	# 		else:
	# 			price = line.price_unit
			
			
	# 		taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
	
	# 		res[line.id] = taxes['total']
	# 		if line.invoice_id:
	# 			cur = line.invoice_id.currency_id
	# 			# res[line.id] = cur_obj.round(cr, uid, cur, res[line.id]) #old
	# 			res[line.id] = round(res[line.id],dec_precision)
	# 	return res

	


	def _set_tax_amount(self, cr, uid, id, field_name, field_value, args=None, context={}):
		
		res = {}
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		
		for item in self.browse(cr,uid,[id],context=context):
			if item.tax_amount != field_value:
				res[item.id] = field_value
				cr.execute("""update account_invoice_line set tax_amount=%s where id=%s""", (field_value, item.id))
			else:
				
				res[item.id] = round(item.quantity*item.price_unit,dec_precision)

		return True


	def _set_price_subtotal(self, cr, uid, id, field_name, field_value, args=None, context={}):
		res = {}
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		
		for item in self.browse(cr,uid,[id],context=context):
			if item.price_subtotal != field_value:
				cr.execute("""update account_invoice_line set price_subtotal=%s where id=%s""", (field_value, item.id))
			else:
				
				field_value
				# res[item.id] = round(item.quantity*item.price_unit,dec_precision)

		return True

	def _set_price_subtotal_netto(self, cr, uid, id, field_name, field_value, args=None, context={}):
		
		res = {}
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		
		for item in self.browse(cr,uid,[id],context=context):
			if item.price_subtotal_netto != field_value:
				
				cr.execute("""update account_invoice_line set price_subtotal_netto=%s where id=%s""", (field_value, item.id))
				return False
			else:
				
				field_value
				# res[item.id] = round(item.quantity*item.price_unit,dec_precision)

		return True
	def _get_invoice_line_by_invoice_line_tax_amount(self,cr,uid,ids,context={}):
		result = {}
		
		for tax in self.pool.get('account.invoice.line.tax.amount').browse(cr, uid, ids, context=context):
			result[tax.invoice_line_id.id] = True
		# printresult
		return result.keys()
	def _set_tax_amount_main(self, cr, uid, id, field_name, field_value, args=None, context={}):
		
		res = {}
		dp = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')

		for item in self.browse(cr,uid,[id],context=context):
			if item.tax_amount_main != field_value:
				res[item.id] = field_value
				cr.execute("""update account_invoice_line set tax_amount_main=%s where id=%s""", (field_value, item.id))

		return True
	_columns = {
		'unit_price_main': fields.function(
			_get_convert_main_currency,
			multi="all",
			string='Unit Price Main',
			type="float",
			digits_compute=dp.get_precision('Account'),
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit'], 91),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],91)
			}
		),


		'amount_discount_main': fields.function(
			_get_convert_main_currency,
			multi="all",
			string='Amount Discount (Main Currency)',
			type="float",
			digits_compute=dp.get_precision('Account'),
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['amount_discount','discount','invoice_line_tax_id'],91),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],91)
			}
		),

		'amount_bruto_main': fields.function(
			_get_convert_main_currency,
			multi="all",
			string='Amount Total (Main Currency)',
			help="Amount bruto, price unit multiply quantity, ammount before discount and taxes / pure total amount",
			type="float",
			digits_compute=dp.get_precision('Account'),
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['unit_price_main','quantity'],91),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],91)
			}
		),


		'sub_total_main': fields.function(
			_get_convert_main_currency,
			multi="all",
			string='SubTotal (Main Currency)',
			type="float",
			digits_compute=dp.get_precision('Account'),
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['amount_bruto_main','amount_discount_main'],91),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],91)
			}
		),

		'tax_amount': fields.function(
			fnct=_get_convert_main_currency,
			fnct_inv=_set_tax_amount,
			multi="all",
			string='Tax Amount',
			type="float",
			digits_compute=dp.get_precision('TaxLine'),
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['price_subtotal','invoice_line_tax_id','tax_amount_ids'],91),
				'account.invoice.line.tax.amount': (_get_invoice_line_by_invoice_line_tax_amount,['tax_amount','tax_amount_main'],91),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],91),
			}
		),


		'tax_amount_main': fields.function(
			fnct=_get_convert_main_currency,
			fnct_inv=_set_tax_amount_main,
			multi="all",
			string='Tax Amount (Main Currency)',
			type="float",
			digits_compute=dp.get_precision('Account'),
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['tax_amount','sub_total_main','invoice_line_tax_id','ppn_tax_amount_main'],91),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],91),
				'account.invoice.line.tax.amount': (_get_invoice_line_by_invoice_line_tax_amount,['tax_amount','tax_amount_main'],91),
			}
		),
		'ppn_tax_amount_main': fields.function(
			_get_convert_main_currency,
			multi="all",
			string='PPN Amount (Main Currency)',
			type="float",
			digits_compute=dp.get_precision('Account'),
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['tax_amount','tax_amount_main','sub_total_main','invoice_line_tax_id'],91),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],91),
				'account.invoice.line.tax.amount': (_get_invoice_line_by_line_tax_amount, ['tax_amount_main'],91)
			}
		),

		'price_subtotal': fields.function(
			fnct=_get_convert_main_currency,
			fnct_inv=_set_price_subtotal,
			string='Total (Before Tax)',
			type="float",
			multi="all",
			digits_compute=dp.get_precision('Account'),
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit','quantity','amount_discount','discount'],90),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],90),
				'account.invoice.line.tax.amount': (_get_invoice_line_by_line_tax_amount,['tax_amount'],90),
			},
		),
		'price_subtotal_netto': fields.function(
			# method=True,
			fnct=_get_convert_main_currency, 
			fnct_inv=_set_price_subtotal_netto,
			string='SubTotal(Netto)',
			type="float",
			multi="all",
			digits_compute=dp.get_precision('Account'),
			# store=True,
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['price_subtotal','tax_amount'],91),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],91),
				'account.invoice.line.tax.amount': (_get_invoice_line_by_line_tax_amount,['tax_amount'],91),
			},
		),

		'sub_total_netto_main': fields.function(
			_get_convert_main_currency,
			multi="all",
			string='Subtotal Netto (Main Currency)',
			type="float",
			digits_compute=dp.get_precision('Account'),
			store={
				'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['tax_amount','tax_amount_main','sub_total_main','price_subtotal_netto'],91),
				'account.invoice': (_get_invoice_line_by_invoice, ['pajak','invoice_line'],91)
			}
		),

		
	}


	def replace_discount(self,cr,uid,ids,qty,price, disc):
		
		
		discVal = disc/100.00

		# discount = discVal
		
		discount = (qty*price)*discVal
		return {'value':{ 'amount_discount':discount} }


account_invoice_line()


class account_invoice_tax(osv.osv):

	def _get_tax_main(self,cr,uid,ids,field_name,args,context={}):
		print "Calling _get_tax_main-----___--____--_--___--__---_-_-_--____",field_name
		# recs = self.browse(cr,uid,ids,context=context)
		dp = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
		res = {}
		for inv_tax in self.browse(cr,uid,ids,context=context):
			
			for inv_line in inv_tax.invoice_id.invoice_line:
				# loop each invoice_lines
				tax_amount_main = 0.0

				for tax_line_amount in inv_line.tax_amount_ids:
					# loop each tax_line_amount
					if inv_tax.name==tax_line_amount.tax_id.name:
						# find same tax name
						tax_amount_main+=tax_line_amount.tax_amount_main
				res[inv_tax.id] = {
					'base_main':math.floor(inv_tax.invoice_id.amount_untaxed_main),
					'amount_main':math.floor(tax_amount_main),
				}

		
		print res,"---____"
		return res

	
	def _get_invoice_tax_by_invoice(self, cr, uid, ids, context=None):
		result = {}
		
		for inv in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
			for line in inv.tax_line:
				result[line.id] = True
		return result.keys()

	def _get_invoice_tax_by_invoice_line(self, cr, uid, ids, context=None):
		result = {}
		
		for inv in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
			for line in inv.invoice_id.tax_line:
				result[line.id] = True
		return result.keys()

	_inherit = 'account.invoice.tax'

	_columns = {
		# 'base_main': fields.float('Base Main'),
		# 'tax_main': fields.float('Tax Main'),
		'base_main': fields.function(
			_get_tax_main,
			string='Base Main',
			multi="tax_group",
			type="float",
			store={
				'account.invoice.tax': (lambda self, cr, uid, ids, c={}: ids, ['base','amount'], 92),
				'account.invoice': (_get_invoice_tax_by_invoice, ['pajak'],92),
				'account.invoice.line': (_get_invoice_tax_by_invoice_line, ['tax_amount','tax_amount_main'],92)
			}
		),
		'amount_main': fields.function(
			_get_tax_main,
			string='Amount Main',
			type="float",
			multi="tax_group",
			store={
				'account.invoice.tax': (lambda self, cr, uid, ids, c={}: ids, ['base','amount'], 92),
				'account.invoice': (_get_invoice_tax_by_invoice, ['pajak'],92),
				'account.invoice.line': (_get_invoice_tax_by_invoice_line, ['tax_amount','tax_amount_main'],93)
			}
		),
	}

account_invoice_tax()


# class account_invoice_line_tax_amount(osv.osv):
# 	_inherit = 'account.invoice.line.tax.amount'
# 	_columns = {
# 		''
# 	}


# class sale_advance_payment_inv(osv.osv_memory):
# 	_inherit = "sale.advance.payment.inv"


# 	def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
# 		if context is None:
# 			context = {}
# 		sale_obj = self.pool.get('sale.order')
# 		ir_property_obj = self.pool.get('ir.property')
# 		fiscal_obj = self.pool.get('account.fiscal.position')
# 		inv_line_obj = self.pool.get('account.invoice.line')
# 		wizard = self.browse(cr, uid, ids[0], context)
# 		sale_ids = context.get('active_ids', [])

# 		result = []
# 		for sale in sale_obj.browse(cr, uid, sale_ids, context=context):
# 			rate = 0.0
# 			exp =re.compile('IDR',re.IGNORECASE) 
# 			if exp.match(sale.pricelist_id.currency_id.name):
# 				rate = 1.0

# 			val = inv_line_obj.product_id_change(cr, uid, [], wizard.product_id.id,
# 					uom_id=False, partner_id=sale.partner_id.id, fposition_id=sale.fiscal_position.id)
# 			res = val['value']

# 			# determine and check income account
# 			if not wizard.product_id.id :
# 				prop = ir_property_obj.get(cr, uid,
# 							'property_account_income_categ', 'product.category', context=context)
# 				prop_id = prop and prop.id or False
# 				account_id = fiscal_obj.map_account(cr, uid, sale.fiscal_position or False, prop_id)
# 				if not account_id:
# 					raise osv.except_osv(_('Configuration Error!'),
# 							_('There is no income account defined as global property.'))
# 				res['account_id'] = account_id
# 			if not res.get('account_id'):
# 				raise osv.except_osv(_('Configuration Error!'),
# 						_('There is no income account defined for this product: "%s" (id:%d).') % \
# 							(wizard.product_id.name, wizard.product_id.id,))

# 			# determine invoice amount
# 			if wizard.amount <= 0.00:
# 				raise osv.except_osv(_('Incorrect Data'),
# 					_('The value of Advance Amount must be positive.'))
# 			if wizard.advance_payment_method == 'percentage':
# 				inv_amount = sale.amount_total * wizard.amount / 100
# 				if not res.get('name'):
# 					res['name'] = _("Advance of %s %%") % (wizard.amount)
# 			else:
# 				inv_amount = wizard.amount
# 				if not res.get('name'):
# 					#TODO: should find a way to call formatLang() from rml_parse
# 					symbol = sale.pricelist_id.currency_id.symbol
# 					if sale.pricelist_id.currency_id.position == 'after':
# 						res['name'] = _("Advance of %s %s") % (inv_amount, symbol)
# 					else:
# 						res['name'] = _("Advance of %s %s") % (symbol, inv_amount)

# 			# determine taxes
# 			if res.get('invoice_line_tax_id'):
# 				res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
# 			else:
# 				res['invoice_line_tax_id'] = False

# 			# create the invoice
# 			inv_line_values = {
# 				'name': res.get('name'),
# 				'origin': sale.name,
# 				'account_id': res['account_id'],
# 				'price_unit': inv_amount,
# 				'quantity': wizard.qtty or 1.0,
# 				'discount': False,
# 				'discount_amount':False,
# 				'uos_id': res.get('uos_id', False),
# 				'product_id': wizard.product_id.id,
# 				'invoice_line_tax_id': res.get('invoice_line_tax_id'),
# 				'account_analytic_id': sale.project_id.id or False,
# 			}
# 			inv_values = {
# 				'name': sale.client_order_ref or sale.name,
# 				'origin': sale.name,
# 				'type': 'out_invoice',
# 				'reference': False,
# 				'account_id': sale.partner_id.property_account_receivable.id,
# 				'partner_id': sale.partner_invoice_id.id,
# 				'invoice_line': [(0, 0, inv_line_values)],
# 				'currency_id': sale.pricelist_id.currency_id.id,
# 				'comment': '',
# 				'payment_term': sale.payment_term.id,
# 				'fiscal_position': sale.fiscal_position.id or sale.partner_id.property_account_position.id,
# 				'group_id':sale.group_id.id,
# 				'user_id':sale.user_id.id,
# 				'pajak': rate,
# 			}
# 			result.append((sale.id, inv_values))

# 			print"CALLLLEDDD PREPARE ADVANCED"
# 		return result
# 	def create_invoices(self,cr,uid,ids,context=None):
# 		print"CALLLLEDDD PREPARE ADVANCED---------------------"
# 		return super(sale_advance_payment_inv,self).create_invoices(cr,uid,ids,context=context)
		
	# def create_invoices(self, cr, uid, ids, context=None):
	# 	ai = self.pool.get('account.invoice')
	# 	ait = self.pool.get('account.invoice.tax')
	# 	res = super(sale_advance_payment_inv,self).create_invoices(cr,uid,ids,context=context)
	# 	# printres,"<<<<>>>>>>"
	# 	inv_id = None
	# 	if 'views' in res:
	# 		# print"Show VIEW POp Up"
	# 	else:
	# 		if 'res_id' in res:
	# 			inv_id = res['res_id']


	# 	if inv_id:
	# 		# invoice created
	# 		ai_rec = ai.browse(cr,uid,ids,context=context)
	# 		rate = 0.0
	# 		exp =re.compile('IDR',re.IGNORECASE) 
	# 		for inv in ai_rec:
	# 			if exp.match(inv.currency_id.name):
	# 				rate = 1.0
	# 				ai.write(cr,uid,ids,{'pajak':rate},context=context)

	# 	# raise osv.except_osv(_('Error!'),_('Error Invoice'))
	# 	return res


class sale_order(osv.osv):
	_inherit = 'sale.order'
	def manual_invoice(self, cr, uid, ids, context=None):
		""" create invoices for the given sales orders (ids), and open the form
			view of one of the newly created invoices
		"""
		mod_obj = self.pool.get('ir.model.data')
		wf_service = netsvc.LocalService("workflow")

		# create invoices through the sales orders' workflow
		inv_ids0 = set(inv.id for sale in self.browse(cr, uid, ids, context) for inv in sale.invoice_ids)
		for id in ids:
			wf_service.trg_validate(uid, 'sale.order', id, 'manual_invoice', cr)
		inv_ids1 = set(inv.id for sale in self.browse(cr, uid, ids, context) for inv in sale.invoice_ids)
		
		
		# determine newly created invoices
		new_inv_ids = list(inv_ids1 - inv_ids0)

		if not new_inv_ids:
			new_inv_ids = [self.action_invoice_create(cr, uid, ids, context)]
			
		res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
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
			'res_id': new_inv_ids and new_inv_ids[0] or False,
		}

class sale_order_line(osv.osv):
	_inherit = 'sale.order.line'
	def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
		
		"""Prepare the dict of values to create the new invoice line for a
		   sales order line. This method may be overridden to implement custom
		   invoice generation (making sure to call super() to establish
		   a clean extension chain).

		   :param browse_record line: sale.order.line record to invoice
		   :param int account_id: optional ID of a G/L account to force
			   (this is used for returning products including service)
		   :return: dict of values to create() the invoice line
		"""
		res = {}
		if not line.invoiced:
			if not account_id:
				if line.product_id:
					account_id = line.product_id.property_account_income.id
					if not account_id:
						account_id = line.product_id.categ_id.property_account_income_categ.id
					if not account_id:
						raise osv.except_osv(_('Error!'),
								_('Please define income account for this product: "%s" (id:%d).') % \
									(line.product_id.name, line.product_id.id,))
				else:
					prop = self.pool.get('ir.property').get(cr, uid,
							'property_account_income_categ', 'product.category',
							context=context)
					account_id = prop and prop.id or False
			uosqty = self._get_line_qty(cr, uid, line, context=context)
			uos_id = self._get_line_uom(cr, uid, line, context=context)
			pu = 0.0
			if uosqty:
				pu = round(line.price_unit * line.product_uom_qty / uosqty,
						self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
			fpos = line.order_id.fiscal_position or False
			account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
			if not account_id:
				raise osv.except_osv(_('Error!'),
							_('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
			res = {
				'name': line.name,
				'sequence': line.sequence,
				'origin': line.order_id.name,
				'account_id': account_id,
				'price_unit': pu,
				'quantity': uosqty,
				'discount': line.discount,
				'amount_discount' : line.discount_nominal,
				'uos_id': uos_id,
				'product_id': line.product_id.id or False,
				'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
				'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
			}
			

		return res

class account_invoice_line_tax_amount(osv.osv):

	def write(self,cr,uid,ids,vals,context={}):

		recs = self.browse(cr,uid,ids,context=context)
		user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
		
		is_manual = False
		is_tax_amount = False
		is_tax_amount_main = False
		
		if "is_manual" in vals:
			is_manual=True
		
		if "tax_amount" in vals:
			is_tax_amount = True
			

		if "is_manual_main" in vals:
			is_manual = True

		if "tax_amount_main" in vals:
			is_tax_amount_main = True
			
		
		for rec in recs:
			if user.company_id.currency_id.id == rec.invoice_line_id.invoice_id.currency_id.id:
				# if same with main company currency then
				# override tax_amount_main and base amount main
				if rec.is_manual:
					is_manual = True

				if rec.is_manual_main:
					is_manual_main=True

				print is_manual
				print is_tax_amount,vals
				if is_manual and is_tax_amount:
					# print "AAAAAA--->>>"
					vals['base_amount_main'] = rec.base_amount
					vals['tax_amount_main'] = vals['tax_amount']
				else:
					raise osv.except_osv(_('Error'),_('Error to write into account.invoice.line.tax.amount, please contact system administrator'))
			else:
				if is_manual and not is_tax_amount_main:
					raise osv.except_osv(_('Error'),_('Error to write account.invoice.line.tax.amount, please contact system administrator, Ref: is_manual and not is_tax_amount_main'))
		print "END Call Write in account_invoice_line_tax_amount in invoice main-----------------"
		return super(account_invoice_line_tax_amount,self).write(cr,uid,ids,vals,context=context)


	def create(self,cr,uid,vals,context={}):
		ail_obj = self.pool.get('account.invoice.line')
		# print "VALLLLLLLL",vals
		# raise osv.except_osv(_('Errr'),_('EEEEEEEEEEEEEEEEEEEEE'))
		inv_line_id = vals['invoice_line_id']
		ail = ail_obj.browse(cr,uid,[inv_line_id],context=context)[0]
		
		# replace with re compute
		getRecompute = ail_obj._get_convert_main_currency(cr,uid,[inv_line_id],['tax_amount_main'],None,context=context)
		print getRecompute,"-------XOXOXXOXOXO-------"
		vals['base_amount_main'] = getRecompute[inv_line_id]['price_subtotal']
		vals['tax_amount_main'] = getRecompute[inv_line_id]['tax_amount_main']

		res = super(account_invoice_line_tax_amount,self).create(cr,uid,vals,context=context)
		self.pool.get('account.invoice.line').write(cr,uid,[inv_line_id],{'tax_amount':vals['tax_amount'],'tax_amount_main':vals['tax_amount_main']})
		return res

	def _get_invoice_tax_amount_by_invoice_line(self, cr, uid, ids, context=None):
		result = {}
		
		for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
			for line_tax_amount in line.tax_amount_ids:
				result[line_tax_amount.id] = True
		return result.keys()

	def _get_invoice_tax_amount_by_invoice(self, cr, uid, ids, context=None):
		result = {}
		
		for inv in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
			for line in inv.invoice_line:
				for line_tax_amount in  line.tax_amount_ids:
					result[line_tax_amount.id] = True
		return result.keys()

	def _get_invoice_line_tax_amount(self,cr,uid,ids,field_name,args,context={}):
		dp = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
		res = {}

		user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
		ail_obj = self.pool.get('account.invoice.line')

		selfObj  = self.browse(cr,uid,ids,context=context)
		for o in selfObj:
			res[o.id] = 0.0
			if o.invoice_line_id.invoice_id.currency_id.id == user.company_id.currency_id.id:
				# if same currecny with main currency then same with tax_amount field in self obj
				res[o.id] = {
					'base_amount_main':o.base_amount,
					'tax_amount_main': o.tax_amount_main
				}
			else:

				main_amount = ail_obj._count_tax_obj(o.tax_id,o.invoice_line_id,o.invoice_line_id.sub_total_main,dp=dp)
				res[o.id] = {
					'base_amount_main':o.invoice_line_id.sub_total_main,
					'tax_amount_main': main_amount['tax_amount_main'],
				}
		print ">>>>>>>>>>>>>>>>>>>>---->>>>>>>>>>>>>>>>",res
		return res

	def _set_tax_amount_main(self, cr, uid, id, field_name, field_value, args=None, context={}):
		
		res = {}
		dp = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		
		for item in self.browse(cr,uid,[id],context=context):
			if item.tax_amount_main != field_value:
				res[item.id] = field_value
				cr.execute("""update account_invoice_line_tax_amount set tax_amount_main=%s where id=%s""", (field_value, item.id))

		return True
	def on_change_tax_amount_main(self,cr,uid,ids,base_amount_main,tax_amount_main):
		res = {}
		ai = self.pool.get('account.invoice')

		for line_tax_amount in self.browse(cr,uid,ids,{}):
			# base_code_line_id = line_tax_amount.tax_id.base_code_id.id
			
			res['value'] = {'is_manual_main':True}
		return res

	_inherit  = 'account.invoice.line.tax.amount'

	_columns = {

		
		'base_amount_main': fields.function(
			fnct=_get_invoice_line_tax_amount,
			type="float",
			multi="amount",
			string="Base Amount Main",
			digits_compute=dp.get_precision('Account'),
			store={
				'account.invoice.line': (_get_invoice_tax_amount_by_invoice_line, ['tax_amount'],101),
				'account.invoice': (_get_invoice_tax_amount_by_invoice,['pajak','invoice_line'],101),
			}
		),
		'tax_amount_main': fields.function(
			fnct=_get_invoice_line_tax_amount,
			fnct_inv=_set_tax_amount_main,
			type="float",
			string="Tax Amount Main",
			multi="amount",
			digits_compute=dp.get_precision('TaxLine'),
			store={
				'account.invoice.line.tax.amount':(lambda self, cr, uid, ids, c={}: ids, ['tax_amount'], 101),
				'account.invoice.line': (_get_invoice_tax_amount_by_invoice_line, ['tax_amount'],101),
				'account.invoice': (_get_invoice_tax_amount_by_invoice,['pajak','invoice_line'],101),

			}
		),
		'currency' : fields.related('invoice_line_id.invoice_id.currency_id','name',string="Currency",store=False),
		'is_manual_main':fields.boolean(string="Is Manual"),
	}

	def _map_value(self,cr,uid,line_id,tax_id,base_amount,tax_amount,base_amount_main,tax_amount_main):
		return {
			'invoice_line_id': line_id,
			'tax_id': tax_id,
			'base_amount': base_amount,
			'tax_amount': tax_amount,
			'base_amount_main': base_amount_main,
			'tax_amount_main' : tax_amount_main,
		}