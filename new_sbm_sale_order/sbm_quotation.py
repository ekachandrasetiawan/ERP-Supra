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

class Sale_order(osv.osv):	
	_inherit ='sale.order'

	# def _count_total(self,cr,uid,ids,fields_name,args,context={}):
	# 	res={}
	# 	order_line = self.browser(cr,uid,ids,context=context)
	# 	print order_line,"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	# 	# for line in order_line:
	# 	# 	print line ,"oaooooo+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	# 	# 	res[line.id] = {
	# 	# 	"base_total":2323,
	# 	# 	}
		
	# 	return res

	# def write(self, cr, uid, ids, vals, context=None):

	# 	print "---------------------------------------"
	# 	print super(Sale_order, self).write(cr, uid, ids, vals, context=context),"cobaaaaa di test save nya"
	# 	print "---------------------------------------"
	# 	return super(Sale_order, self).write(cr, uid, ids, vals, context=context)


	def _count_total(self, cr, uid, ids, name, args, context={}):
		print "PANGGIL _COUNT_TOTAL"
		res = {}
		print "cobaaa di baca"
		print res,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<==============================================="
		sale_order = self.browse(cr,uid,ids,context=context)
		print sale_order
		total_base_total=0
		for i in sale_order:
			for r in i.order_line:
				print r.id,"-----",r.base_total
				total_base_total += r.base_total
			res[i.id] = {"base_total":total_base_total,}
		print total_base_total
		return res

	def _count_tax(self,cr,uid,ids,fields_name,args,context={}):
		res={}
		return res

	def _inv_base_total(self,cr,uid,ids,fields_name,args,context={}):
		res={}
		return res
	def _get_so_line_by_so(self,cr,uid,ids,context={}):
		res = {}
		for line in self.pool.get('sale.order.line').browse(cr,uid,ids,context=context):
			res[line.order_id.id]=True
		return res.keys()

	_columns = {
		'quotation_no':fields.char(required=True,string='Quotation#'),
		'base_total':fields.function(
			_count_total,
			string='Base Total',
			type="float",
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 20),
				'sale.order.line': (_get_so_line_by_so, ['price_unit','product_uom_qty'], 20),
			},
			multi="line_total"
		),

		'quotation_state':fields.selection([('draft','Draft'),('confirmed','Confirmed'),('win','Win'),('lost','Lost'),('cancel','Cancel')],string="Quotation State"),
		'cancel_stage':fields.selection([('internal user fault','Internal User Fault'),('external user fault','External User Fault'),('lose','Lose')]),
		'cancel_message':fields.text(string="Cancel Message"),
		'revised_histories':fields.one2many('sale.order.revision.history','sale_order_id')
	}
	_sql_constraints = [
		('quotation_no_unique', 'unique(quotation_no)', 'The quotation_no must be unique !')
		]
	_defaults={
		
		'quotation_state':'draft'
	}

	def confirm_quotation(self,cr,uid,ids,context={}):
		res = False
		quotation_obj = self.pool.get("sale.order")
		data_sekarang = self.browse(cr,uid,ids,context=context)[0]
		if data_sekarang.order_line	==[]:
			quotation_obj.write(cr,uid,ids,{'quotation_state':'draft'},context=context)
			raise osv.except_osv(_('Warning'),_('Order Cant be confirmed'))
		else:
			for line in data_sekarang.order_line:
				if line.material_lines==[]:
					quotation_obj.write(cr,uid,ids,{'quotation_state':'draft'},context=context)
					raise osv.except_osv(_('Warning'),_('Order Cant be confirmed'))
		if data_sekarang.quotation_state == 'draft':
			if quotation_obj.write(cr,uid,ids,{'quotation_state':'confirmed'},context=context):
				res = True
		else:
			raise osv.except_osv(_('Warning'),_('Order Cant be confirmed'))

		return res

	def cancel_quotation(self,cr,uid,ids,context={}):
		res = False
		quotation_obj = self.pool.get("sale.order")
		data_sekarang = self.browse(cr,uid,ids,context=context)[0]

		if data_sekarang.quotation_state == 'draft':
			if quotation_obj.write(cr,uid,ids,{'quotation_state':'cancel'},context=context):
				res = True
		else:
			raise osv.except_osv(_('Warning'),_('Order Cant be Cancel'))

		return res

