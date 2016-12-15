from datetime import datetime
from stock import stock
from openerp.osv import fields, orm
import math
import time
import decimal
import webbrowser
import netsvc
import openerp.exceptions
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

		
class inherit_stock_picking_out(osv.osv):
	_inherit = "stock.picking.out"
	_columns = {
			'invoice_id': fields.many2one('account.invoice','Invoice')
		}

class res_partner_extention(osv.osv):
	_inherit = 'res.partner'

	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		res = []
		results = super(res_partner_extention,self).name_get(cr, uid, ids, context)
		tmp = 0
		for index, result in results:
			record_partner = self.browse(cr,uid,index,context=context) #siapin data object
			tmp = index
			if record_partner.city:
				city=" "+record_partner.city
			else:
				city=""
			if record_partner.state_id:
				state_id=" "+record_partner.state_id.name
			else:
				state_id=""

			if context.get('address_attention') or context.get('search_default_filter_confirm'):

				res_name = "%s"%(record_partner.name)
				res.append((index,res_name))

			elif context.get('address_delivery'):
				
				res_name = "%s"%(record_partner.name)+city+state_id+"\n"+ self._display_address(cr, uid, record_partner, without_company=True, context=context)
				res_name = res_name.replace('\n\n','\n')
				res_name = res_name.replace('\n\n','\n')
				
				res.append((index,res_name))
			elif context.get('address_invoice'):
				res_name = "%s"%(record_partner.name)+city+state_id
				res.append((index,res_name))
			else:
				res.append((index,result))

		return res


