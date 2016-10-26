from datetime import datetime
from stock import stock
import math
import time
import webbrowser
import netsvc
from datetime import datetime
import openerp.exceptions
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import re

class acount_invoice(osv.osv):
	_inherit = 'account.invoice'
	_columns = {
		'tax_transaction_type':fields.selection([('01','01 - To Non Tax Collector'),('02','02 - To Treasurer Collector'),('03','03 -To Non Treasurer Collector'),('04','04 - Other Base Tax Amount'),('06','06 - Other Referral'),('07','07 - Non Paid Referral'),('08','08 - Free Tax Referral'),('09','09 - Activa Referral')],string="Tax Transaction Type"),
		'is_tax_replacement':fields.boolean('Is a Tax Replacement'),
		'tax_no_1':fields.char('Tax No 1',size=3),
		'tax_year':fields.char('Year',size=4),
		'tax_no_2':fields.char('Tax No 2',size=8),
		# 'partner_id':fields.many2one('res.partner','Custo mer',domain=['|','|',('customer','=', True),('is_company','=','True'),('child_ids.type','=','Invoice')])
	}

	def _get_default_tax_no_1(self,cr,uid,ids,context=None):
		res = False
		print context
		print "+"*200
		# browsed = self.browse(cr, uid, ids, context=context)
		
		# if browsed:
		# 	if type(browsed) == list:
		# 		res = {}
		# 		for s in browsed:
		# 			# 010.031-16.1914197
		# 			if s.faktur_pajak_no:
		# 				res[s.id] = s.faktur_pajak_no[4:3]
		# 			else:
		# 				res[s.id] = None
		# 	else:
		# 		res = browsed.faktur_pajak_no[4:3]
		
		return res

	def _get_default_tax_year(self, cr, uid, context=None):
		res = False
		print context
		print "="*200
		# browsed = self.browse(cr, uid, ids, context=context)
		
		# if browsed:
		# 	if type(browsed) == list:
		# 		res = {}
		# 		for s in browsed:
		# 			if s.date_invoice:
		# 				date_invoice = datetime.strptime(s.date_invoice,'%Y-%m-%d')
		# 				res[s.id] = date_invoice.year
		# 	else:
		# 		if date_invoice:

		# 			date_invoice = datetime.strptime(browsed.date_invoice,'%Y-%m-%d')
		# 			res = date_invoice.year
		
		return res

	def _get_default_tax_no_2(self, cr, uid, context=None):
		res = False
		print context
		print "-"*200
		# browsed = self.browse(cr, uid, ids, context=context)
		
		# if browsed:
		# 	if type(browsed) == list:
		# 		res = {}
		# 		for s in browsed:
		# 			res[s.id] = None
		# 			# 010.031-16.19141977
		# 			if s.faktur_pajak_no:
		# 				res[s.id] = s.faktur_pajak_no[11:8]
		# 	else:
		# 		res = browsed.faktur_pajak_no[4:3]
		
		return res


	def _get_default_is_tax_replacement(self, cr, uid, context=None):
		print context
		print "."*200
		res = False
		# browsed = self.browse(cr, uid, ids, context=context)
		
		# if browsed:
		# 	if type(browsed) == list:
		# 		res = {}
		# 		for s in browsed:
		# 			# 010.031-16.19141977
		# 			if s.faktur_pajak_no:
		# 				if s.faktur_pajak_no[3:1]==1:
		# 					res[s.id] = True
		# 				else:
		# 					res[s.id] = False
					
		# 	else:
		# 		if browsed.faktur_pajak_no:
		# 			if browsed.faktur_pajak_no[3:1]==1:
		# 				res = True
		return res

	_defaults={
		
		'tax_transaction_type':'01',
		'tax_no_1':_get_default_tax_no_1,
		'tax_no_2':_get_default_tax_no_2,
		'is_tax_replacement':_get_default_is_tax_replacement,
		'tax_year':_get_default_tax_year,
	}


	def _set_tax_year(self,cr,uid,ids,context={}):
		return False

	def onchange_date_invoice(self,cr,uid,ids,date_invoice,is_tax_replacement='01',tax_no_2=False,need_date=True):
		res={}
		print "++++++++++++++++++++++++++++++++++++++++++++++++====================================================="
		print date_invoice,"---",uid,"----",ids
		print is_tax_replacement
		print need_date, "<<<<<<<<<<<<<<<<<<"
		tax_no_2 = tax_no_2 or '00000000'
		if date_invoice:
			month_tax = str(date_invoice[5:-3])
			print month_tax
			# tax_year_res = tax_year[-2:]
			if month_tax =='01':
				month_tax='I'
			elif month_tax == '02':
				month_tax='II'
			elif month_tax=='03':
				month_tax='III'
			elif month_tax=='04':
				month_tax='IV'
			elif month_tax=='05':
				month_tax='V'
			elif month_tax=='06':
				month_tax='VI'
			elif month_tax=='07':
				month_tax='VII'
			elif month_tax=='08':
				month_tax='VIII'
			elif month_tax=='09':
				month_tax='IX'
			elif month_tax=='10':
				month_tax='X'
			elif month_tax=='11':
				month_tax='XI'
			elif month_tax=='12':
				month_tax='XII'
			print str(date_invoice[-2:])
			res['value'] ={
			'tax_year':str(date_invoice[:4]),
			'kwitansi':tax_no_2+'/'+'SBM'+'/'+month_tax+'/'+str(date_invoice[:4])
			}
		else:
			if need_date:
				print "AAAAAAAAAAAAAAAAA"
				raise osv.except_osv(_('Warning'),_('Select Invoice Date'))
		return res

	def onchange_format_faktur(self, cr, uid, ids, no):
		# filter dulu no ,, buang selain string nomor
		print no
		# no = '01.00.00-29301200'
		# my_list = []
		
		# for filterno in no:     # First Example
		#    print 'Current Letter :', filterno
		#    if filterno == '0' or filterno == '1' or filterno == '2' or filterno == '3' or filterno == '4' or filterno == '5' or filterno == '6' or filterno == '7' or filterno == '8' or filterno == '9':
		# 	    my_list.append(filterno)
		# print my_list
		# no = ''.join(str(e) for e in my_list)
		# no = no.replace('-','').replace('.','')
		


		no = re.sub(r'\D','',no)
		# print "=============================================================="


		try:
			int(no)
			if len(no) == 16:
				value = list(no)
				value.insert(3, '.')
				value.insert(7, '-')
				value.insert(10, '.')
				result = "".join(value)
				return {'value': {'faktur_pajak_no': result}}      
			else:
				return {'warning': {"title": _("Perhatian"), "message": _("Nomor faktur pajak harus 16 digit")}, 'value': {'faktur_pajak_no': False}}
		except:
			return {'warning': {"title": _("Perhatian"), "message": _("Masukan 16 digit angka tanpa separator")}, 'value': {'faktur_pajak_no': False}}


	def onchange_tax_no(self,cr,uid,ids,date_invoice,tax_transaction_type,is_tax_replacement,tax_no_1,tax_year,tax_no_2,need_date=True):
		
		res={}
		if is_tax_replacement:
			tax_replacement_str ="1"
		else:
			tax_replacement_str = "0"

		tax_no_1 = tax_no_1 or '000'
		tax_year = tax_year or '00'
		tax_no_2 = tax_no_2 or '00000000'
		# filteryear = False
		print need_date
		print tax_transaction_type,"<<<<<<<<<<<<<<<<<<<<type"
		print tax_replacement_str,"replace"
		print tax_no_1,"no1"
		print tax_year,"year"
		print tax_no_2,"no2"
		if tax_transaction_type == False:
			raise osv.except_osv(_('Warning'),_('Tax Transaction Type Tidak Boleh Kosong'))


		if date_invoice:
			month_tax = str(date_invoice[5:-3])
			print month_tax
			tax_year_res = tax_year[-2:]
			if month_tax =='01':
				month_tax='I'
			elif month_tax == '02':
				month_tax='II'
			elif month_tax=='03':
				month_tax='III'
			elif month_tax=='04':
				month_tax='IV'
			elif month_tax=='05':
				month_tax='V'
			elif month_tax=='06':
				month_tax='VI'
			elif month_tax=='07':
				month_tax='VII'
			elif month_tax=='08':
				month_tax='VIII'
			elif month_tax=='09':
				month_tax='IX'
			elif month_tax=='10':
				month_tax='X'
			elif month_tax=='11':
				month_tax='XI'
			elif month_tax=='12':
				month_tax='XII'
				date_invoice[2:-6]
			res ['value'] ={
				
				'faktur_pajak_no':tax_transaction_type+tax_replacement_str+tax_no_1+tax_year_res+tax_no_2,
				'kwitansi':tax_no_2+'/'+'SBM'+'/'+month_tax+'/'+str(date_invoice[:4])
				# 'kwitansi':tax_no_2
			}

			#mengecek tax no 1
			tax_no_1 = re.sub(r'\D','',tax_no_1)
			if len(tax_no_1) < 3:
				
				raise osv.except_osv(_('Warning'),_('Tax No 1 harus 3 karakter dan merupakan angka'))
			tax_no_2 = re.sub(r'\D','',tax_no_2)
			if len(tax_no_2) < 8:
				
				raise osv.except_osv(_('Warning'),_('Tax No 2 harus 8 karakter dan merupakan angka'))
			

			
			tax_year = re.sub(r'\D','',tax_year)
			if len(tax_year) < 4 or int(tax_year) > 2030 or int(tax_year) <1900:
				
				res ['value'] ={
				
				'tax_year':str(date_invoice[:4])
				
			}
				
		else:
			tax_year = re.sub(r'\D','',tax_year)
			if tax_year == "":
				tax_year="0"
				tax_year = re.sub(r'\D','',tax_year)
			# mengecek tax year
			if len(tax_year) < 4 or int(tax_year) > 2030 or int(tax_year) <1900 :
				
				res ['value'] ={
				
				'tax_year':""
				
			}
			#mengecek tax no 1
			tax_no_1 = re.sub(r'\D','',tax_no_1)
			if len(tax_no_1) < 3:
				
				raise osv.except_osv(_('Warning'),_('Tax No 1 harus 3 karakter dan merupakan angka'))

			tax_no_2 = re.sub(r'\D','',tax_no_2)
			if len(tax_no_2) < 8:
				
				raise osv.except_osv(_('Warning'),_('Tax No 2 harus 8 karakter dan merupakan angka'))
			

			if need_date:
				# res ['value'] ={
				
				# 'tax_year':""
				# }
				print "AAAAAAAAAAAAAAAAA"
				# raise osv.except_osv(_('Warning'),_('Select Invoice Date'))
				res['warning'] ={
					'title':'WARNING',
					'message':'PLEASE SELECT INVOICE DATE BEFORE DOING THIS !!!'
				}
		print res
		
		return res

