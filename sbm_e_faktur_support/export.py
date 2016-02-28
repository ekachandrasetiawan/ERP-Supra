import openerp.exceptions
import datetime,time
import csv
import math
from openerp import tools
from openerp.tools.translate import _
from osv import osv, fields
import urllib
from cStringIO import StringIO

import openerp.addons.decimal_precision as dp

from openerp.tools.float_utils import float_round

# import web.http as openerpweb

import openerp.addons.web.http as oeweb


class acount_invoice(osv.osv):
	_inherit = 'account.invoice'
	_columns = {
		'faktur_pajak_no': fields.char('No Faktur Pajak',size=20,required=True),
		'state': fields.selection([
			('draft','Draft'),
			('submited','Submited'), #NEW FLOW TO SUBMIT TO VALIDATE THE INVOICE
			('proforma','Pro-forma'),
			('proforma2','Pro-forma'),
			('open','Open'),
			('paid','Paid'),
			('cancel','Cancelled'),
			],'Status', select=True, readonly=True, track_visibility='onchange',
			help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Invoice. \
			\n* The \'Pro-forma\' when invoice is in Pro-forma status,invoice does not have an invoice number. \
			\n* The \'Open\' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice. \
			\n* The \'Paid\' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
			\n* The \'Cancelled\' status is used when user cancel invoice.'),
	}

	def draft_submited(self,cr,uid,ids,context={}):
		for s in self.browse(cr,uid,ids,context=context):
			if s.state != 'submited':
				raise osv.except_osv(_('Error'),_('Tidak bisa merubah status menjadi draft karena status sudah validate!'))
			
		self.write(cr,uid,ids,{'state':'draft'})

		return True
	def submit_to_validate(self,cr,uid,ids,context={}):
		# res = {}
		res = False
		for d in self.browse(cr,uid,ids,context=context):
			if d.faktur_pajak_no != '000.000-00.00000000' and d.faktur_pajak_no != '0000000000000000':
				num = d.faktur_pajak_no.split('.')
				fp = num[2]
				# search same number
				sameFP = self.search(cr,uid,[('faktur_pajak_no','like',fp),('state','!=','cancel'),('id','!=',d.id),('type','=','out_invoice')])
				# print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",sameFP
				if len(sameFP) > 0:
					# if exist
					res = False
					browseAllSame = self.browse(cr,uid,sameFP,context=context)
					errSame = [str(bs.id) for bs in browseAllSame]
					# print "==============================",errSame
					raise osv.except_osv(_('Error'),_('Nomor Faktur Pajak Sudah dipakai, tidak bisa menggunakan nomor faktur lebih dari 1 kali, Jika Nomor tersebut diganti silahkan cancel terlebih dahulu invoice yang lama\r\n.'+',\r\n'.join(errSame)))
					res =  False
				else:
					res = True
				
			else:
				if(d.faktur_pajak_no != '000.000-00.00000000'):
					raise osv.except_osv(_('Error'),_('Cek nomor Faktur Pajak!'))
					res=  False
				else:
					res=  True


		if res:
			self.write(cr,uid,d.id,{'state':'submited'},context=context)
		return True
	def efak_invoices_export(self,cr,uid,ids,context={}):
		print ids,"Context Invoice E-Faktur Export----------------------",context
		if context is None:
			context = {}

		if 'active_model' in context and context['active_model']=='sale.advance.payment.inv':
			ids = ids
		else:
			try:
				ids = context['active_ids']
				# print 'active_ids===============',ids
			except:
				ids = ids

			# print 'IDSSSSSSSSSSSSSSSS=========================+++++++',ids

		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"service/get-invoices-csv&ids="+str(','.join(map(str,ids)))+"&uid="+str(uid)
		for browse in self.browse(cr,uid,ids):
			if browse.partner_id.npwp == '11111111111111111111':
				raise osv.except_osv(_('Error!'),_('NPWP '+browse.partner_id.name+' = '+browse.partner_id.npwp+'\r\n\r\nTolong Update NPWP terlebih dahulu untuk export data. Jika Customer ini tidak mempunyai NPWP atau merupakan Customer Perorangan maka Update NPWP menjadi 00.000.000.0-000.000'))
			elif browse.partner_id.npwp == False:
				raise osv.except_osv(_('Error'),_('NPWP '+browse.partner_id.name+' kosong.\r\n\r\nHarus diisi..!!!'))
		
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.out',
			'params': {
				'redir'	: urlTo
			},
		}
	def efak_invoice_data(self,cr,uid,ids,context={}):

		faktur_data = []
		res = False
		outp = StringIO()
		# sw = csv.writer(outp,delimiter=',',quotechar='"')
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency') 
		for inv in self.browse(cr,uid,ids,context):
			cur = inv.currency_id

			KD_JENIS_TRANSAKSI = '01'
			FG_PENGGANTI = '0'
			NOMOR_FAKTUR = inv.kwitansi
			date_invoice = datetime.datetime.strptime(inv.date_invoice,'%Y-%m-%d')
			MASA_PAJAK = date_invoice.month
			TAHUN_PAJAK = date_invoice.year
			TANGGAL_FAKTUR = datetime.datetime.strftime(date_invoice,'%d/%m/%Y')
			NPWP = inv.partner_id.parent_id.npwp or inv.partner_id.npwp
			NAMA = inv.partner_id.parent_id.name or inv.partner_id.name
			ALAMAT_LENGKAP = inv.partner_id.street
			JUMLAH_DPP = inv.amount_total
			JUMLAH_PPN = inv.amount_tax
			JUMLAH_PPNBM = 0
			ID_KETERANGAN_TAMBAHAN = ""
			FG_UANG_MUKA = "0"
			UANG_MUKA_DPP = "0"
			UANG_MUKA_PPN = "0"
			UANG_MUKA_PPNBM = "0"
			REFERENSI = inv.comment

			faktur_data.append(
				[
					'FK',
					KD_JENIS_TRANSAKSI,
					FG_PENGGANTI,
					NOMOR_FAKTUR,
					MASA_PAJAK,
					TAHUN_PAJAK,
					TANGGAL_FAKTUR,
					NPWP,
					NAMA,
					ALAMAT_LENGKAP,
					JUMLAH_DPP,
					JUMLAH_PPN,
					JUMLAH_PPNBM,
					ID_KETERANGAN_TAMBAHAN,
					FG_UANG_MUKA,
					UANG_MUKA_DPP,
					UANG_MUKA_PPN,
					UANG_MUKA_PPNBM,
					REFERENSI
				]
			)
			# CUSTOMER / SUPLIER DATA
			partner = inv.partner_id.parent_id or inv.partner_id

			faktur_data.append([
				"FAPR", 
				"PT. SUPRABAKRI MANDIRI",
				"Jl. Danau Sunter Utara Blok A No. 9 Tanjung Priok - Jakarta Utara",
				"","","","",""
			])

			# LOOP EACH INVOICE ITEM
			
			for item in inv.invoice_line:
				
				
				ppn_total = 0
				tax_compute =  tax_obj.compute_all(cr, uid, item.invoice_line_tax_id, (item.price_unit* (1-(item.discount or 0.0)/100.0)), item.quantity, item.product_id, inv.partner_id)['taxes'][0]
				# print tax_compute
				faktur_data.append(
					[
						"OF",item.product_id.default_code,item.name,item.price_unit,item.quantity,item.price_subtotal,
						inv.total_discount,item.price_subtotal,
						tax_compute['amount'],
						"0","0.0"
					]
				)
			# sw.writerows(faktur_data)
		# outp.seek(0)
		# data = outp.read()
		# outp.close()
		return faktur_data