class Sale_order(osv.osv):	
	_name ='sale.order'
	_inherit =['sale.order','mail.thread']

	def write(self,cr,uid,ids,vals,context={}):
		if type(ids) ==list:
			val = self.browse(cr, uid, ids, context={})[0]
		else:
			val = self.browse(cr, uid, ids, context={})

		m  = self.pool.get('ir.model.data')
		id_group = m.get_object(cr, uid, 'base', 'group_admin_support').id
		id_group_regional = m.get_object(cr, uid, 'sbm_inherit', 'group_sales_admin_regional').id

		user_group = self.pool.get('res.groups').browse(cr, uid, [id_group,id_group_regional])

		id_group_ho = m.get_object(cr, uid, 'sbm_order_handler', 'group_admin_ho').id
		user_group_ho = self.pool.get('res.groups').browse(cr, uid, id_group_ho)

		status = False
		
		if user_group:
			for x in user_group.users:
				if uid == x.id:
					status = True

		if user_group_ho:
			for y in user_group_ho.users:
				if uid == y.id:
					status = True
		if val.quotation_state == 'confirmed' and status == False:
			raise osv.except_osv(('Warning..!!'), ('User Not Access Edit Quotation'))

		return super(Sale_order, self).write(cr, uid, ids, vals, context=context)

	def action_cancel(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		self.write(cr,uid,val.id,{'quotation_state':'cancel'})

		return super(Sale_order, self).action_cancel(cr, uid, ids, context=None)

	def copy_pure_quotation(self,cr,uid,ids,context=None):
		rec = self.browse(cr,uid,ids,context)[0]
		isi_line = []
				
		for line in rec.order_line:
			isi_tax = []
			tax_ids = []
			change_prouct = self.pool.get('sale.order.line').onchange_product_quotation(cr, uid, [line.id], line.product_id.id, line.product_uom_qty, line.product_uom)['value'];
			for taxid in line.tax_id:
				tax_ids.append(taxid.id)
			
			isi_material=[]
			for material in line.material_lines:
				isi_material.append((0,0,
					{
					'product_id':material.product_id.id,
					'desc':material.desc,
					'qty':material.qty,
					'uom':material.uom.id,
					'picking_location':material.picking_location.id
					}))
			if len(isi_material)==0:
				
				isi_material = change_prouct['material_lines']

				_logger.error((change_prouct,"............>>>>",isi_material))

			isi_line.append((0,0,
				{
				'product_id':line.product_id.id,
				'name':line.name,
				'product_uom_qty':line.product_uom_qty,
				'tax_id':[(6,0,tax_ids)],
				'material_lines':isi_material,
				'product_uom':line.product_uom.id
				}))

		prepareNewSO = {
			'origin':rec.origin,
			'order_policy':rec.order_policy,
			'client_order_ref':rec.client_order_ref,
			'partner_id':rec.partner_id.id,
			'date_order':rec.date_order,
			'note':rec.note,
			'user_id':rec.user_id.id,
			'payment_term':rec.payment_term.id,
			'company_id':rec.company_id.id,
			'state':'draft',
			'partner_shipping_id':rec.partner_shipping_id.id,
			'picking_policy':rec.picking_policy,
			'incoterm':rec.incoterm.id,
			'carrier_id':rec.carrier_id.id,
			'worktype':rec.worktype,
			'week':rec.week,
			'attention':rec.attention.id,
			'internal_notes':rec.internal_notes,
			'project_id':rec.project_id.id,
			'pricelist_id':rec.pricelist_id.id,
			'partner_invoice_id':rec.partner_invoice_id.id,
			'group_id':rec.group_id.id,
			'order_line':isi_line
		}

		ListScope1 = []
		ListScope2 = []
		ListTerms = []

		for sSupra in rec.scope_work_supra:
			ListScope1.append(sSupra.id)
		for sCust in rec.scope_work_customer:
			ListScope2.append(sCust.id)
		for sTerm in rec.term_condition:
			ListTerms.append(sTerm.id)

		prepareNewSO['scope_work_supra'] = False
		prepareNewSO['scope_work_customer'] = False
		prepareNewSO['term_condition'] = False

		newOrderId = self.create(cr,uid,prepareNewSO,context)
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_order_handler', 'quotation_form_view')
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'quotation.form',
			'res_model': 'sale.order',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'res_id':newOrderId,
			'domain': "[('id','=',"+str(newOrderId)+")]",
		}

	def _set_repeat_so_id(self,cr,uid,ids,old_so_id,context={}):
		return self.write(cr,uid,ids,{'repeat_so_id':old_so_id},context)

	def _check_before_save(self,cr,uid,order_line):
		for material in order_line:
			material_lines = material[2]['material_lines']
		if order_line and material_lines:
			res = True
		else:
			res = False
		return res

	def create(self, cr, uid,vals, context=None):
		res =None
		if(self._check_before_save(cr,uid,vals.get('order_line'))):
			sequence_no_quotation = self.pool.get('ir.sequence').get(cr, uid, 'quotation.sequence.type')
			vals['quotation_no'] = sequence_no_quotation
			res = super(Sale_order, self).create(cr, uid, vals, context=context)
		else:
			raise osv.except_osv(_('Warning'),_('Order Line dan Material Line tidak boleh kosong'))
		return res

	def _count_total(self, cr, uid, ids, name, args, context={}):
		res = {}
		sale_order = self.browse(cr,uid,ids,context=context)
		total_base_total=0
		for i in sale_order:
			for r in i.order_line:
				total_base_total += r.base_total

			if i.pricelist_id.name == 'IDR':
				total_base_total = int(total_base_total)

			res[i.id] = {"base_total":total_base_total,}

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

	def _get_total_discount(self, cr, uid, ids, name, args, context={}):
		res = {}
		sale_order = self.browse(cr,uid,ids,context=context)
		print sale_order
		total_discount_nominal=0
		for i in sale_order:
			for r in i.order_line:
				total_discount_nominal += r.discount_nominal

			if i.pricelist_id.name == 'IDR':
				total_discount_nominal = int(total_discount_nominal)

			res[i.id] = {"total_amount_discount":total_discount_nominal,}

		return res

	def _get_years(self,cr,uid,ids,name,args,context={}):
		res={}
		sale_order = self.browse(cr,uid,ids,context=context)
		for i in sale_order:
			name = i.quotation_no[3:5]
			print name,"ini namanya"
			res[i.id]={'is_year':'20'+name}	

		return res

	def _get_month(self,cr,uid,ids,name,args,context={}):
		res={}
		sale_order = self.browse(cr,uid,ids,context=context)
		for i in sale_order:
			name = i.quotation_no[6:8]
			res[i.id]={'month':name}	
		
		return res

	def _search_month(self, cr, uid, obj, name, args, context):
		for i in args:
			filter_no=str(i[2])
			if len(filter_no)==1:
				filter_no="0"+str(i[2])
		res = [('name','like','%/%/'+filter_no+"/%")]
	
		return res

	def _search_years(self, cr, uid,obj, name, args, context={}):
		for i in args:
			print i[2]
			filter_no = str(i[2])
			if len(filter_no)>2:
				filter_no=filter_no[-2:]
		res = [('name','ilike','%/'+str(filter_no))]

		return res

	_columns = {
		'quotation_no':fields.char(string='Quotation#',required=True),
		'base_total':fields.function(_count_total, string='Base Total', type="float",
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','pricelist_id'], 20),
				'sale.order.line': (_get_so_line_by_so, ['price_unit','product_uom_qty'], 20),
			},
			multi="line_total"
		),
		'doc_year':fields.function(_get_years,fnct_search=_search_years,string='Doc Years',store=False),
		'doc_month':fields.function(_get_month,fnct_search=_search_month,string='Doc Month',store=False),
		'quotation_state':fields.selection([('draft','Draft'),('confirmed','Confirmed'),('win','Win'),('lost','Lost'),('cancel','Cancel')],string="Quotation State",track_visibility="onchange"),
		'cancel_stage':fields.selection([('internal user fault','Internal User Fault'),('external user fault','External User Fault'),('lose','Lose')]),
		'cancel_message':fields.text(string="Cancel Message"),
		'revised_histories':fields.one2many('sale.order.revision.history','sale_order_id'),
		'total_amount_discount':fields.function(_get_total_discount, string="total Discount", type="float",
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','pricelist_id'], 20),
				'sale.order.line': (_get_so_line_by_so, ['discount','discount_nominal'], 20),
			},
			multi="line"
			),
		'repeat_so_id': fields.many2one('sale.order', 'Old Order Ref', ondelete="RESTRICT", onupdate="CASCADE", track_visibility="onchange"),
	}
	_defaults={
		'quotation_no':"/",
		'quotation_state':'draft',
		}

	_track={
		'partner_id':{},
		'payment_term':{},
		'partner_shipping_id':{},
		'attention':{},
		'partner_invoice_id':{},
		'pricelist_id':{},
		'date_order':{},
		'user_id':{},
		'group_id':{},
		'amount_untaxed':{}
	}

	def print_rfq(self,cr,uid,ids,context={}):
		res={}
		sale_order = self.browse(cr,uid,ids,context=context)[0]
		id_report = self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name','=','quotation.webkit')])
		datas = {
				 'model': 'sale.order',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}

		return {
			'type': 'ir.actions.report.xml', 
			'report_name': 'quotation.webkit',
			'name': sale_order.quotation_no,
			'datas': datas,
			'nodestroy': True
		}
		
	def print_rfq_web(self,cr,uid,ids,context={}):
		url = self.pool.get('res.users').get_print_url(cr, uid, ids, context=None)
		urlTo = url+"print-sale-order/rfq&id="+str(ids[0])
		
		return {
			'type'  : 'ir.actions.client',
			'tag'   : 'print.out.op',
			'params': {
				'redir' : urlTo,
				'uid':uid
			},
		}

	def print_so_web(self,cr,uid,ids,context={}):
		url = self.pool.get('res.users').get_print_url(cr, uid, ids, context=None)
		urlTo = url+"print-sale-order/saleorder&id="+str(ids[0])
		
		return {
			'type'  : 'ir.actions.client',
			'tag'   : 'print.out.op',
			'params': {
			'redir' : urlTo,
			'uid':uid
			},
		}

	def print_so(self,cr,uid,ids,context={}):
		res={}
		sale_order = self.browse(cr,uid,ids,context=context)[0]
		id_report = self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name','=','quotation.webkit')])
		datas = {
				 'model': 'sale.order',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {
			'type': 'ir.actions.report.xml', 
			'report_name':'sale.order.webkit',
			'name': sale_order.name,
			'datas': datas,
			'nodestroy': True
		}

	def confirm_quotation(self,cr,uid,ids,context={}):
		res = False
		quotation_obj = self.pool.get("sale.order")
		data_sekarang = self.browse(cr,uid,ids,context=context)[0]

		if data_sekarang.order_line	==[]:
			quotation_obj.write(cr,uid,ids,{'quotation_state':'draft'},context=context)
			raise osv.except_osv(_('Warning'),_('Order Cant be confirmed, Order Line is Empty, Please Check Order Lines'))
		else:
			for line in data_sekarang.order_line:
				if line.material_lines==[]:
					quotation_obj.write(cr,uid,ids,{'quotation_state':'draft'},context=context)
					raise osv.except_osv(_('Warning'),_('Order Cant be confirmed, Sale Order Material is Empty, Please Reload'))

		if data_sekarang.quotation_state == 'draft':
			if quotation_obj.write(cr,uid,ids,{'quotation_state':'confirmed'},context=context):
				res = True
		else:
			raise osv.except_osv(_('Warning'),_('Order Cant be confirmed, Only Draft Qotation State can be confirmed!'))

		return res

	def loadBomLine(self,cr,uid,bom_line,product_uom_qty,product_uom,seq_id,is_loaded_from_change=True):
		res = {}
		print bom_line, 
		print bom_line.product_id.id, "iddd" 
		res = {
				'product_id':bom_line.product_id.id,
				'uom':bom_line.product_uom.id,
				'qty':product_uom_qty*bom_line.product_qty,
				'picking_location':seq_id,
				'is_loaded_from_change':is_loaded_from_change,
		}
		return res

	def generate_wo(self,cr,uid,ids,context={}):
		action = False
		val = self.browse(cr, uid, ids, context={})[0]
		ops = self.browse(cr, uid, ids, context=context)
		obj_wo = self.pool.get('sbm.work.order')
		
		new_wo_ids = []
		for so in ops:
			prep_wo = {}
			evt_prepare_change = obj_wo.sale_order_change(cr, uid, ids, val.id)

			prep_wo = evt_prepare_change['value']
			prep_wo['sale_order_id']=so.id
			prep_wo['source_type']='sale_order'

			id_wo = obj_wo.create(cr, uid, prep_wo, context=context)

		pool_data=self.pool.get("ir.model.data")
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'sbm_order_handler', "sbm_work_order_form")     
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'sbm.work.order.form'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'sbm.work.order'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = id_wo
		return action


	def generate_material(self,cr,uid,ids,context={}):
		res={}
		vals = {}
		if type(ids) != list:
			ids = [ids]
		
		sale_orders = self.browse(cr,uid,ids,context)
		for sale_order in sale_orders:
			if sale_order.quotation_state ==False and sale_order.state != 'draft' and sale_order.state != 'cancel':
				self.write(cr,uid,ids,{'quotation_state':'win'})

			for material in sale_order.order_line:
				if material.material_lines ==[]:
					product=self.pool.get('product.product').browse(cr,uid,material.product_id.id,context)
					this_material = self.pool.get('sale.order.line')

					seq_id = self.pool.get('stock.location').search(cr, uid, [('code','=','HO')])

					if len(seq_id):
						seq_id = seq_id[0]
					if product.bom_ids:
						bom_line_set = self.pool.get('mrp.bom').browse(cr,uid,product.bom_ids[0].id)
						vals= {
							'material_lines':[(0,0,self.loadBomLine(cr,uid,bom_line,material.product_uom_qty,material.product_uom,seq_id)) for bom_line in bom_line_set.bom_lines],
						}
					else:
						vals={
						'material_lines': [
								(0,0,{
									'product_id':material.product_id.id,
									'desc': material.name,
									'qty':material.product_uom_qty,
									'uom':material.product_uom.id,
									'picking_location':seq_id,
									'is_loaded_from_change':True
									} )
							],
						
						}
					this_material.write(cr,uid,material.id,vals,context)
				else:
					print "Exist";

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

	def cek_so(self,cr,uid,ids,context={}):
		res =False
		sale_order = self.browse(cr,uid,ids,context=context)[0]
		invoice_in_picking=False
		invoice_in_invoice=False
		amount_total = 0

		if sale_order.picking_ids:
			#menghitung total amount di invoice
			for hitung in sale_order.picking_ids:
				if hitung.invoice_id.amount_total and hitung.invoice_id.state=='paid':
					amount_total+=hitung.invoice_id.amount_total

			for picking in sale_order.picking_ids:
				#kondisi di mana state = paid maka invoice_in_picking = True dan cek amount_total di invoice sama dengan amount_total di sale order
				if picking.invoice_id.state=='paid' and amount_total>=sale_order.amount_total:
					invoice_in_picking =True
					
		#cek invoice di invoice_ids 
		if sale_order.invoice_ids:
			for invoice in sale_order.invoice_ids:
				#kondisi di mana state = paid maka invoice_in_invoice = true
				if invoice.state == 'paid':
					invoice_in_invoice =True
		# cek invoice_in_picking atau invoice_in_invoice 
		if invoice_in_picking or invoice_in_invoice:
			cek_data = False
			#cek isi material line apakah ada
			if sale_order.order_line[0].material_lines:

				for material_so in sale_order.order_line[0].material_lines:
					#cek apakah quantity sama shipped_qty atau type productnya = service
					if material_so.qty == material_so.shipped_qty or material_so.product_id.type=="service":
						cek_data=True
					else:
						cek_data=False
						break

				#cek data untuk di eksekusi
				if cek_data:
					if self.pool.get('sale.order').write(cr,uid,ids,{'state':'done'},context=context):
						res = True
				else:
					raise osv.except_osv(_('Warning'),_('Material line belum semuanya terkirim'))
			else:
				raise osv.except_osv(_('Warning'),_('Belum ada material'))
		else:
			raise osv.except_osv(_('Warning'),_('invoice belum selesai'))

		return  res