class account_invoice_line(osv.osv):
	_inherit = 'account.invoice.line'

	def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
		if context is None:
			context = {}
		# print product,"<<<<<<product"
		# print uom,"<<<<<<<<<<<<<uos_id"
		# print qty,"<<<<<<<<quantity"
		product_obj = self.pool.get('product.product').browse(cr,uid,product,context=context) #dapetin product berdasarkan product id
		product_uom = self.pool.get('product.uom').browse(cr,uid,uom,context=context) #dapetin product berdasarkan product id
		
		# print product_obj.name, " namaaa product"
		# print product_uom.name, " namaaa uom baru"
		# print product_obj.uom_id.name, " namaaa uom"
		# print product_obj.uos_id.category_id, " namaaa uos category"
		# print product_obj.uom_id.category_id.name, " namaaa category" 
		# print product_obj.default_code, "defaulll code"
		# print product_obj.sale_delay, "defaulll code"

		if product and uom:
			# 1. data uos_id ,product_obj.uos_id , kategori uom , kategori product
			# 2. jika ketegori uos = kategori uom product atau jika uos_id = product_obj.uos_id maka print boleh.
			# 3. jika tidak maka print tidak boleh
			print product_uom.category_id.id , ":" , product_obj.uom_id.category_id.id
			print "======================================="
			print uom ,':', product_obj.uos_id.id
			if product_uom.category_id.id == product_obj.uom_id.category_id.id or uom == product_obj.uos_id.id:
				return True
			else:
				warning={
					'title':'Warning',
					'message':'The selected unit of measure is not compatible with the unit of measure of the product.'
				}
				return {'warning': warning}
		return True