# <record model='ir.actions.act_window' id="wizard_lost_quotation_form">
# 			<field name="name">wizard.lost.quotation.form</field>
# 			<field name="type">ir.actions.act_window</field>
# 			<field name="res_model">wizard.lost.quotation</field>
# 			<field name="view_type">form</field>
# 			<field name="view_mode">form</field>
# 			<field name="view_id" ref="lost_quotation_wizard"/>
# 			<field name="target">new</field>
# 		</record>


	# def wizard_lost_quotation_form(self,cr,uid,ids,context={}):
	# 	dir={
	# 		"name":"wizard.lost.quotation.form",
	# 		"type":"ir.actions.act_window",
	# 		"res_model":"wizard.lost.quotation",
	# 		"view_type":"form",
	# 		"view_mode":"form",
	# 		"view_id ref=lost_quotation_wizard",
	# 		"target":"new"


	# 	}

	# 	return dir

class sale_order_material_line(osv.osv):


	_name = 'sale.order.material.line'
	_description = 'Sale order material line'
	_columns = {
		'sale_order_line_id':fields.many2one('sale.order.line',string="Sale Order Line"),
		'product_id':fields.many2one('product.product',string="Product", required=True, domain=[('sale_ok','=','True'),('categ_id.name','!=','LOCAL')], active=True),
		'desc':fields.text(string="Description"),
		'qty':fields.float(string="Qty",required=True),
		'uom':fields.many2one("product.uom",required=True,string="uom"),
		'picking_location':fields.many2one('stock.location',required=True)
		}

	def _get_ho_location(self,cr,uid,ids,context={}):
		test_obj = self.pool.get("sale.order")
		
		# print ["file.sql",],"aaaaaaaaaaaaaa"
		# return False
		
# def default_get(self, cr, uid, picking_location, context=None):
#    		 data = super(sale_order_material_line, self).default_get(cr, uid, picking_location, context=context)
#    		 data['picking_location']=64
#    		 return data

	# 	# product_obj = cr.execute('SELECT "id" FROM "stock_location" where "name" like "HO" ')

	# 	# args=["HO"]
	# 	# sql='SELECT id FROM stock_location WHERE name IN (%s)' 
	# 	# in_p=', '.join(list(map(lambda x: '%s', args)))
	# 	# sql = sql % in_p
	# 	# product_obj = cr.execute(sql, args)
	# 	# print product_obj,"aaaaaaaaaaaaaaaaaaaaaaaaaa"
		
		# args=['%HO%']
		# sql='SELECT id FROM stock_location WHERE name like (%s)' 
		# # name=', '.join(map(lambda x: '%s', args))
		# # sql = sql % name
		# product_obj = cr.execute(sql, args)

		# cari id dari stock.location where name like 'HO'
		seq_id = self.pool.get('stock.location').search(cr, uid, [('name','=','HO')]) 
		return seq_id
	_defaults={
		
		'picking_location':_get_ho_location,
		'qty':1

	}
	def onchange_product_material(self,cr,uid,ids,product_id):
		res={}
		if product_id:
			product= self.pool.get('product.product').browse(cr,uid,product_id,{})
			res["value"]={
			"uom":product.uom_id.id
			}

		print res 
		return res

	def onchange_product_uom(self,cr,uid,ids,product_id,uom,context={}):
		res ={}
		if product_id:
				
			product = self.pool.get("product.product").browse(cr,uid,product_id,context=context)
			product_uom_browse = self.pool.get("product.uom").browse(cr,uid,uom,context=context)
			
			kategori_uom_product = product.uom_id.category_id.id
			Kategori_uom =product_uom_browse.category_id.id
			# print Kategori_uom	,"<<<<<<<<<<<<<<<<<<<<<<<<"
			if uom:
				if Kategori_uom != kategori_uom_product :
					if uom != product.uos_id.id:
						res["value"]={"uom":product.uom_id.id}
						res['warning']={'title':"Error",'message':'Kategori Uom Harus sama'}

		
				# return res
				# raise osv.except_osv(_('Warning'),_('Kategori Uom Harus sama'))

		return res
	