class account_invoice(osv.osv):

	def _get_total_discount(self,cr,uid,ids,name,arg,context=None):
		# get total discount from line amount discount
		res = {}
		user_obj = self.pool.get('res.users')
		currency_obj = self.pool.get('res.currency')
		user = user_obj.browse(cr, uid, uid, {})
		
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		invoices = self.pool.get('account.invoice')
		discount=0
		totaldiscount=0 
		amount_untaxed=0
		
		invoices= self.browse(cr, uid, ids, context=context)
		for inv in invoices:
			res[inv.id]=0
			for line in inv.invoice_line:
				res[inv.id]+=line.amount_discount

			

			if inv.currency_id.id==user.company_id.currency_id.id:
				res[inv.id] =math.floor(res[inv.id])
			else:
				res[inv.id] = round(res[inv.id],dec_precision)

		return res
	def _amount_all(self, cr, uid, ids, name, args, context=None):
		
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		res = super(account_invoice,self)._amount_all(cr,uid,ids,name,args,context=context)
		user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
		# print name,"FIELDDDDDDDDD NAMEEEEEEEEEE"

		for invoice in self.browse(cr, uid, ids, context=context):
			res[invoice.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0
			}
			for line in invoice.invoice_line:
				res[invoice.id]['amount_untaxed'] += line.price_subtotal
				# print line.price_subtotal,"..................................................... price subtotal"
			for line in invoice.tax_line:
				res[invoice.id]['amount_tax'] += line.amount
				
			# IF CURRENCY IN VOICE SAME AS CURRENCY DEFINED IN COMPANY SETTING THEN FLOOR THE TOTAL VALUES
			if invoice.currency_id.id==user.company_id.currency_id.id:
				# print res,"BEFOREEEEE FLOOORINGGGG--------------------"
				res[invoice.id]['amount_untaxed'] = math.floor(res[invoice.id]['amount_untaxed'])
				res[invoice.id]['amount_tax'] = math.floor(res[invoice.id]['amount_tax'])
				res[invoice.id]['amount_total'] = math.floor(res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed'])
			else:
				res[invoice.id]['amount_untaxed'] = round(res[invoice.id]['amount_untaxed'],dec_precision)
				res[invoice.id]['amount_tax'] = round(res[invoice.id]['amount_tax'],dec_precision)
				res[invoice.id]['amount_total'] = round(res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed'],dec_precision)

		
		return res
	def _get_invoice_tax(self, cr, uid, ids, context=None):
		# result = super(account_invoice,self)._get_invoice_tax(cr, uid, ids, context=context)
		result = {}
		for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
			result[tax.invoice_id.id] = True
		return result.keys()
	 
	def _get_invoice_line(self, cr, uid, ids, context=None):
		# result = super(account_invoice,self)._get_invoice_line(cr, uid, ids, context=context)
		result = {}
		for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
			result[line.invoice_id.id] = True
		return result.keys()
	_inherit = 'account.invoice'
	_columns = {
		'total_discount':fields.function(
			_get_total_discount,string='Total Discount',required=False,store=False
		),
		'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Subtotal', track_visibility='always',
			store={
				'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 99),
				'account.invoice.tax': (_get_invoice_tax, None, 99),
				'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','tax_amount','price_subtotal','price_subtotal_netto'], 99),
			},
			multi="all"),
		'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
			store={
				'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 99),
				'account.invoice.tax': (_get_invoice_tax, None, 99),
				'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','tax_amount','price_subtotal','price_subtotal_netto'], 99),
			},
			multi="all"),
		'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
			store={
				'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 99),
				'account.invoice.tax': (_get_invoice_tax, None, 99),
				'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','tax_amount','price_subtotal','price_subtotal_netto'], 99),
			},
			multi="all"),
	}