class sale_order_material_line(osv.osv):
	_name = 'sale.order.material.line'
	_description = 'Sale order material line'
	_order = "no asc"
	
	_columns = {
		'no':fields.integer('No'),
		'sale_order_line_id':fields.many2one('sale.order.line',string="Sale Order Line", onupdate="CASCADE", ondelete="CASCADE"),
		'product_id':fields.many2one('product.product',string="Product", required=True, domain=[('sale_ok','=','True'),('categ_id.name','!=','LOCAL')], active=True),
		'desc':fields.text(string="Description"),
		'qty':fields.float(string="Qty",required=True),
		'uom':fields.many2one("product.uom",required=True,string="uom"),
		'picking_location':fields.many2one('stock.location',required=True),
		'is_loaded_from_change':fields.boolean('Load From Change ?'),
		'sale_order_id': fields.related('sale_order_line_id','order_id', type='many2one', relation='sale.order', store=True),
		'status': fields.related('sale_order_line_id','state', type='char', relation='sale.order'),
	}

	def _get_ho_location(self,cr,uid,ids,context={}):
		objname, location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'stock_location_stock')
		if not location_id:
			raise osv.except_osv(_('Error'),_('Please Define Default Stock Location'))
		return location_id

	_defaults = {
		'is_loaded_from_change':False,
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

		return res

	def onchange_product_uom(self,cr,uid,ids,product_id,uom,context={}):
		res ={}
		if product_id:
				
			product = self.pool.get("product.product").browse(cr,uid,product_id,context=context)
		
			kategori_uom_product = product.uom_id.category_id.id
			
			if uom:
				product_uom_browse = self.pool.get("product.uom").browse(cr,uid,uom,context=context)
				Kategori_uom =product_uom_browse.category_id.id
				if Kategori_uom != kategori_uom_product :
					if uom != product.uos_id.id:
						res["value"]={"uom":product.uom_id.id}
						res['warning']={'title':"Error",'message':'Kategori Uom Harus sama'}
		return res
	


class sale_order_line(osv.osv):	
	_inherit ='sale.order.line'

	def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
		res = super(sale_order_line, self)._amount_line(cr,uid,ids, field_name, arg, context=None)

		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		
		user_obj = self.pool.get('res.users')
		currency_obj = self.pool.get('res.currency')
		user = user_obj.browse(cr, uid, uid, context=context)


		res = {}
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			sb_total = line.base_total - line.discount_nominal

			price = line.price_unit
			taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
			cur = line.order_id.pricelist_id.currency_id

			if (line.order_id.pricelist_id.currency_id.id==user.company_id.currency_id.id):
				total =  decimal.Decimal(taxes['total']).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
				res[line.id] = float(sb_total)
			else:
				res[line.id] = cur_obj.round(cr, uid, cur, taxes['total']-line.discount_nominal)
		
		return res


	def _count_base_total(self,product_uom_qty,price_unit,discount, discount_nominal):
		nilai = product_uom_qty*price_unit
		count =  decimal.Decimal(nilai).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)

		return float(count)

	def _count_discount_nominal(self,base_total,discount):
		nilai = base_total * discount/100.0
		count = float(decimal.Decimal(nilai).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN))
		return count

	def _count_price_subtotal(self,base_total,discount_n):
		count = base_total - discount_n
		return count
	"""
	@tax_ids harus diisi sama list yang isinya integer id tax cth: [1,2,3,4,5]
	"""
	def _count_amount_tax(self,cr,uid,subtotal,tax_ids):
		list_tax = tax_ids
		amount_tax_total=0

		for i in list_tax:
			tax_bro = self.pool.get("account.tax").browse(cr,uid,i)

			amount_tax = subtotal * tax_bro.amount
			amount_tax_total += amount_tax
		
		return amount_tax_total

	def _count_amount_line(self, cr, uid, ids, name, args, context={}):
		res = {}
		order_lines = self.browse(cr,uid,ids,context=context)
		
		for line in order_lines:
			
			base_total	= self._count_base_total(line.product_uom_qty,line.price_unit,line.discount,line.discount_nominal)
			discount_n = self._count_discount_nominal(base_total,line.discount)
			subtotal_ = self._count_price_subtotal(base_total,discount_n)

			list_tax_id	= []
			for t in line.tax_id:
				
				list_tax_id.append(t.id)

			subtotal_ = float(decimal.Decimal(subtotal_).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN))

			taxes_total= self._count_amount_tax(cr,uid,subtotal_,list_tax_id)
			taxes_total = decimal.Decimal(taxes_total).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
			res[line.id] = {"base_total":base_total,
							"discount_nominal":discount_n,
							"price_subtotal":subtotal_,
							"amount_tax":taxes_total}
		return res

	def replace_discount(self,cr,uid,ids,qty,price, disc):

		subtotal = qty*price
		nilai = (subtotal*disc)/100.00

		x = decimal.Decimal(nilai).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
		self._count_base_total(qty, price, disc, nilai)

		return {'value':{ 'discount_nominal':x} }


	_columns = {
		'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
		'base_total':fields.function(_count_amount_line,type="float", string="Base Total", multi="line_total",
			store={
				'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit','product_uom_qty','discount','discount_nominal'], 1),

			}
		),
		'amount_tax':fields.function(
			_count_amount_line,type="float",string="Tax Amount", multi="line_total",
			store={
				'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, ['base_total','tax_id','discount','discount_nominal'], 1),
			}	
		),		
		'material_lines':fields.one2many('sale.order.material.line','sale_order_line_id'),
		'name':fields.text(string='Description',required=False)	
	}
	
	def onchange_price_unit(self,cr,uid,ids,product_uom_qty,price_unit,discount,discount_nominal,tax_id):
		res={
			'base_total':0.0,
			'discount_nominal':0.0,
			'price_subtotal':0.0,
			'amount_tax':0.0
		}
		
		if product_uom_qty and price_unit:
			base_total	= self._count_base_total(product_uom_qty,price_unit,discount,discount_nominal)
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
			base_total	= self._count_base_total(product_uom_qty,price_unit,discount,discount_nominal)
			discount_n = discount_nominal
			subtotal_ = self._count_price_subtotal(base_total,discount_n)
			
			taxes_total = self._count_amount_tax(cr,uid,subtotal_,tax_id[0][2])
			res["value"]={
						"base_total":base_total,
						"price_subtotal":subtotal_,
						"amount_tax":taxes_total
						}
		return res

	def loadBomLine(self,cr,uid,bom_line,product_uom_qty,product_uom,seq_id,is_loaded_from_change=True):
		res = {}
		print bom_line, 
		print bom_line.product_id.id, "iddd" 
		res = {
				'product_id':bom_line.product_id.id,
				'uom':bom_line.product_uom.id,
				'qty':product_uom_qty*bom_line.product_qty,
				'picking_location':seq_id,
				'is_loaded_from_change':is_loaded_from_change,
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

		order_lines = self.pool.get('sale.order.line').browse(cr,uid,ids)
		old_material_ids = []
		for line in order_lines:
			for material in line.material_lines:
				old_material_ids.append(material.id)

		if product_id:
			seq_id = self.pool.get('sale.order.material.line')._get_ho_location(cr,uid,ids,context={})

			product= self.pool.get('product.product').browse(cr,uid,product_id,{})
			

			if product.bom_ids:
				bom_line_set = self.pool.get('mrp.bom').browse(cr,uid,product.bom_ids[0].id)

				res['value'] = {
					'material_lines':[(0,0,self.loadBomLine(cr,uid,bom_line,product_uom_qty,product_uom,seq_id)) for bom_line in bom_line_set.bom_lines],
					"product_uom":product.uom_id.id,
				}

				if old_material_ids:
					mtr_lines = res['value']['material_lines']

					for old_mtr in old_material_ids:
						lr = (2,old_mtr)
						mtr_lines.append(lr)
					res['value']['material_lines'] = mtr_lines
			else:
				res['value'] = {
					'material_lines': [
						(0,0,{'product_id':product_id,'qty':product_uom_qty,'uom':product.uom_id.id,'picking_location':seq_id,'is_loaded_from_change':True}),
					],
					"product_uom":product.uom_id.id
				}

			if old_material_ids:
				mtr_lines = res['value']['material_lines']

				for old_mtr in old_material_ids:
					lr = (2,old_mtr)
					mtr_lines.append(lr)
				res['value']['material_lines'] = mtr_lines
			if product.description_sale:
				res['value']['name']=product.description_sale
			else:
				res['value']['name']=False
			if product.supplier_taxes_id:
				tax =[]
				for i in product.supplier_taxes_id:
					print i.id
					tax.append(i.id)
				res['value']['tax_id']=tax
			else:
				res['value']['tax_id']=False

		return res

	

	def onchange_product_uom(self,cr,uid,ids,product_id,product_uom,context={}):
		res ={}
		if product_id:
				
			product = self.pool.get("product.product").browse(cr,uid,product_id,context=context)
			kategori_uom_product = product.uom_id.category_id.id

			if product_uom:
				product_uom_browse = self.pool.get("product.uom").browse(cr,uid,product_uom,context=context)
				Kategori_uom =product_uom_browse.category_id.id
				if Kategori_uom != kategori_uom_product :
					if product_uom != product.uos_id.id:
						res["value"]={"product_uom":product.uom_id.id}
						res['warning']={'title':"Error",'message':'Kategori Uom Harus sama'}
		return res
	
	def onchange_product_quotation_qty(self,cr,uid,ids,product_id,product_uom_qty,product_uom,price_unit,discount,tax_id,material_lines_object,context={}):
		res={}
		mrp_obj = self.pool.get('mrp.bom')

		if product_uom_qty == False or product_uom_qty<1:
			res["warning"]={'title':"Error",'message':'Quantity tidak boleh kosong'}
			res['value'] = {				
				"product_uom_qty":1
			}
		else:
			if product_id:
				discount_nominal = 0
				base_total	= self._count_base_total(product_uom_qty,price_unit,discount,discount_nominal)
				discount_n = self._count_discount_nominal(base_total,discount)
				subtotal_ = self._count_price_subtotal(base_total,discount_n)
				taxes_total = self._count_amount_tax(cr,uid,subtotal_,tax_id[0][2])
				seq_id = self.pool.get('stock.location').search(cr, uid, [('code','=','HO')])
				if len(seq_id):
					seq_id = seq_id[0]
				
				product = self.pool.get('product.product').browse(cr,uid,product_id,{})

				all_values_without_bom =[]
				change_applied = True
				for material in material_lines_object:
					old_material = self.pool.get("sale.order.material.line").browse(cr,uid,material[1],context=context)

					bom_id = mrp_obj.search(cr,uid,[('product_id', '=' ,product_id)])
					material_id = mrp_obj.browse(cr,uid,bom_id)
					qty_bom = 1
					if material[2]:
						for x in material_id:

							bom_material = mrp_obj.search(cr,uid,[('bom_id', '=' , x.id), ('product_id', '=' , material[2]['product_id'])])
							browse_mrp  = mrp_obj.browse(cr, uid, bom_material)
							if browse_mrp:
								browse_mrp = browse_mrp[0]

								qty_bom = browse_mrp.product_qty
							else:
								qty_bom = 1


					if material[0]==0:
						# new record
						print "New Record"
						update_values = {
							'desc':material[2].get('desc',False),
							'product_id':material[2]['product_id'],
							"qty":product_uom_qty * qty_bom,
							'uom':material[2]["uom"],
							"picking_location":seq_id,
							'is_loaded_from_change':False
						}
						if material[2].get('is_loaded_from_change',False):
							
							update_values['qty'] = product_uom_qty * qty_bom
							update_values['is_loaded_from_change'] = True
						else:
							update_values['qty'] = material[2].get('qty',0.0)
						all_values_without_bom.append((0,0,update_values))
					elif material[0]==1:
						diff1 = material[2].get('qty',old_material.qty)
						diff2 = product_uom_qty * qty_bom
						theQty = diff1
						if diff1!=diff2:
							theQty = diff2

						updated_val = {
							'qty':theQty * qty_bom,
							'is_loaded_from_change':False,
							'product_id':material[2].get('product_id',old_material.product_id.id),
							'desc':material[2].get('desc',old_material.desc),
							'uom':material[2].get('uom',old_material.uom.id),
							'picking_location':seq_id
						}


						if old_material.is_loaded_from_change:
							updated_val['qty'] = product_uom_qty * qty_bom
							all_values_without_bom.append((1,material[1],updated_val))
							updated_val['is_loaded_from_change'] = True
						else:
							all_values_without_bom.append((1,material[1],updated_val))


					elif material[0]==2:
						all_values_without_bom.append((2,material[1]))
					elif material[0]==4:

						update_values = {
							'desc':old_material.desc,
							'product_id':old_material.product_id.id,
							"qty":product_uom_qty * qty_bom,
							'uom':old_material.uom.id,
							"picking_location":seq_id,
							'is_loaded_from_change':False
						}

						if old_material.is_loaded_from_change:
							all_values_without_bom.append((1,material[1],update_values))
							update_values['is_loaded_from_change'] = True
						else:
							all_values_without_bom.append((1,material[1],update_values))
						
					res['value']={
					"material_lines":all_values_without_bom,
					"base_total":base_total,
					"price_subtotal":subtotal_,
					"amount_tax":taxes_total
					}
		return res


class account_invoice_line(osv.osv):
	_inherit='account.invoice.line'
	_columns={
		'product_id': fields.many2one('product.product', 'Product', ondelete='set null', select=True, required=True),
		'name': fields.text('Description', required=False),
		'sale_order_lines': fields.many2many('sale.order.line', 'sale_order_line_invoice_rel', 'invoice_id', 'order_line_id', 'Order Lines', readonly=True),
	}

class sale_order_invoice(osv.osv):	
	_name ='sale.order'
	_inherit =['sale.order','mail.thread']

	def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
		res1={}
		idInvoice = super(sale_order_invoice,self).action_invoice_create(cr,uid,ids,grouped,states,date_invoice,context=context)
		account_invoice= self.pool.get('account.invoice').browse(cr,uid,idInvoice)

		for inv_line in account_invoice.invoice_line:
			material_invoice =[]
			desc = ""
			for order_line in inv_line.sale_order_lines:
				# if material more than 1
				inv_line_desc = ""
				if order_line.name:
					inv_line_desc = order_line.name

				if len(order_line.material_lines)>1:
					print "MORE THAN 1"
					# append new line if not null
					if inv_line_desc:
						inv_line_desc += "\n"

					inv_line_desc += "Consist of:"
					for material in order_line.material_lines:
						try:

							material_desc = "["+str(material.product_id.default_code)+"]"+str(material.product_id.name)+" (" +str(float(material.qty)) +""+str(material.uom.name)+")"+str(material.desc)
						except UnicodeError:
							material_desc = "["+str(material.product_id.default_code)+"]"+str(material.product_id.name)+" (" +str(float(material.qty))+str(material.desc)

						inv_line_desc += "\n"+material_desc
				else:
					# if product and uom same
					theMaterial = order_line.material_lines[0]
					print "ONLNY 1"
					if order_line.product_id.id==theMaterial.product_id.id and theMaterial.uom.id==order_line.product_uom.id:
						print "only 1 condition 1"
						# then only append material description
						if theMaterial.desc:
							inv_line_desc += theMaterial.desc
					else:
						print "ONLY 1 CONDITION 2",theMaterial.uom.id,'-',order_line.product_uom.id
						if inv_line_desc:
							inv_line_desc += "\n"

						inv_line_desc += "Consist of:"
						for material in order_line.material_lines:
							material_desc = "["+str(material.product_id.default_code)+"]"+str(material.product_id.name)+" (" +str(float(material.qty)) +""+str(material.uom.name)+")"+str(material.desc)
							inv_line_desc += "\n"+material_desc

				
				# print desc,"=++++++++++++++++++++++++++++++++=",material
				desc += inv_line_desc
				# print desc,"<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"
				write_invoice_line = self.pool.get('account.invoice.line').write(cr,uid,inv_line.id,{'name':desc })
		
		# raise osv.except_osv("ERRRRRRRRRRRRRRRRR","ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
		return idInvoice

class WizardCreatePbSo(osv.osv_memory):
	_inherit='wizard.create.pb'
	
	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		so_ids = context.get('active_ids', [])
		active_model = context.get('active_model')
		res = {}
		if not so_ids or len(so_ids) != 1:
			return res
		so_id, = so_ids
		if so_id:
			res.update(so_id=so_id)
			so = self.pool.get('sale.order').browse(cr, uid, so_id, context=context)
			linesData = []

			for l in so.order_line:
				for m in l.material_lines:
					mat = self._load_so_line(cr, uid, m)
					linesData.append(mat)
		
			res['lines'] = linesData
		return res


	def _load_so_line(self, cr, uid,line):
		res = {
		'so_line_id': line.sale_order_line_id.id,
		'so_material_line_id': line.id,
		'product_id'		: line.product_id.id,
		'description'		: line.desc,
		'uom'				: line.uom.id,
		'qty'				: line.qty,
		}
		return res	

class WizardCreatePbLineSo(osv.osv_memory):
	_inherit="wizard.create.pb.line"
	_columns={
		
		'so_material_line_id':fields.many2one('sale.order.material.line','Item Line',required=True),
	}

class detail_pb(osv.osv):
	_inherit="detail.pb"
	_columns={
		
		'sale_order_material_line_id':fields.many2one('sale.order.material.line','Item Line',required=True),
	}