class sale_order_line(osv.osv):	
	_inherit ='sale.order.line'
	def _count_base_total(self,product_uom_qty,price_unit):
		
		return product_uom_qty*price_unit
	def _count_discount_nominal(self,base_total,discount):
		return base_total * discount/100.0
	def _count_price_subtotal(self,base_total,discount_n):
		return base_total-discount_n
	"""
	@tax_ids harus diisi sama list yang isinya integer id tax cth: [1,2,3,4,5]
	"""
	def _count_amount_tax(self,cr,uid,subtotal,tax_ids):
		list_tax = tax_ids
		amount_tax_total=0
				
		for i in list_tax:
			tax_bro = self.pool.get("account.tax").browse(cr,uid,i)
		
			amount_tax= subtotal* tax_bro.amount
			amount_tax_total+=amount_tax
		
		return amount_tax_total

	def _count_amount_line(self, cr, uid, ids, name, args, context={}):
		print "PANGGIL _count_amount_line"
		res = {}
		order_lines = self.browse(cr,uid,ids,context=context)
		
		for line in order_lines:
			
			base_total	= self._count_base_total(line.product_uom_qty,line.price_unit)
			discount_n = self._count_discount_nominal(base_total,line.discount)
			subtotal_ = self._count_price_subtotal(base_total,discount_n)
			list_tax_id	= []
			for t in line.tax_id:
				
				list_tax_id.append(t.id)
			taxes_total= self._count_amount_tax(cr,uid,subtotal_,list_tax_id)
			
			res[line.id] = {"base_total":base_total,
							"discount_nominal":discount_n,
							"price_subtotal":subtotal_,
							"amount_tax":taxes_total}

						

		return res
	_columns = {
		'base_total':fields.function(
			_count_amount_line,
			type="float",
			store={
				'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit','product_uom_qty'], 1),

			},
			string="Base Total",
			multi="line_total"
		),
		'amount_tax':fields.function(
			_count_amount_line,
			type="float",
			store={
				'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, ['base_total','tax_id'], 1),
			},
			string="Tax Amount",
			multi="line_total"
			),		
		'material_lines':fields.one2many('sale.order.material.line','sale_order_line_id')		
	}




	
	def onchange_price_unit(self,cr,uid,ids,product_uom_qty,price_unit,discount,discount_nominal,tax_id):
		res={
			'base_total':0.0,
			'discount_nominal':0.0,
			'price_subtotal':0.0,
			'amount_tax':0.0
		}
		
		if product_uom_qty and price_unit:
			base_total	= self._count_base_total(product_uom_qty,price_unit)
			discount_n = self._count_discount_nominal(base_total,discount)
			subtotal_ = self._count_price_subtotal(base_total,discount_n)
			taxes_total = self._count_amount_tax(cr,uid,subtotal_,tax_id[0][2])
			res["value"]={
				"base_total":base_total,
				"discount_nominal":discount_n,
				"price_subtotal":subtotal_,
				"amount_tax":taxes_total
			}
		return res

	def onchange_diskon(self,cr,uid,ids,product_uom_qty,price_unit,discount,discount_nominal,tax_id):
		res={
			'base_total':0.0,
			'discount_nominal':0.0,
			'price_subtotal':0.0,
			'amount_tax':0.0
			}
		if product_uom_qty and price_unit:
			base_total	= self._count_base_total(product_uom_qty,price_unit)
			discount_n = discount_nominal
			subtotal_ = self._count_price_subtotal(base_total,discount_n)
			
			taxes_total = self._count_amount_tax(cr,uid,subtotal_,tax_id[0][2])
			# taxes_total = self._count_amount_tax(subtotal_,tax_id)
			res["value"]={
						"base_total":base_total,
						"price_subtotal":subtotal_,
						"amount_tax":taxes_total
						}
		return res

	def loadBomLine(self,cr,uid,bom_line,product_uom_qty,product_uom,seq_id):
		res = {}
		print bom_line, 
		print bom_line.product_id.id, "iddd" 
		res = {
				'product_id':bom_line.product_id.id,
				'uom':bom_line.product_uom.id,
				'qty':product_uom_qty*bom_line.product_qty,
				'picking_location':seq_id,
				
		}
		return res

	def loadBomLineqty(self,cr,uid,product_id,product_uom_qty,product_uom,seq_id,base_total,discount_n,subtotal_,taxes_total):
		res = {}
		res = {
				'product_id':product_id.product_id.id,
				'uom':product_id.product_uom.id,
				'qty':product_uom_qty*product_id.product_qty,
				'picking_location':seq_id,
				"base_total":base_total,
				"price_subtotal":subtotal_,
				"amount_tax":taxes_total
				}
		return res

	def onchange_product_quotation(self,cr,uid,ids,product_id,product_uom_qty,product_uom):
		res={}
		if product_id:
			seq_id = self.pool.get('stock.location').search(cr, uid, [('name','=','HO')])

			if len(seq_id):
				seq_id = seq_id[0]

			product= self.pool.get('product.product').browse(cr,uid,product_id,{})
			
			if product.bom_ids:	
				bom_line_set = self.pool.get('mrp.bom').browse(cr,uid,product.bom_ids[0].id)

				res['value'] = {
					'material_lines':[(0,0,self.loadBomLine(cr,uid,bom_line,product_uom_qty,product_uom,seq_id)) for bom_line in bom_line_set.bom_lines],
					"product_uom":product.uom_id.id
				}

			else:

				res['value'] = {
					'material_lines': [
						(0,0,{'product_id':product_id,'qty':product_uom_qty,'uom':product.uom_id.id,'picking_location':seq_id}),
					],
					"product_uom":product.uom_id.id
				}



	
		print res 
		return res

	

	def onchange_product_uom(self,cr,uid,ids,product_id,product_uom,context={}):
		res ={}
		if product_id:
				
			product = self.pool.get("product.product").browse(cr,uid,product_id,context=context)
			product_uom_browse = self.pool.get("product.uom").browse(cr,uid,product_uom,context=context)
			print "LLLLLLLLLLLLLl"
			kategori_uom_product = product.uom_id.category_id.id
			Kategori_uom =product_uom_browse.category_id.id
			# print Kategori_uom	,"<<<<<<<<<<<<<<<<<<<<<<<<"
			if product_uom:
				if Kategori_uom != kategori_uom_product :
					if product_uom != product.uos_id.id:
						res["value"]={"product_uom":product.uom_id.id}
						res['warning']={'title':"Error",'message':'Kategori Uom Harus sama'}

		
				# return res
				# raise osv.except_osv(_('Warning'),_('Kategori Uom Harus sama'))

		return res
	
	def onchange_product_quotation_qty(self,cr,uid,ids,product_id,product_uom_qty,product_uom,price_unit,discount,tax_id,material_lines_object,context={}):
		res={}
		print ids,"ini id nya"
		if product_uom_qty == False or product_uom_qty<1:
			res["warning"]={'title':"Error",'message':'Quantity not null'}
			res['value'] = {
								
								"product_uom_qty":1
							}
		else:


				if product_id:
					base_total	= self._count_base_total(product_uom_qty,price_unit)
					discount_n = self._count_discount_nominal(base_total,discount)
					subtotal_ = self._count_price_subtotal(base_total,discount_n)
			
					taxes_total = self._count_amount_tax(cr,uid,subtotal_,tax_id[0][2])
					seq_id = self.pool.get('stock.location').search(cr, uid, [('name','=','HO')])

					if len(seq_id):
						seq_id = seq_id[0]
					product= self.pool.get('product.product').browse(cr,uid,product_id,{})
			
					if product.bom_ids:	
						array_material = []
						
						bom_line_set = self.pool.get('mrp.bom').browse(cr,uid,product.bom_ids[0].id)
						all_values_with_bom= [(0,0,self.loadBomLineqty(cr,uid,product_id,product_uom_qty,product_uom,seq_id,base_total,discount_n,subtotal_,taxes_total)) for product_id in bom_line_set.bom_lines]
					
						for material in material_lines_object:
							tidak_sama = True
							if material[2]:
								
								for s in all_values_with_bom:
									if material[2]['product_id'] == s[2]['product_id']:
										tidak_sama=False
										break
								if tidak_sama:
									array_material.append(material[2]),
									all_values_with_bom.append((0,0,material[2]))
								

							else:
								if ids:

									self_browse_line = self.browse(cr,uid,ids,context=context)[0]
									for material_browse in self_browse_line.material_lines:
										tidak_sama_cek = True
										for a in all_values_with_bom:
										
											if material_browse.product_id.id == a[2]['product_id']:
												tidak_sama_cek = False
												break
										if tidak_sama_cek:
											all_values_with_bom.append((0,0,{'product_id':material_browse.product_id.id,'qty':material_browse.qty,'uom':material_browse.uom.id,'picking_location':seq_id}))

											
									# if tidak_sama_cek:
									# 	# array_material.append(material[2]),
									# 	# print material[2],"aaaaaaa"
									# 	all_values_with_bom.append((0,0,material_browse.product_id.id))




							# if material[2]:
								
								# for s in all_values_with_bom:
								# 	if material[2]['product_id'] == s[2]['product_id']:
								# 		print  material[2]['product_id'],"=",s[2]['product_id']
								# 		tidak_sama=False
								# 		break
								# if tidak_sama:
								# 	array_material.append(material[2]),
								# 	print material[2],"aaaaaaa"
								# 	all_values_with_bom.append((0,0,material[2]))






								
						
						print all_values_with_bom,"dicobaaaa dulu bosssss"
						res['value'] = {
								'material_lines':all_values_with_bom,
								"base_total":base_total,
								"price_subtotal":subtotal_,
								"amount_tax":taxes_total
		
						}

						# res['value'].update = {'material_lines': [
						# 			(0,0,{'product_id':product_id,'qty':555,'uom':product_uom,'picking_location':seq_id}),
						# 							]}
					else:
						all_values_without_bom = []
						all_values_without_bom.append((0,0,{'product_id':product_id,'qty':product_uom_qty,'uom':product_uom,'picking_location':seq_id})) 
						for material in material_lines_object:
							tidak_sama = True
							if material[2]:
								
								for s in all_values_without_bom:
									if material[2]['product_id'] == s[2]['product_id']:
										tidak_sama=False
										break
								if tidak_sama:
									all_values_without_bom.append((0,0,material[2]))
								

							else:
								if ids:

									self_browse_line = self.browse(cr,uid,ids,context=context)[0]
									for material_browse in self_browse_line.material_lines:
										tidak_sama_cek = True
										for a in all_values_without_bom:
										
											if material_browse.product_id.id == a[2]['product_id']:
												tidak_sama_cek = False
												break
										if tidak_sama_cek:
											all_values_without_bom.append((0,0,{'product_id':material_browse.product_id.id,'qty':material_browse.qty,'uom':material_browse.uom.id,'picking_location':seq_id}))

											
						res['value'] = {
								'material_lines': all_values_without_bom,
								"base_total":base_total,
								"price_subtotal":subtotal_,
								"amount_tax":taxes_total
							}
		# self.subtotal(cr,uid,ids,product_uom_qty,price_unit,discount_nominal)
		
		return res

	