class account_invoice_line(osv.osv):

	def _get_count_amount_bruto(self,price_unit,qty):
		res = round((price_unit*qty),2)
		return res


	"""
	Method to get percentage of discount by amount_discount field changes
	@self
	@amount_bruto (float) amount_bruto 
	@amount_discount (float) discount (amount total of discount)
	"""
	def _get_count_discount(self,amount_bruto,amount_discount):
		if amount_bruto:
			return round((amount_discount/amount_bruto) * 100.00,2)
		else:
			return False

	"""
	Method to get amount discount by percentage discount
	@self
	@amount_bruto (float) total price_unit * qty
	@discount (float) discount in percent
	"""
	def _get_count_amount_discount(self,amount_bruto,discount):
		if discount:
			res = round(((discount/100.0)*amount_bruto),2)
		else:
			res = False
		
		return res

	"""
	Method to get price_subtotal
	price_subtotal = amount_bruto - amount_discount
	result will be rounded into 2 decimal
	@self
	@amount_bruto (float) total price_unit * qty
	@discount (float) discount in percent
	"""
	def _get_count_price_subtotal(self,amount_bruto,amount_discount):
		print "AAA-----CALLLLLLLLLLLLLLLLLLLLLLLEEEEEEEEEEEEEEEEEEEEED"
		return round((amount_bruto-amount_discount),2)

	"""
	Method to get _get_count_tax_amount
	tax_amount  = sumaary of each applied taxes on item based on price_subtotal
	result will be rounded into 2 decimal
	@self
	@price_subtotal (float) base amount
	@taxes (list - many2many) taxes applied on item
	"""
	def _get_count_tax_amount(self,cr,uid,price_subtotal,taxes):
		
		dec_precision_tax_line = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
		tax_ids = []
		tax_ids = taxes[0][2]

		tax_obj = self.pool.get('account.tax').browse(cr,uid,tax_ids,{})
		tax_amount = 0.00
		for tax in tax_obj:
			
			if tax.type=='percent':
				tax_amount += round((tax.amount*price_subtotal),dec_precision_tax_line)
				
			else:
				raise osv.except_osv(_('Error'),_('Tax not support'))

		return tax_amount
	"""
	Method to get price_subtotal_netto
	
	result will be rounded into 2 decimal
	@self
	@price_subtotal (float)
	@tax_amount (float)
	"""
	def _get_count_price_subtotal_netto(self,price_subtotal,tax_amount):
		
		res = round(price_subtotal+tax_amount,2)
		
		return res



	"""

	"""
	def _change_amount_discount(self,amount_bruto,discount,amount_discount):
		# if discount amount changed
		# check if discount rounded
		res = {}
		prop_disc = self._get_count_discount(float(amount_bruto),float(amount_discount))

		
		if math.ceil(prop_disc) != math.ceil(discount):
			# if base different is same
			res['discount'] = prop_disc
			
		else:
			res['discount'] = discount
			
		res['price_subtotal'] = self._get_count_price_subtotal(amount_bruto,amount_discount)

		return res


	"""
	"""
	def on_change_amount(self,cr,uid,ids,field_name,price_unit,quantity,amount_bruto,discount_p,discount_a,price_subtotal,taxes,tax_amount):
		
		res = {
			'value':{
				'amount_bruto':float(amount_bruto),
				'discount':float(discount_p),
				'amount_discount':float(discount_a),
				'tax_amount':float(tax_amount),
				'price_subtotal_netto': 0.00,
			}
		}
		# if changed from price_unit
		if field_name == 'price_unit' or field_name=='quantity':
			
			res['value']['amount_bruto'] = self._get_count_amount_bruto(price_unit,quantity)
			change_amount_discount = self._change_amount_discount(res['value']['amount_bruto'],discount_p,discount_a)
			res['value']['discount'] = change_amount_discount['discount']
			res['value']['price_subtotal'] = change_amount_discount['price_subtotal']

		elif field_name == 'discount':
			# if discount change
			res['value']['amount_discount'] = self._get_count_amount_discount(amount_bruto,discount_p)
		elif field_name == 'amount_discount':
			change_amount_discount = self._change_amount_discount(amount_bruto,discount_p,discount_a)
			res['value']['discount'] = 0.00
			res['value']['price_subtotal'] = change_amount_discount['price_subtotal']
		elif field_name=='price_subtotal':
			res['value']['tax_amount'] = self._get_count_tax_amount(cr,uid,price_subtotal,taxes)
			
			res['value']['price_subtotal_netto'] = self._get_count_price_subtotal_netto(price_subtotal,res['value']['tax_amount'])
		elif field_name=='invoice_line_tax_id':
			res['value']['tax_amount'] = self._get_count_tax_amount(cr,uid,price_subtotal,taxes)
			
		elif field_name=='tax_amount':
			
			res['value']['price_subtotal_netto'] = self._get_count_price_subtotal_netto(price_subtotal,res['value']['tax_amount'])
		
		return res


	def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		
		res = super(account_invoice_line,self)._amount_line(cr,uid,ids,prop,unknow_none,unknow_dict)
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		# TEST AJA lagi
		res = {}
		tax_obj = self.pool.get('account.tax')
		# cur_obj = self.pool.get('res.currency')
		for line in self.browse(cr, uid, ids):
			if line.amount_discount!=0.0:
				price = line.price_unit - (line.amount_discount/line.quantity)
			elif line.discount!=0.0:
				# amount discount null/0.0 but discount percentage is set,, then system will warn the user to make sure the nominal of discount
				raise osv.except_osv(_('Error!'),_('Discount on percentage is defined but the nominal is not defined,,Please fill the discount on nominal field, based on discount percentage of total price or Contact your System Administrator!'))
			else:
				price = line.price_unit
			
			
			taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			
			res[line.id] = taxes['total']
			if line.invoice_id:
				cur = line.invoice_id.currency_id
				# res[line.id] = cur_obj.round(cr, uid, cur, res[line.id]) #old
				res[line.id] = round(res[line.id],dec_precision)
		return res

	# def _get_price_subtotal_netto(self, cr, uid, ids, prop, unknow_none, unknow_dict):
	# 	print "Calll _get_price_subtotal_netto"
	# 	res = {}
	# 	dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
	# 	tax_obj = self.pool.get('account.tax')
	# 	for line in self.browse(cr, uid, ids):
	# 		print line.price_subtotal_netto,"===="
	# 		if line.amount_discount!=0.0:
	# 			price = line.price_unit - (line.amount_discount/line.quantity)
	# 		elif line.discount!=0.0:
	# 			# amount discount null/0.0 but discount percentage is set,, then system will warn the user to make sure the nominal of discount
	# 			raise osv.except_osv(_('Error!'),_('Discount on percentage is defined but the nominal is not defined,,Please fill the discount on nominal field, based on discount percentage of total price or Contact your System Administrator!'))
	# 		else:
	# 			price = line.price_unit
			
			
	# 		taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
	# 		# print res
	# 		res[line.id] = taxes['total_included']
			
	# 		if line.invoice_id:
	# 			cur = line.invoice_id.currency_id
	# 			res[line.id] = round(res[line.id],dec_precision)

	# 	print res,"SUBTOTAL NETTO"
	# 	return res
	def _get_amount_bruto(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		for item in self.browse(cr,uid,ids,context=context):
			res[item.id] = round(item.quantity*item.price_unit,dec_precision)

		return res

	def _set_amount_bruto(self, cr, uid, id, field_name, field_value, args=None, context={}):
		
		res = {}
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		for item in self.browse(cr,uid,[id],context=context):
			if item.amount_bruto != field_value:
				
				res[item.id] = field_value
				cr.execute("""update account_invoice_line set amount_bruto=%s where id=%s""", (field_value, item.id))
			else:
				res[item.id] = round(item.quantity*item.price_unit,dec_precision)

		return res
	def _set_price_subtotal(self, cr, uid, id, field_name, field_value, args=None, context={}):
		
		res = {}
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		
		for item in self.browse(cr,uid,[id],context=context):
			if item.price_subtotal != field_value:
				
				res[item.id] = field_value
				cr.execute("""update account_invoice_line set price_subtotal=%s where id=%s""", (field_value, item.id))
			else:
				
				res[item.id] = round(item.quantity*item.price_unit,dec_precision)

		return True


	def _set_price_subtotal_netto(self, cr, uid, id, field_name, field_value, args=None, context={}):
		res = {}
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		
		for item in self.browse(cr,uid,[id],context=context):
			if item.price_subtotal_netto != field_value:
				
				
				cr.execute("""update account_invoice_line set price_subtotal_netto=%s where id=%s""", (field_value, item.id))
			else:
				
				res[item.id] = round(item.quantity*item.price_unit,dec_precision)
		
		return True


	def _get_amount_before_tax(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')

		for item in self.browse(cr,uid,ids,context=context):
			
			res[item.id] = round(item.amount_bruto-item.amount_discount,dec_precision)

		return res
	def _get_invoice_line_by_invoice(self, cr, uid, ids, context=None):
		result = {}
		for inv in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
			for line in inv.invoice_line:
				result[line.id] = True
		return result.keys()
	_inherit = 'account.invoice.line'
	_columns = {
		
		'amount_bruto':fields.function(
			# _get_amount_bruto,
			fnct=_get_amount_bruto,
			fnct_inv=_set_amount_bruto,
			string="Amount Total",
			help="Amount bruto, price unit multiply quantity, ammount before discount and taxes / pure total amount",
			type="float",
			store={
				'account.invoice.line':(lambda self, cr, uid, ids, c={}: ids,['price_unit','quantity'],50)
			},
		),
		# 'price_subtotal': fields.function(
		# 	fnct=_amount_line,
		# 	fnct_inv=_set_price_subtotal,
		# 	string='Total (Before Tax)',
		# 	type="float", 
		# 	store={
		# 		'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit','quantity','amount_discount','discount','invoice_line_tax_id','invoice_line_tax_id'], 50),
		# 		'account.invoice': (_get_invoice_line_by_invoice, ['pajak'],50)
		# 	},
		# ),
		# 'price_subtotal_netto': fields.function(
		# 	# method=True,
		# 	fnct=_get_price_subtotal_netto, 
		# 	fnct_inv=_set_price_subtotal_netto,
		# 	string='SubTotal(Netto)',
		# 	type="float",
		# 	# store=True,
		# 	store={
		# 		'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit','quantity','amount_discount','discount','invoice_line_tax_id','tax_amount','invoice_line_tax_id'], 50),
		# 		'account.invoice': (_get_invoice_line_by_invoice, ['pajak'],50)
		# 	},
		# ),

		'amount_discount':fields.float('Amount Discount',required=False),
		# 'amount_before_tax':fields.function(
		# 	_get_amount_before_tax,
		# 	string="Amount Before Tax",
		# 	help="Amount Before Tax, amount total - discount",
		# 	type="float",
		# 	store={
		# 		'account.invoice.line':(lambda self, cr, uid, ids, c={}: ids,['price_unit','quantity'],51)
		# 	},
		# )
	}

# class account_tax(osv.osv):
# 	_inherit = 'account.tax'
# 	def _unit_compute(self, cr, uid, taxes, price_unit, product=None, partner=None, quantity=0):
# 		taxes = self._applicable(cr, uid, taxes, price_unit ,product, partner)
# 		res = []
# 		cur_price_unit=price_unit
# 		for tax in taxes:
# 			# we compute the amount for the current tax object and append it to the result
# 			data = {'id':tax.id,
# 					'name':tax.description and tax.description + " - " + tax.name or tax.name,
# 					'account_collected_id':tax.account_collected_id.id,
# 					'account_paid_id':tax.account_paid_id.id,
# 					'account_analytic_collected_id': tax.account_analytic_collected_id.id,
# 					'account_analytic_paid_id': tax.account_analytic_paid_id.id,
# 					'base_code_id': tax.base_code_id.id,
# 					'ref_base_code_id': tax.ref_base_code_id.id,
# 					'sequence': tax.sequence,
# 					'base_sign': tax.base_sign,
# 					'tax_sign': tax.tax_sign,
# 					'ref_base_sign': tax.ref_base_sign,
# 					'ref_tax_sign': tax.ref_tax_sign,
# 					'price_unit': cur_price_unit,
# 					'tax_code_id': tax.tax_code_id.id,
# 					'ref_tax_code_id': tax.ref_tax_code_id.id,
# 			}
# 			res.append(data)
# 			if tax.type=='percent':
# 				amount = cur_price_unit * tax.amount
# 				data['amount'] = amount

# 			elif tax.type=='fixed':
# 				data['amount'] = tax.amount
# 				data['tax_amount']=quantity
# 				# data['amount'] = quantity
# 			elif tax.type=='code':
# 				localdict = {'price_unit':cur_price_unit, 'product':product, 'partner':partner}
# 				exec tax.python_compute in localdict
# 				amount = localdict['result']
# 				data['amount'] = amount
# 			elif tax.type=='balance':
# 				data['amount'] = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)
# 				data['balance'] = cur_price_unit

# 			amount2 = data.get('amount', 0.0)
# 			if tax.child_ids:
# 				if tax.child_depend:
# 					latest = res.pop()
# 				amount = amount2
# 				child_tax = self._unit_compute(cr, uid, tax.child_ids, amount, product, partner, quantity)
# 				res.extend(child_tax)
# 				if tax.child_depend:
# 					for r in res:
# 						for name in ('base','ref_base'):
# 							if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
# 								r[name+'_code_id'] = latest[name+'_code_id']
# 								r[name+'_sign'] = latest[name+'_sign']
# 								r['price_unit'] = latest['price_unit']
# 								latest[name+'_code_id'] = False
# 						for name in ('tax','ref_tax'):
# 							if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
# 								r[name+'_code_id'] = latest[name+'_code_id']
# 								r[name+'_sign'] = latest[name+'_sign']
# 								r['amount'] = data['amount']
# 								latest[name+'_code_id'] = False
# 			if tax.include_base_amount:
# 				cur_price_unit+=amount2
# 		return res

	# def _unit_compute(self, cr, uid, taxes, price_unit, product=None, partner=None, quantity=0):
	# 	taxes = self._applicable(cr, uid, taxes, price_unit ,product, partner)
	# 	res = []
	# 	dec_precision_tax_line = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
	# 	cur_price_unit=price_unit
	# 	for tax in taxes:
	# 		# we compute the amount for the current tax object and append it to the result
	# 		data = {
	# 			'id':tax.id,
	# 			'name':tax.description and tax.description + " - " + tax.name or tax.name,
	# 			'account_collected_id':tax.account_collected_id.id,
	# 			'account_paid_id':tax.account_paid_id.id,
	# 			'account_analytic_collected_id': tax.account_analytic_collected_id.id,
	# 			'account_analytic_paid_id': tax.account_analytic_paid_id.id,
	# 			'base_code_id': tax.base_code_id.id,
	# 			'ref_base_code_id': tax.ref_base_code_id.id,
	# 			'sequence': tax.sequence,
	# 			'base_sign': tax.base_sign,
	# 			'tax_sign': tax.tax_sign,
	# 			'ref_base_sign': tax.ref_base_sign,
	# 			'ref_tax_sign': tax.ref_tax_sign,
	# 			'price_unit': cur_price_unit,
	# 			'tax_code_id': tax.tax_code_id.id,
	# 			'ref_tax_code_id': tax.ref_tax_code_id.id,
	# 		}
	# 		res.append(data)
			
	# 		if tax.type=='percent':

	# 			amount = cur_price_unit * tax.amount
	# 			data['amount'] = round(amount,dec_precision_tax_line) # TAX / PAJAK
	# 			print data['amount'],'++=+==============++==++==+=++=+=++=+==+==+==++=========='

	# 		elif tax.type=='fixed':
	# 			data['amount'] = tax.amount
	# 			data['tax_amount']=quantity
	# 		   # data['amount'] = quantity
	# 		elif tax.type=='code':
	# 			localdict = {'price_unit':cur_price_unit, 'product':product, 'partner':partner}
	# 			exec tax.python_compute in localdict
	# 			amount = localdict['result']
	# 			data['amount'] = amount
	# 		elif tax.type=='balance':
	# 			data['amount'] = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)
	# 			data['balance'] = cur_price_unit

	# 		amount2 = data.get('amount', 0.0)
			
	# 		if tax.child_ids:
	# 			# print "Printed"
	# 			if tax.child_depend:
	# 				latest = res.pop()
	# 			amount = amount2
	# 			child_tax = self._unit_compute(cr, uid, tax.child_ids, amount, product, partner, quantity)
	# 			res.extend(child_tax)
	# 			if tax.child_depend:
	# 				for r in res:
	# 					for name in ('base','ref_base'):
	# 						if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
	# 							r[name+'_code_id'] = latest[name+'_code_id']
	# 							r[name+'_sign'] = latest[name+'_sign']
	# 							r['price_unit'] = latest['price_unit']
	# 							latest[name+'_code_id'] = False
	# 					for name in ('tax','ref_tax'):
	# 						if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
	# 							r[name+'_code_id'] = latest[name+'_code_id']
	# 							r[name+'_sign'] = latest[name+'_sign']
	# 							r['amount'] = data['amount']
	# 							latest[name+'_code_id'] = False
	# 		if tax.include_base_amount:
	# 			cur_price_unit+=amount2
			
		
	# 	return res

	# def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, force_excluded=False):
	# 	"""
	# 	:param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
	# 		tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
	# 		False
	# 	RETURN: {
	# 			'total': 0.0,                # Total without taxes
	# 			'total_included: 0.0,        # Total with taxes
	# 			'taxes': []                  # List of taxes, see compute for the format
	# 		}
	# 	"""

	# 	# By default, for each tax, tax amount will first be computed
	# 	# and rounded at the 'Account' decimal precision for each
	# 	# PO/SO/invoice line and then these rounded amounts will be
	# 	# summed, leading to the total amount for that tax. But, if the
	# 	# company has tax_calculation_rounding_method = round_globally,
	# 	# we still follow the same method, but we use a much larger
	# 	# precision when we round the tax amount for each line (we use
	# 	# the 'Account' decimal precision + 5), and that way it's like
	# 	# rounding after the sum of the tax amounts of each line

	# 	precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
	# 	tax_compute_precision = precision
	# 	if taxes and taxes[0].company_id.tax_calculation_rounding_method == 'round_globally':
	# 		tax_compute_precision += 5
	# 	totalin = totalex = round(price_unit * quantity, precision)
	# 	# print "TOTAL INNNNNNNNN--->",totalin
	# 	# print "TOTAL EXXXXXXXXX--->",totalex


	# 	# raise osv.except_osv(_('Error!'),_('Error'))
	# 	tin = []
	# 	tex = []
	# 	for tax in taxes:
	# 		if not tax.price_include or force_excluded:
	# 			tex.append(tax)
	# 		else:
	# 			tin.append(tax)
	# 	tin = self.compute_inv(cr, uid, tin, price_unit, quantity, product=product, partner=partner, precision=tax_compute_precision)
	# 	print "TAX INNNNNN--->",tin
	# 	for r in tin:
	# 		totalex -= r.get('amount', 0.0)
	# 	totlex_qty = 0.0
	# 	try:
	# 		totlex_qty = totalex/quantity
	# 	except:
	# 		pass
	# 	tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=tax_compute_precision)
	# 	print "TAX EXXXXXXXXXXX--->",tex
	# 	for r in tex:
	# 		totalin += r.get('amount', 0.0)
	# 	# print "TOTAL INNNNNNNNN--->",totalin
	# 	# print "TOTAL EXXXXXXXXX--->",totalex
		
	# 	# per invoice line taxes total
	# 	# only 1 line
	# 	res = {
	# 		'total': round(totalex,precision),
	# 		'total_included': round(totalin,precision),
	# 		'taxes': tin + tex
	# 	}

	# 	print res,"==<>"
	# 	# raise osv.except_osv(_('Error!'),_('Error'))
	# 	return res


	# def _compute(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
	# 	"""
	# 	Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

	# 	RETURN:
	# 		[ tax ]
	# 		tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
	# 		one tax for each tax id in IDS and their children
	# 	"""
	# 	if not precision:
	# 		precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
	# 	# print precision,"precisionxxxxxxxxxxxxxxxxxxxxxxx"
	# 	res = self._unit_compute(cr, uid, taxes, price_unit, product, partner, quantity)
		
	# 	total = 0.0
	# 	for r in res:
	# 		if r.get('balance',False):
	# 			r['amount'] = round(r.get('balance', 0.0) * quantity, precision) - total
	# 		else:
	# 			r['amount'] = round(r.get('amount', 0.0) * quantity, precision)
	# 			total += r['amount']
	# 		# print r,"RRRRRRRRRRRRRRRRRRRR"

	# 	return res
	
# 	def _unit_compute_inv(self, cr, uid, taxes, price_unit, product=None, partner=None):
# 		taxes = self._applicable(cr, uid, taxes, price_unit,  product, partner)
# 		res = []
# 		taxes.reverse()
# 		cur_price_unit = price_unit

# 		tax_parent_tot = 0.0
# 		for tax in taxes:
# 			if (tax.type=='percent') and not tax.include_base_amount:
# 				tax_parent_tot += tax.amount

# 		for tax in taxes:
# 			if (tax.type=='fixed') and not tax.include_base_amount:
# 				cur_price_unit -= tax.amount

# 		for tax in taxes:
# 			if tax.type=='percent':
# 				if tax.include_base_amount:
# 					amount = cur_price_unit - (cur_price_unit / (1 + tax.amount))
# 				else:
# 					amount = (cur_price_unit / (1 + tax_parent_tot)) * tax.amount

# 			elif tax.type=='fixed':
# 				amount = tax.amount

# 			elif tax.type=='code':
# 				localdict = {'price_unit':cur_price_unit, 'product':product, 'partner':partner}
# 				exec tax.python_compute_inv in localdict
# 				amount = localdict['result']
# 			elif tax.type=='balance':
# 				amount = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)

# 			if tax.include_base_amount:
# 				cur_price_unit -= amount
# 				todo = 0
# 			else:
# 				todo = 1
# 			res.append({
# 				'id': tax.id,
# 				'todo': todo,
# 				'name': tax.name,
# 				'amount': amount,
# 				'account_collected_id': tax.account_collected_id.id,
# 				'account_paid_id': tax.account_paid_id.id,
# 				'account_analytic_collected_id': tax.account_analytic_collected_id.id,
# 				'account_analytic_paid_id': tax.account_analytic_paid_id.id,
# 				'base_code_id': tax.base_code_id.id,
# 				'ref_base_code_id': tax.ref_base_code_id.id,
# 				'sequence': tax.sequence,
# 				'base_sign': tax.base_sign,
# 				'tax_sign': tax.tax_sign,
# 				'ref_base_sign': tax.ref_base_sign,
# 				'ref_tax_sign': tax.ref_tax_sign,
# 				'price_unit': cur_price_unit,
# 				'tax_code_id': tax.tax_code_id.id,
# 				'ref_tax_code_id': tax.ref_tax_code_id.id,
# 			})
# 			if tax.child_ids:
# 				if tax.child_depend:
# 					del res[-1]
# 					amount = price_unit

# 			parent_tax = self._unit_compute_inv(cr, uid, tax.child_ids, amount, product, partner)
# 			res.extend(parent_tax)

# 		total = 0.0
# 		for r in res:
# 			if r['todo']:
# 				total += r['amount']
# 		for r in res:
# 			r['price_unit'] -= total
# 			r['todo'] = 0
# 		return res

# 	def compute_inv(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
# 		"""
# 		Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.
# 		Price Unit is a Tax included price

# 		RETURN:
# 			[ tax ]
# 			tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
# 			one tax for each tax id in IDS and their children
# 		"""
# 		if not precision:
# 			precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
# 		res = self._unit_compute_inv(cr, uid, taxes, price_unit, product, partner=None)
# 		total = 0.0
# 		for r in res:
# 			if r.get('balance',False):
# 				r['amount'] = round(r['balance'] * quantity, precision) - total
# 			else:
# 				r['amount'] = round(r['amount'] * quantity, precision)
# 				total += r['amount']
# 		return res
