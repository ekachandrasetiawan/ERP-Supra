from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import re
import openerp.exceptions
from lxml import etree
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp.tools.float_utils import float_compare

import logging

_logger = logging.getLogger(__name__)

class delivery_note(osv.osv):

	def _get_years(self,cr,uid,ids,field_name,arg,context={}):

		return True


	def _get_month(self,cr,uid,ids,field_name,arg,context={}):

		return True


	def _search_month(self, cr, uid, obj, name, args, context):
		for x in args:
			filter_no=str(x[2])
			month = '0'
			if filter_no == '1':
				month = 'I'
			elif filter_no == '2':
				month = 'II'
			elif filter_no == '3':
				month = 'III'
			elif filter_no == '4':
				month = 'IV'
			elif filter_no == '5':
				month = 'V'
			elif filter_no == '6':
				month = 'VI'
			elif filter_no == '7':
				month = 'VII'
			elif filter_no == '8':
				month = 'VIII'
			elif filter_no == '9':
				month = 'IX'
			elif filter_no == '10':
				month = 'X'
			elif filter_no == '11':
				month = 'XI'
			elif filter_no == '12':
				month = 'XII'
		res = [('name','like','%/%/%/'+month+"/%")]
		return res

	def _search_years(self, cr, uid,obj, name, args, context={}):
		for x in args:
			filter_no = str(x[2])
			if len(filter_no)>2:
				filter_no=filter_no[-2:]
		res = [('name','ilike','%/'+str(filter_no))]
		return res

	def _search_name(self, cr, uid,obj, name, args, context={}):
		for x in args:
			filter_no = x
		res = [('name','ilike',filter_no)]
		return res

	def _getRequestDocNo(self,cr,uid,ids,field_name,args,context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

			if val.doc_date[5:5 + 2] == '01':
				mount = 'I'
			elif val.doc_date[5:5 + 2] == '02':
				mount = 'II'
			elif val.doc_date[5:5 + 2] == '03':
				mount = 'III'
			elif val.doc_date[5:5 + 2] == '04':
				mount = 'IV'
			elif val.doc_date[5:5 + 2] == '05':
				mount = 'V'
			elif val.doc_date[5:5 + 2] == '06':
				mount = 'VI'
			elif val.doc_date[5:5 + 2] == '07':
				mount = 'VII'
			elif val.doc_date[5:5 + 2] == '08':
				mount = 'VIII'
			elif val.doc_date[5:5 + 2] == '09':
				mount = 'IX'
			elif val.doc_date[5:5 + 2] == '10':
				mount = 'X'
			elif val.doc_date[5:5 + 2] == '11':
				mount = 'XI'
			elif val.doc_date[5:5 + 2] == '12':
				mount = 'XII'
			else:
				mount= rom[int(vals[2])]

			dn = self.pool.get('delivery.note')
			if val.prepare_id.id:
				saleid = self.pool.get('order.preparation').browse(cr, uid, val.prepare_id.id).sale_id.id
				usa = str(self.pool.get('sale.order').browse(cr, uid, saleid).user_id.initial)
			else:
				usa = "FALSE"


			use = str(self.pool.get('res.users').browse(cr, uid, val.create_uid.id).initial)

			RequestNo  = 'C/SBM-ADM/'+usa+'-'+use+'/'+mount+'/'+val.doc_date[2:2 + 2]

			res[item.id] = RequestNo
		return res

	def _getRequestName(self,cr,uid,ids,field_name,args,context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		res = {}
		self._getRequestDocNo(cr, uid, ids, field_name,args,context={})
		for item in self.browse(cr,uid,ids,context=context):
			if val.state == 'draft':
				if val.name:
					RequestNo = val.name
				else:
					RequestNo = '/'
			else:
				if val.seq_no:
					RequestNo = val.seq_no+val.request_doc_no
				else:
					# jika dn lama jika name sudah ada maka pasti name = nomor DN
					if val.name != '/' and val.name.strip() != '':
						RequestNo = val.name
						# set up seq_no = name[:6]
						self.write(cr, uid, ids, {'seq_no':val.name[:6]})
					else:
						raise osv.except_osv(_('Error'), _("Failed to update name code on Delivery Note,, Please Contat System Administrator!"))
			res[item.id] = RequestNo
		return res

	_inherit = "delivery.note"
	_columns = {
		'poc': fields.char('Customer Reference', size=64,track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]}),
		'tanggal' : fields.date('Delivery Date',track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]}),
		'attn':fields.many2one('res.partner',string="Attention",readonly=True, states={'draft': [('readonly', False)]}),
		'note_lines': fields.one2many('delivery.note.line', 'note_id', 'Note Lines', readonly=True, states={'draft': [('readonly', False)]}),
		'picking_id': fields.many2one('stock.picking', 'Stock Picking', domain=[('type', '=', 'out')], required=False,readonly=True, states={'draft': [('readonly', False)]}),
		'postpone_picking': fields.many2one('stock.picking', 'Postpone Picking', required=False,readonly=True, states={'draft': [('readonly', False)]}),
		'work_order_id': fields.many2one('perintah.kerja',string="SPK",store=True,required=False,readonly=True, states={'draft': [('readonly', False)]}),
		'work_order_in': fields.many2one('perintah.kerja.internal',string="SPK Internal",readonly=True, states={'draft': [('readonly', False)]}),
		'state': fields.selection([('draft', 'Draft'), ('submited','Submited'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel'), ('torefund', 'To Refund'), ('refunded', 'Refunded'),('postpone', 'Postpone')], 'State', readonly=True,track_visibility='onchange'),
		'doc_year':fields.function(_get_years,fnct_search=_search_years,string='Doc Years',store=False),
		'doc_month':fields.function(_get_month,fnct_search=_search_month,string='Doc Month',store=False),
		'doc_date' : fields.date('Document Date',track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)], 'postpone': [('readonly', False)]}),
		'name': fields.function(_getRequestName, fnct_search=_search_name, method=True, track_visibility='onchange', string="No#",type="char",
			store={
				'delivery.note': (lambda self, cr, uid, ids, c={}: ids, ['doc_date','state','seq_no'], 20),
			}),
		'seq_no':fields.char('Seq No Delivery Note'),
		'request_doc_no': fields.function(_getRequestDocNo, track_visibility='onchange', method=True, string="Request No",type="char",
			store={
				'delivery.note': (lambda self, cr, uid, ids, c={}: ids, ['doc_date','state'], 20),
			}),
	}

	_defaults = {
		'doc_date': time.strftime('%Y-%m-%d'),
	}

	_order = "id desc"

	_track = {
		'name':{},
		'doc_date':{},
		'tanggal':{},
		'poc':{},
		'prepare_id':{}
	}




	def validasi_stock(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		loc = 12
		if not val.special:
			if val.prepare_id.location_id.id:
				loc = val.prepare_id.location_id.id

			for line in val.note_lines:
				for x in line.note_lines_material:
					if not context:
						context = {}
					context['location'] = loc

					product =self.pool.get('product.product').browse(cr, uid, x.product_id.id, context=context)

					if x.qty > product.qty_available and not re.match(r'service',product.categ_id.name,re.M|re.I) and not re.match(r'on it maintenance service',product.categ_id.name,re.M|re.I):
						mm = ' ' + product.default_code + ' '
						stock = ' ' + str(product.qty_available) + ' '
						msg = 'Stock Product' + mm + 'Tidak Mencukupi.!\n'+ ' Qty Available'+ stock 

						raise openerp.exceptions.Warning(msg)

		return True
	

	"""
	:return boolean True or False
	It wil raise an exception if abnormal / false function data
	"""
	def validate(self,cr,uid,ids,context={}):
		# check if item pass by order preparation
		# to do
		return True

	"""
	Action to repackage Delivery Note
	This action will trigerring set DN state to draft and set Order Preparation to Draft
	"""
	def package_repack(self,cr,uid,ids,context={}):
		vals = self.browse(cr,uid,ids,context=context)
		op = self.pool.get('order.preparation')
		log_message = self.pool.get('')
		for val in vals:
			# op
			if not val.prepare_id:
				raise osv.except_osv(_('Error'),_('Cant Re Packing Package, Order Preparation False'))

			op.write(cr,uid,val.prepare_id.id,{'state':'draft'})
			op.log(cr,uid,val.prepare_id.id,_('Repacking Package !'))
			self.package_draft(cr,uid,ids,context=context)
		return True

	def print_dn_out_new(self,cr,uid,ids,context=None):
		url = self.pool.get('res.users').get_print_url(cr, uid, ids, context=None)
		
		urlTo = url+"delivery-note/printnew&id="+str(ids[0])+"&uid="+str(uid)
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.int.move',
			'params': {
				'redir'	: urlTo,
				'uid':uid
			},
		}

	def create(self, cr, uid, vals, context=None):
		prepareExists = self.search(cr,uid,[('prepare_id','=',vals['prepare_id']),('state','not in',['cancel'])])
		if prepareExists and vals['special']==False:
			no = ""
			for nt in self.browse(cr,uid,prepareExists,context):
				no += "["+nt.name+"]\n"
			raise osv.except_osv(_("Error!!!"),_("Delivery Notes Already Exist. DN Doc. No = "+no))
		vals['name'] ='/'
		for lines in vals['note_lines']:
			if type(lines)==tuple:
				got_line = lines[2]
			elif type(lines) == list:
				got_line = lines[2]
			else:
				got_line = lines

			if got_line['product_qty'] == 0:
				product = self.pool.get('product.product').browse(cr, uid, [got_line[2]['product_id']])[0]
				raise osv.except_osv(_("Error!!!"),_("Product Qty "+ product.default_code + " Not '0'"))
		print vals,"______________________________"
		return super(delivery_note, self).create(cr, uid, vals, context=context)


	def onchange_old_spk(self, cr, uid, ids, spk_id, op_id=None, context={}):
		# browse = self.pool.get('perintah.key')browse(cr, uid, ids, context=context)
		if not op_id:

			spk = self.pool.get('perintah.kerja').browse(cr, uid, spk_id, context=context)
			line = []
			res = {}				
			for spk_item in spk.perintah_lines:
				item = {
					'product_id':spk_item.product_id.id,
					'name': spk_item.name,
					'product_qty':spk_item.product_qty,
					'product_uom':spk_item.product_uom.id,
				}

				item['note_lines_material'] = [(0,0,{
					'product_id':spk_item.product_id.id,
					'name': spk_item.name,
					'qty':spk_item.product_qty,
					'product_uom':spk_item.product_uom.id,
				})]
				print item['note_lines_material'],'+++++++++++++++++++++++++++++++++++++++++++++++++++++++='
				line.append(item)

			res['note_lines'] = line
			return {'value':res}
		else:
			return True

	""""Event On Change Order Packaging"""
	def prepare_change(self, cr, uid, ids, pre, validasi=False):

		recount = False
		self.check_is_processed_queue(cr, uid, pre, False, validasi, {})
		res = super(delivery_note,self).prepare_change(cr, uid, ids, pre)
		if pre :
			res = {}; line = []

			data = self.pool.get('order.preparation').browse(cr, uid, pre)
			dnid = self.pool.get('delivery.note').search(cr, uid, [('prepare_id', '=', pre), ('state', '=', 'done')])

			product =[x.sale_line_material_id.sale_order_line_id.id for x in data.prepare_lines if x.sale_line_material_id]
			if product == []:
				# Jika OP merupakan OP Lama, OP tidak memilliki Sale Order Material Line
				line_op = self.pool.get('order.preparation.line').search(cr, uid, [('preparation_id', '=', pre)])
				for op_line in self.pool.get('order.preparation.line').browse(cr,uid,line_op):
					
					material_line = []

					material_line.append((0,0,{
						'name':op_line.name,
						'product_id':op_line.product_id.id,
						'desc':op_line.name,
						'qty':op_line.product_qty,
						'product_uom':op_line.product_uom.id,
						'op_line_id':op_line.id
					}))

					line.append((0,0,{
						'no': op_line.no,
						'product_id' : op_line.product_id.id,
						'product_qty': op_line.product_qty,
						'product_uom': op_line.product_uom.id,
						'name': op_line.name,
						'note_lines_material': material_line,
						'sale_line_id': op_line.move_id.sale_line_id.id
					}))

			order_line = self.pool.get('sale.order.line').search(cr, uid, [('id', 'in', product)])
			data_order_line = self.pool.get('sale.order.line').browse(cr, uid, order_line)

			qty_dn_line = 0

			for y in data_order_line:
				so_material_line = self.pool.get('sale.order.material.line').search(cr, uid, [('sale_order_line_id', 'in', [y.id])])
				data_material_line = self.pool.get('sale.order.material.line').browse(cr, uid, so_material_line)					

				material_line = []

				# Cek Jumlah Line Material
				# need check
				if len(data_material_line) == 1:

					for qty_dn in data_material_line:
						
						if qty_dn.product_id.id == y.product_id.id:
							op_qty = self.pool.get('order.preparation.line').search(cr, uid, [('sale_line_material_id', 'in', [qty_dn.id]), ('preparation_id', '=', [pre])])
							qty_op = self.pool.get('order.preparation.line').browse(cr, uid, op_qty)[0]
							qty_dn_line = qty_op.product_qty
				# else:
				for dline in data_material_line:
					op_line = self.pool.get('order.preparation.line').search(cr, uid, [('sale_line_material_id', 'in', [dline.id]), ('preparation_id', '=', [pre])])
					data_op_line = self.pool.get('order.preparation.line').browse(cr, uid, op_line)
					
					if data_op_line:
						for dopline in data_op_line:

							# Cek Batch
							batch = self.pool.get('order.preparation.batch').search(cr, uid, [('batch_id', 'in', [dopline.id])])
							data_batch = self.pool.get('order.preparation.batch').browse(cr, uid, batch)

							if data_batch:
								# Jika Ada Batch Maka Tampilkan Batch
								qty_dn_line = 0
								for xbatch in data_batch:
									material_line.append((0,0,{
										'product_id':dopline.product_id.id,
										'prodlot_id':xbatch.name.id,
										'desc':xbatch.desc,
										'qty':xbatch.qty,
										'product_uom':dopline.product_uom.id,
										'location_id':dline.picking_location.id,
										'op_line_id':dopline.id
									}))
									qty_dn_line += xbatch.qty
									recount = True
							else:
								material_line.append((0,0,{
									'name':dopline.name,
									'product_id':dopline.product_id.id,
									'desc':dopline.name,
									'qty':dopline.product_qty,
									'product_uom':dopline.product_uom.id,
									'location_id':dline.picking_location.id,
									'op_line_id':dopline.id
									}))

				line.append((0,0,{
					'no': y.sequence,
					'product_id' : y.product_id.id,
					'product_qty': qty_dn_line,
					'product_uom': y.product_uom.id,
					'name': y.name,
					'note_lines_material': material_line,
					'sale_line_id': y.id,
					}))

			self._qty_recount(cr,uid,ids,line, recount, {})

			res['note_lines'] = line
			res['poc'] = data.sale_id.client_order_ref
			res['tanggal'] = data.duedate
			res['partner_id'] = data.sale_id.partner_id.id
			res['partner_shipping_id'] = data.sale_id.partner_shipping_id.id
			res['attn'] = data.sale_id.attention.id

		return  {'value': res}

	"""
		Will re write tuple of line data of delivery note line material
		It will re count delivery note line material -> product_qty to count line set/lot qty from formula
	"""
	def _qty_recount(self,cr,uid,ids,lines, recount=False, context={}):
		res = {}
		
		for line in lines:
			if type(line)==tuple:
				data = line[2]
			else:
				data=line
			# print "<<<<<<<<<<<<<<<<--------\n",data,"\n-------->>>>>>>>>>>>>>"
			sale_line = self.pool.get('sale.order.line').browse(cr,uid,data['sale_line_id'],context=context) #get sale line object


			fullorder = sale_line.product_uom_qty #prepare full order


			avgList = []
			for materialTuple in data['note_lines_material']:
				material = materialTuple[2]
				# material.op_line_id.sale_line_material_id

				op_line = self.pool.get('order.preparation.line').browse(cr,uid,material['op_line_id'],context=context) #non list browse
				if not op_line.sale_line_material_id.id:
					avgM = 100.0
					# raise osv.except_osv(_('Error'),_('Sale Material Is FALSE\nPlease tell your System Administrator'))
				else:
					avgM = (material['qty']/op_line.sale_line_material_id.qty)*100.00
				avgList.append(avgM)

			avg = (sum(avgList)/len(avgList))
			#if recount == False:
			data['product_qty'] = fullorder*(avg/100.00)
			_logger.error((fullorder, "--------------------", avg))
		return True

	"""
	Return String 
	delivery note sequence no
	"""

	def get_seq_no(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		dn = self.pool.get('delivery.note')

		if val.prepare_id.is_postpone == False:
			vals = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note').split('/')
			dn_no =time.strftime('%y')+ vals[-1]
		else:
			if val.special:
				vals = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note').split('/')
				dn_no =time.strftime('%y')+ vals[-1]
			else:
				
				if val.prepare_id.is_postpone == True:
					vals = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note.postpone').split('/')
					dn_no =time.strftime('%y')+ vals[-1] + 'PS/'
				else:
					vals = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note').split('/')
					dn_no =time.strftime('%y')+ vals[-1]
					
		return dn_no

	def set_sequence_no(self, cr, uid, ids, force=False,context=None):
		vals = self.browse(cr,uid,ids,context=context)
		
		for val in vals:
			if 'PS' in val.name and val.prepare_id.is_postpone == True:
				no = self.get_seq_no(cr,uid,ids,context=context)
			elif 'PS' in val.name and val.prepare_id.is_postpone == False:
				no = self.get_seq_no(cr,uid,ids,context=context)
			elif val.state == 'draft':
				no = self.get_seq_no(cr,uid,ids,context=context)
			elif val.state == 'postpone':
				no = self.get_seq_no(cr,uid,ids,context=context)
			elif val.prepare_id.is_postpone == True:
				no = val.name

			if not val.name or force or val.name == '/': #if name is None / False OR if allow to write new sequence no
				self.write(cr, uid, ids,{
										'seq_no':no,
										},context=context) #write name into new sequence
			else:
				self.write(cr, uid, ids,{
										'seq_no':no,
										},context=context) #write name into new sequence				
		return True

	def set_new_sequence_no(self,cr,uid,ids,context={}):
		return self.set_sequence_no(cr,uid,ids,force=True,context=context)


	def create_picking(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		dn = self.pool.get('delivery.note')
		stock_picking = self.pool.get('stock.picking')
		stock_location = self.pool.get('stock.location')
		stock_move = self.pool.get('stock.move')
		dn_material = self.pool.get('delivery.note.line.material')

		picking_type = 'out'
		seq_obj_name =  'stock.picking.' + picking_type

		m  = self.pool.get('ir.model.data')
		id_loc = m.get_object(cr, uid, 'stock', 'stock_location_customers').id

		# Create Stock Picking
		if val.special:
			origin =""
			if val.work_order_id:
				origin  = val.work_order_id.pr_id.name

			if val.work_order_in:
				origin = val.work_order_in.no_pb

			picking = stock_picking.create(cr, uid, {
				'name':self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
				'origin':origin,
				'partner_id':val.partner_id.id,
				'stock_journal_id':1,
				'move_type':'direct',
				'invoice_state':'2binvoiced',
				'auto_picking':False,
				'type':picking_type,
				'sale_id':False,
				'note_id':val.id,
				'state':'draft'
			})	
		else:

			picking = stock_picking.create(cr, uid, {
						'name':self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
						'origin':val.prepare_id.sale_id.name,
						'partner_id':val.partner_id.id,
						'stock_journal_id':1,
						'move_type':'direct',
						'invoice_state':'2binvoiced',
						'auto_picking':False,
						'type':picking_type,
						'sale_id':val.prepare_id.sale_id.id,
						'note_id':val.id,
						'state':'draft'
						})

		# Create Stock Move
		if val.special:
			loc_id=14
		else:
			if val.prepare_id.id:
				loc_id =val.prepare_id.location_id.id
			else:
				if val.special:
					loc_id = 14
				else:
					loc_id = 14
		print "loccccc----------------",loc_id

		for line in val.note_lines:
			for x in line.note_lines_material:
				sale_line_id = False
				# if sale order line with material
				# if x.op_line_id.sale_line_material_id:
				# 	sale_line_id = x.op_line_id.sale_line_material_id.id #detect via order.preparation.line sale_line_material_id

				# elif  x.op_line_id.move_id and x.op_line_id.move_id.sale_line_id:
				# 	# if old op not has sale_line_material_id on order_preparation_line object
				# 	sale_line_id = x.op_line_id.move_id.sale_line_id.id
				
				if val.special:
					sale_line_id = False
					move_id = stock_move.create(cr,uid,{
						'name' : x.product_id.name,
						'origin':origin,
						'product_uos_qty':x.qty,
						'product_uom':x.product_uom.id,
						'prodlot_id':x.prodlot_id.id,
						'product_qty':x.qty,
						'product_uos':x.product_uom.id,
						'partner_id':val.partner_id.id,
						'product_id':x.product_id.id,
						'auto_validate':False,
						'location_id' :loc_id,
						'company_id':1,
						'picking_id': picking,
						'state':'draft',
						'location_dest_id' :id_loc,
						'sale_line_id': False,
						'sale_material_id':False,
						},context=context)
				else:
					sale_line_id = x.op_line_id.sale_line_id.id
					move_id = stock_move.create(cr,uid,{
						'name' : x.product_id.name,
						'origin':val.prepare_id.sale_id.name,
						'product_uos_qty':x.qty,
						'product_uom':x.product_uom.id,
						'prodlot_id':x.prodlot_id.id,
						'product_qty':x.qty,
						'product_uos':x.product_uom.id,
						'partner_id':val.partner_id.id,
						'product_id':x.product_id.id,
						'auto_validate':False,
						'location_id' :loc_id,
						'company_id':1,
						'picking_id': picking,
						'state':'draft',
						'location_dest_id' :id_loc,
						'sale_line_id': sale_line_id,
						'sale_material_id':x.op_line_id.sale_line_material_id.id,
						},context=context)

					# Update DN Line Material Dengan ID Move
				dn_material.write(cr,uid,x.id,{'stock_move_id':move_id})

		# Update Picking id di DN
		dn.write(cr,uid,val.id,{'picking_id':picking})

		stock_picking.action_assign(cr, uid, [picking])

		return True


	def submit(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		dn = self.pool.get('delivery.note')
		dn_line = self.pool.get('delivery.note.line')
		dn_material = self.pool.get('delivery.note.line.material')
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')
		if not val.special:
			if val.prepare_id.state != 'done':
				raise osv.except_osv(_('Error'),_('Error to Approve Delivery Note\nOrder Preparation Document state not Ready / Done yet.\n Maybe order in Re Packing\n'))

			cek = dn_line.search(cr,uid, [('note_id','=', ids)])
			hasil = dn_line.browse(cr, uid, cek)
			for data in hasil:
				product =[x.id for x in data.note_lines_material if x.id]
				if product == []:
					raise openerp.exceptions.Warning("Delivery Note Line Tidak Memiliki Material Lines")
			# Jalankan Fungsi Asli Package Confirm
			dn.package_confirm(cr,uid, ids,context=context)
			self.validate(cr,uid,ids,context=context)	

			# Jalankan Fungsi Create Picking jika dn baru
			if not val.prepare_id.picking_id:
				dn.create_picking(cr, uid, ids)
			else:
				self.write(cr,uid,ids,{'picking_id':val.prepare_id.picking_id.id})
			# Jalankan Fungsi Sequence No
			if val.name == '/' or val.seq_no==False:
				dn.set_sequence_no(cr, uid, ids, False, context=context)
			elif 'PS' in val.name and val.prepare_id.is_postpone == False:
				dn.set_sequence_no(cr, uid, ids, False, context=context)
		else:
			if val.seq_no==False or val.name=='/':
				# set new no with old style
				dn.set_sequence_no(cr, uid, ids, False, context=context)
			else:
				dn.set_sequence_no(cr, uid, ids, False, context=context)

			dn.create_picking(cr, uid, ids)

		# Cek Validasi Stock By Picking Location 
		self.validasi_stock(cr, uid, ids, context=context)

		self.write(cr, uid, ids, {'state':'submited'}, context=context)

		return True

	def approve_note(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids)[0]

		if val.prepare_id.is_postpone == True:
			raise osv.except_osv(_('Warning'),_('Error to Approve Delivery Note\nOrder Preparation Document state not Ready / Done yet.\n Maybe order in Re Packing status is postpone\n'))

		# Cek Validasi Stock By Picking Location 
		self.validasi_stock(cr, uid, ids, context=context)

		return self.write(cr, uid, ids, {'state':'approve'},context=context)

	"""OVERRIDE package_confirm on module ad_delivery_note"""
	def package_confirm(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]

		if val.prepare_id.sale_id.state == 'cancel' or val.prepare_id.sale_id.state == 'draft':
			raise osv.except_osv(_('Error'),_('Can\'t Change Document State, Please make sure Sale Order has been confirmed'))


		for x in val.note_lines:
			if x.product_qty <= 0:
				raise osv.except_osv(('Perhatian !'), ('Quantity product harus lebih besar dari 0 !'))
		return True

	def package_approve(self,cr,uid,ids,context={}):
		
		return self.write(cr,uid,ids,{"state":"apporove"})

	def package_draft(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		if val.postpone_picking:
			move = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', [val.postpone_picking.id])])
			data = self.pool.get('stock.move').browse(cr, uid, move)
			# Delete Move Postpone Picking
			for x in data:
				self.pool.get('stock.move').write(cr,uid,x.id,{'state':'draft'})
				self.pool.get('stock.move').unlink(cr,uid,[x.id],context)

			# Delete  Postpone Picking
			self.pool.get('stock.picking').write(cr,uid,val.postpone_picking.id,{'state':'draft'})
			self.pool.get('stock.picking').unlink(cr,uid,[val.postpone_picking.id],context)
			self.write(cr, uid, ids, {'state': 'draft','postpone_picking':False})

		if val.picking_id:
			move = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', [val.picking_id.id])])
			data = self.pool.get('stock.move').browse(cr, uid, move)
			# Delete Move Picking
			for x in data:
				self.pool.get('stock.move').write(cr,uid,x.id,{'state':'draft'})
				self.pool.get('stock.move').unlink(cr,uid,[x.id],context)

			# Delete Picking
			self.pool.get('stock.picking').unlink(cr,uid,[val.picking_id.id],context)
			self.write(cr, uid, ids, {'state': 'draft','picking_id':False})
		
		self.write(cr, uid, ids, {'state': 'draft'})
		return True                               


	def package_postpone(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		dn = self.pool.get('delivery.note')
		dn_line = self.pool.get('delivery.note.line')
		dn_material = self.pool.get('delivery.note.line.material')
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')

		picking_type = 'out'
		seq_obj_name =  'stock.picking.' + picking_type

		if val.picking_id.id == False:
			raise openerp.exceptions.Warning("Delivery Note Tidak Dapat di Postpone")


		if val.postpone_picking:
			stock_picking.write(cr,uid,val.postpone_picking.id,{'state':'done'})

			for move_line in val.postpone_picking.move_lines:
				stock_move.write(cr,uid,move_line.id,{'state':'done'})
		else:
			# Create Stock Picking 
			picking = stock_picking.create(cr, uid, {
						'name':self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
						'origin':val.prepare_id.sale_id.name,
						'partner_id':val.partner_id.id,
						'stock_journal_id':1,
						'move_type':'direct',
						'invoice_state':'none',
						'auto_picking':False,
						'type':picking_type,
						'sale_id':val.prepare_id.sale_id.id,
						'note_id':val.id,
						'is_postpone':True,
						'state':'done'
						})

			# Create Stock Move
			location = self.pool.get('stock.location').search(cr, uid, [('code', '=', 'PRTS')])
			if not location:
				raise osv.except_osv(_('Error'),_('Location Not Found, Please Contact System Administrator. Code PRTS')) #rasie warning that location postpone not found

			data_location = self.pool.get('stock.location').browse(cr, uid, location)[0]

			for line in val.note_lines:
				for x in line.note_lines_material:
					move_id = stock_move.create(cr,uid,{
						'name' : x.product_id.name,
						'origin':val.prepare_id.sale_id.name,
						'product_uos_qty':x.qty,
						'product_uom':x.product_uom.id,
						'prodlot_id':x.prodlot_id.id,
						'product_qty':x.qty,
						'product_uos':x.product_uom.id,
						'partner_id':val.partner_id.id,
						'product_id':x.product_id.id,
						'auto_validate':False,
						'location_id' :12,
						'company_id':1,
						'picking_id': picking,
						'state':'done',
						'location_dest_id' : data_location.id
						},context=context)
					
					# Update DN Line Material Dengan ID Move
					dn_material.write(cr,uid,x.id,{'stock_move_id':move_id})

			# Update Picking id di DN
			dn.write(cr,uid,val.id,{'postpone_picking':picking})

		self.write(cr, uid, ids, {'state': 'postpone'})
		return True


	def package_continue(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')
		op = self.pool.get('order.preparation')

		# Proses di 
		op.write(cr, uid, [val.prepare_id.id], {'is_postpone': False})
		

		if val.postpone_picking:
			stock_picking.write(cr,uid,val.postpone_picking.id,{'state':'cancel'})

			for move_line in val.postpone_picking.move_lines:
				stock_move.write(cr,uid,move_line.id,{'state':'cancel'})
		# Jalankan Fungsi OP Done
		op.preparation_done(cr, uid, [val.prepare_id.id], context=None)

		self.submit(cr, uid, ids, context=None)
		
		# self.write(cr, uid, ids, {'state': 'approve'})
		return True


	def package_new_validate(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		stock_picking = self.pool.get('stock.picking')
		old_picking = False #flag to check if old document
		
		# Cek Validasi Stock By Picking Location 
		self.validasi_stock(cr, uid, ids, context=context)


		if val.prepare_id.picking_id:
			# print "INNNNNN",val.prepare_id.prepare_lines[0].sale_line_material_id
			if not val.prepare_id.prepare_lines[0].sale_line_material_id:
				old_picking = True
		# jika ada picking_id di dn



		if val.picking_id.id:
			# if 
			if not old_picking:
				# raise osv.except_osv('Error','EEEE1')
				
				stock_move = self.pool.get('stock.move')
				partial_data = {}
				move = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', val.picking_id.id)])
				data_move = self.pool.get('stock.move').browse(cr, uid, move)
				# Update Done Picking & Move
				stock_picking.action_move(cr, uid, [val.picking_id.id])

				self.write(cr, uid, ids, {'state': 'done','tanggal':datetime.now()})
			else:
				# raise osv.except_osv('Error','EEEE2')
				partial_data = {}
				for line in val.note_lines:
					for dn_material in line.note_lines_material:
						partial_data['move%s' % (dn_material.op_line_id.move_id.id)] = {
									'product_id': dn_material.product_id.id,
									'product_qty': dn_material.qty,
									'product_uom': dn_material.product_uom.id,
									'prodlot_id': dn_material.prodlot_id.id}
				

				# call do_partial
				picking_do = stock_picking.do_partial(cr,uid,[val.prepare_id.picking_id.id],partial_data,context=context)
				picking_done = picking_do.items()
				done_picking_id = picking_done[0][1]['delivered_picking'] #get new picking id where new picking_id is transfered


				prepare_obj = self.pool.get('order.preparation')

				prepare_obj.write(cr,uid,[val.prepare_id.id],{'picking_id':done_picking_id}) #write into order_preparation_line

				stock_picking.write(cr,uid, [done_picking_id], {'note_id': val.id})

				# self.write(cr, uid, ids, {'state': 'done', 'picking_id': picking_do[0][1]['delivered_picking']})
				self.write(cr, uid, ids, {'state': 'done', 'picking_id':done_picking_id,'tanggal':datetime.now()}) #write done to self
		else:
			# jika tidak ada picking_id di dn

			self.pool.get('delivery.note').package_validate(cr, uid, ids)
			self.write(cr, uid, ids, {'picking_id': val.prepare_id.picking_id.id, 'tanggal':datetime.now()})
		# raise osv.except_osv('Error','EEEE')
		return True
		

	def package_cancel(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')

		if val.picking_id:
			stock_picking.action_cancel(cr, uid, [val.picking_id.id])

		if val.postpone_picking:
			stock_picking.action_cancel(cr, uid, [val.postpone_picking.id])

		self.write(cr, uid, ids, {'state':'cancel'})
		return True


	def return_product(self, cr, uid, ids, context=None):
		res = {}
		val = self.browse(cr, uid, ids)[0]
		dn = self.pool.get('delivery.note')

		if val.picking_id.id:
			dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_stock_return_picking_form')
			res = {
				'name':'Return Shipment',
				'view_mode': 'form',
				'view_id': view_id,
				'view_type': 'form',
				'view_name':'stock.stock_return_picking_memory',
				'res_model': 'stock.return.picking.memory',
				'type': 'ir.actions.act_window',
				'target': 'new',
				'res_id':val.picking_id.id,
				'domain': "[('id','=',"+str(val.picking_id.id)+")]",
				'key2':'client_action_multi',
				'multi':"True",
				'context':{
					'active_id':val.picking_id.id,
					'active_model':'stock.return.picking',
					'active_ids':val.picking_id.id,
				}
			}
			if val.picking_id.id==False:
				dn.write(cr,uid,val.id,{'picking_id':val.prepare_id.picking_id.id})
		else:
			res = super(delivery_note,self).return_product(cr,uid,ids,context={})

		return res


delivery_note()


class packing_list_line(osv.osv):
	_inherit = "packing.list.line"


	def refresh(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		if val.note_id.picking_id.id == False and val.note_id.state <>'done':
			for y in val.note_id.note_lines:
				for x in y.note_lines_material:
					res = self.pool.get('product.list.line').create(cr, uid, {
																  'no': y.no,
																  'name': x.desc,
																  'packing_id': val.id,
																  'product_id': x.product_id.id,
																  'product_qty': x.qty,
																  'product_uom': x.product_uom.id,
																  # 'product_packaging': y.note_id.product_packaging.id,
																  })
		else:
			res = super(packing_list_line,self).refresh(cr,uid,ids,context={})

		return res


packing_list_line()

class delivery_note_line(osv.osv):


	"""Count Sale Item Qty from ORder Preparation
		Example: 
		On SO 1 Item Sale On sale line is 10 Set and consist of 10 ea material X and 10 ea material Y
	"""
	def _count_sale_item(self,cr,uid,ids,context={}):
		res = {}
		
		browse = self.browse(cr,uid,ids,context=context)
		for data in browse:
			
			fullorder = data.sale_line_id.product_uom_qty #prepare full order
			avgList = []
			for material in data.note_lines_material:
				avgM = (material.qty/material.op_line_id.sale_line_material_id.qty)*100.00
				avgList.append(avgM)
			avg = (sum(avgList)/len(avgList))
			res[data.id] = fullorder/(avg*100)

		print res,"++++++++++++++++++++++>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

		return res

	def _get_refunded_item(self,cr,uid,ids,field_name,arg,context={}):

		return False

	_inherit = "delivery.note.line"
	_columns = {
		'no': fields.integer('No'),
		'name': fields.text('Description'),
		'note_id': fields.many2one('delivery.note', 'Delivery Note', required=True, ondelete='cascade'),
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)]),
		'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
		'product_uom': fields.many2one('product.uom', 'UoM'),
		'product_packaging': fields.many2one('product.packaging', 'Packaging'),
		'op_line_id':fields.many2one('order.preparation.line','OP Line',required=True),
		'note_line_return_ids': fields.many2many('stock.move','delivery_note_line_return','delivery_note_line_id',string="Note Line Returns"),
		
		'state':fields.related('note_id', 'state', type='selection', store=False, string='State'),
		'note_lines_material': fields.one2many('delivery.note.line.material', 'note_line_id', 'Note Lines Material', readonly=False),
		'sale_line_id': fields.many2one('sale.order.line',required=True, string="Sale Line"),
	}

	def onchange_product_id(self, cr, uid, ids, product_id, uom_id):
		product = self.pool.get('product.template').browse(cr, uid, product_id)
		uom = uom_id
		if product_id:
			if uom_id == False:
				uom = product.uom_id.id
			else:
				if uom_id == product.uom_id.id:
					uom = product.uom_id.id
				elif uom_id == product.uos_id.id:
					uom = product.uos_id.id
				elif uom_id <> product.uom_id.id or uom_id <> product.uos_id.id:
					uom = product.uom_id.id
				else:
					uom = False
					raise openerp.exceptions.Warning('UOM Error')
		return {'value':{'product_uom':uom}}

delivery_note_line()


class delivery_note_line_material(osv.osv):

	def _get_refunded_item(self,cr,uid,ids,field_name,arg,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			refunded_total = 0
			for refund in item.note_line_material_return_ids:
				refunded_total += refund.product_qty

			
			res[item.id] = refunded_total
		return res

	_name = "delivery.note.line.material"
	_columns = {
		'product_id' : fields.many2one('product.product', required=True, string="Product"),
		'prodlot_id':fields.many2one('stock.production.lot', string='Serial Number', onupdate='cascade', ondelete='cascade',select=True),
		'note_line_id': fields.many2one('delivery.note.line', 'Delivery Note Line', required=True, ondelete='cascade'),
		'qty': fields.float('Qty',required=True),
		'product_uom': fields.many2one('product.uom',required=True, string='UOM'),
		'stock_move_id': fields.many2one('stock.move',required=False, string='Stock Move'),
		'desc': fields.text('Description',required=False),
		'location_id':fields.many2one('stock.location',required=False,readonly=True,string="Warehouse Location"),
		'op_line_id':fields.many2one('order.preparation.line','OP Line',required=False),
		'note_line_material_return_ids': fields.many2many('stock.move','delivery_note_line_material_return','delivery_note_line_material_id',string="Note Line Material Returns"),
		'refunded_item': fields.function(_get_refunded_item, string='Refunded Item', store=False),
		'state': fields.related('note_line_id','state', type='selection', relation='delivery.note.line', string='State'),
	}

	_rec_name = 'product_id';

delivery_note_line_material()

class order_preparation_line(osv.osv):
	_inherit = "order.preparation.line"
	_columns = {
		'dn_line_materials':fields.one2many('delivery.note.line.material','op_line_id', string='DN Materail', required=False),
	}

order_preparation_line()


class delivery_note_line_material_return(osv.osv):
	_name = 'delivery.note.line.material.return'	
	_columns = {
		'id':fields.integer('ID'),
		'delivery_note_id': fields.many2one('delivery.note','Delivery Note', ondelete='cascade',onupdate="cascade"),
		'delivery_note_line_id': fields.many2one('delivery.note.line','Delivery Note Line',ondelete='cascade',onupdate="cascade"),
		'delivery_note_line_material_id': fields.many2one('delivery.note.line.material','Delivery Note Line Material',ondelete='cascade',onupdate="cascade"),
		'stock_picking_id': fields.many2one('stock.picking','Stock Picking',ondelete='cascade',onupdate="cascade"),
		'stock_move_id': fields.many2one('stock.move','Stock Move',ondelete='cascade', onupdate="cascade"),
	}

delivery_note_line_material_return()


class stock_picking_in(osv.osv):
	_inherit = 'stock.picking.in'
	_table="stock_picking"

	_columns = {
		'return_no':fields.char('Return No'),
	}

	def print_return(self,cr,uid,ids,context=None):
		url = self.pool.get('res.users').get_print_url(cr, uid, ids, context=None)
		urlTo = url+"delivery-note/printreturn&id="+str(ids[0])+"&uid="+str(uid)
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.out.op',
			'params': {
				'redir'	: urlTo,
				'uid':uid
			},
		}				
	
stock_picking_in()



class stock_picking(osv.osv):

	_name = 'stock.picking'
	_inherit = ["stock.picking","mail.thread"]

	_columns = {
		'is_postpone': fields.boolean('Is Postpone'),
		'return_no':fields.char('Return No'),
	}

stock_picking()


class stock_move(osv.osv):
	_inherit = 'stock.move'
	_columns = {
		'sale_material_id': fields.many2one('sale.order.material.line','Sale Material', required=False),
	}


stock_move()


class stock_return_picking_memory(osv.osv_memory):
	_name = "stock.return.picking.memory"
	_inherit = "stock.return.picking.memory"
	_columns = {
		'cancel_notes': fields.text('Cancel Notes'),
	}

stock_return_picking_memory()


class stock_return_picking(osv.osv_memory):
	_inherit = 'stock.return.picking'
	_name = 'stock.return.picking'
	_description = 'Return Picking'

	def default_get(self, cr, uid, fields, context=None):

		result1 = []
		if context is None:
			context = {}
		res = super(stock_return_picking, self).default_get(cr, uid, fields, context=context)

		record_idx = context and context.get('active_id', False) or False

		if context.get('active_model') == 'stock.picking' or context.get('active_model') =='stock.picking.in' or context.get('active_model') =='stock.picking.out':
			record_id = context and context.get('active_id', False)
		else:
			val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)

			if val.picking_id.id:
				record_id = val.picking_id.id
			else:
				record_id = val.prepare_id.picking_id.id

		pick_obj = self.pool.get('stock.picking')
		pick = pick_obj.browse(cr, uid, record_id, context=context)
		if pick:
			if 'invoice_state' in fields:
				if pick.invoice_state=='invoiced':
					res.update({'invoice_state': '2binvoiced'})
				else:
					res.update({'invoice_state': 'none'})
			return_history = self.get_return_history(cr, uid, record_id, context)       
			for line in pick.move_lines:
				qty = line.product_qty - return_history.get(line.id, 0)
				if qty > 0:
					result1.append({'product_id': line.product_id.id, 'sisa':qty, 'quantity': qty,'move_id':line.id, 'prodlot_id': line.prodlot_id and line.prodlot_id.id or False})

			if 'product_return_moves' in fields:
				res.update({'product_return_moves': result1})

		return res


	def view_init(self, cr, uid, fields_list, context=None):
		res ={}
		if context is None:
			context = {}
		record_idx = context and context.get('active_id', False)
		if context.get('active_model') == 'stock.picking' or context.get('active_model') == 'stock.picking.in' or context.get('active_model') == 'stock.picking.out':
			record_id = context and context.get('active_id', False)
		else:
			val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)

			if val.picking_id.id:
				record_id = val.picking_id.id
				context.update({
					'active_model': 'stock.picking',
					'active_ids': [val.picking_id.id],
					'active_id': val.picking_id.id
				})
			else:
				record_id = val.prepare_id.picking_id.id
				context.update({
					'active_model': 'stock.picking',
					'active_ids': [val.prepare_id.picking_id.id],
					'active_id': val.prepare_id.picking_id.id
				})
		res = super(stock_return_picking, self).view_init(cr, uid, fields_list, context=context)
		return res


	def get_return_history(self, cr, uid, pick_id, context=None):
		
		return super(stock_return_picking, self).get_return_history(cr, uid, pick_id, context=context)


	def create_returns(self, cr, uid, ids, context=None):
		dn = self.pool.get('delivery.note')
		# call active dn
		active_dn_id = context['active_ids'][0]
		dn_obj = dn.browse(cr,uid,context['active_ids'][0],context=context)


		if context is None:
			context = {} 
		record_idx = context and context.get('active_id', False) or False
		
		val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)

		if context.get('active_model') == 'stock.picking' or context.get('active_model') == 'stock.picking.in' or context.get('active_model') == 'stock.picking.out':
			record_id = context and context.get('active_id', False) or False
		else:
			if val.picking_id.id:
				record_id = val.picking_id.id
			else:
				record_id = val.prepare_id.picking_id.id


		move_obj = self.pool.get('stock.move')
		pick_obj = self.pool.get('stock.picking')
		uom_obj = self.pool.get('product.uom')
		data_obj = self.pool.get('stock.return.picking.memory')
		act_obj = self.pool.get('ir.actions.act_window')
		model_obj = self.pool.get('ir.model.data')
		#  Delivery Note
		del_note = self.pool.get('delivery.note')

		wf_service = netsvc.LocalService("workflow")
		
		if context.get('active_model') == 'stock.picking' or context.get('active_model') == 'stock.picking.in' or context.get('active_model') == 'stock.picking.out':
			record_id = context and context.get('active_id', False) or False
			pick = pick_obj.browse(cr, uid, record_id, context=context)
		else:
			if val.picking_id.id:
				pick = pick_obj.browse(cr, uid, val.picking_id.id, context=context)
			else:
				pick = pick_obj.browse(cr, uid, val.prepare_id.picking_id.id, context=context)

		data = self.read(cr, uid, ids[0], context=context)
		date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
		set_invoice_state_to_none = True
		returned_lines = 0
		
		#Create new picking for returned products
		seq_obj_name = 'stock.picking'
		new_type = 'internal'
		if pick.type =='out':
			new_type = 'in'
			seq_obj_name = 'stock.picking.in'
		elif pick.type =='in':
			new_type = 'out'
			seq_obj_name = 'stock.picking.out'
		new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
		
		if context.get('active_model') == 'stock.picking' or context.get('active_model') ==  'stock.picking.in' or context.get('active_model') == 'stock.picking.out':
			new_picking = pick_obj.copy(cr, uid, pick.id, {
								'name': _('%s-%s-return') % (new_pick_name, pick.name),
								'move_lines': [], 
								'state':'draft', 
								'type': new_type,
								'date':date_cur,
								'invoice_state': data['invoice_state'],
								})
		else:
			new_picking = pick_obj.copy(cr, uid, pick.id, {
								'name': _('%s-%s-return') % (new_pick_name, pick.name),
								'move_lines': [], 
								'state':'draft', 
								'type': new_type,
								'date':date_cur,
								'note_id':val.id,
								'invoice_state': data['invoice_state'],
								})
			if val.picking_id.id:
				if val.picking_id.id==False:
					dn.write(cr,uid,val.id,{'note_return_ids':[(4,new_picking)],'picking_id':val.prepare_id.picking_id.id})
				else:
					dn.write(cr,uid,val.id,{'note_return_ids':[(4,new_picking)]})
			else:
				dn.write(cr,uid,val.id,{'note_return_ids':[(4,new_picking)]})


		dn_return_rel = []
		val_id = data['product_return_moves']
		
		# prepare op / to get note line id
		if context.get('active_model') == 'delivery.note':
			op_line = self.pool.get('order.preparation.line')
			dn_line = self.pool.get('delivery.note.line')
			dn_line_material = self.pool.get('delivery.note.line.material')


		for v in val_id:
			data_get = data_obj.browse(cr, uid, v, context=context)
			mov_id = data_get.move_id.id

			# search op and dn
			if context.get('active_model') == 'delivery.note':
				val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)
				if val.picking_id.id:
					dn_line_material_id=dn_line_material.search(cr,uid,[('stock_move_id','in',[mov_id])],context=context)
					print dn_line_material_id,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<---------------",mov_id
					dn_line_id = dn_line.search(cr,uid,[('note_lines_material','=',dn_line_material_id[0])],context=context)[0]
					id_line_material = dn_line_material_id[0]

				else:
					# op_line_id = op_line.search(cr,uid,[('move_id','=',mov_id)],context=context)
					# dn_line_id = dn_line.search(cr,uid,[('op_line_id','=',op_line_id[0])],context=context)[0]
					
					dn_line_material_id=dn_line_material.search(cr,uid,[('stock_move_id','=',mov_id)],context=context)
					dn_line_id = dn_line.search(cr,uid,[('note_lines_material','=',dn_line_material_id[0])],context=context)[0]
					id_line_material = dn_line_material_id[0]

			if not mov_id:
				raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))

			# Cek Barang yang sisa & yang di input
			return_history = self.get_return_history(cr, uid, pick.id, context)
			
			qty = 0
			for line in pick.move_lines:
				qty += line.product_qty - return_history.get(line.id, 0)

			if context.get('active_model') == 'delivery.note':
				if data_get.quantity > qty:
					raise osv.except_osv(_('Warning !'), _("Product Qty Tidak Mencukupi"))
					
			new_qty = data_get.quantity
			move = move_obj.browse(cr, uid, mov_id, context=context)
			new_location = move.location_dest_id.id
			returned_qty = move.product_qty
			for rec in move.move_history_ids2:
				returned_qty -= rec.product_qty

			if returned_qty != new_qty:
				set_invoice_state_to_none = False
			if new_qty:
				returned_lines += 1
				new_move=move_obj.copy(cr, uid, move.id, {
											'product_qty': new_qty,
											'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
											'picking_id': new_picking, 
											'state': 'draft',
											'location_id': new_location, 
											'location_dest_id': move.location_id.id,
											'cancel_notes':data_get.cancel_notes,
											'date': date_cur,
				})
				move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4,new_move)]}, context=context)
				
			if context.get('active_model') == 'delivery.note':
				val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)
				if val.picking_id.id:
					tpl = {'delivery_note_id':active_dn_id,'stock_picking_id':new_picking,'delivery_note_line_id':dn_line_id,'delivery_note_line_material_id':id_line_material,'stock_move_id':new_move}
					dn_return_rel.append(tpl)
				else:
					tpl = {'delivery_note_id':active_dn_id,'stock_picking_id':new_picking,'delivery_note_line_id':dn_line_id,'stock_move_id':new_move}
					dn_return_rel.append(tpl)

		if context.get('active_model') == 'delivery.note':
			val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)

			dn_r = self.pool.get('delivery.note.line.return')
			dn_rm = self.pool.get('delivery.note.line.material.return')
			# write into dn line rel

			if val.picking_id.id:
				for note_line_return in dn_return_rel:
					dn_rm.create(cr,uid,note_line_return)
					# a
			else:	
				# Create return Lama 
				for note_line_return in dn_return_rel:
					dn_r.create(cr,uid,note_line_return)
		if not returned_lines:
			raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

		if set_invoice_state_to_none:
			pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'}, context=context)
		wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
		pick_obj.force_assign(cr, uid, [new_picking], context)
		# update Delivery Note
		if context.get('active_model') == 'delivery.note':
			val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)
			del_note.write(cr, uid, val.id, {'state':'torefund','refund_id':new_picking}, context=context)

		model_list = {
				'out': 'stock.picking.out',
				'in': 'stock.picking.in',
				'internal': 'stock.picking',
		}
		return {
			'domain': "[('id', 'in', ["+str(new_picking)+"])]",
			'name': _('Returned Picking'),
			'view_type':'form',
			'view_mode':'tree,form',
			'res_model': model_list.get(new_type, 'stock.picking'),
			'type':'ir.actions.act_window',
			'context':context,
		}


	def create_return_no(self, cr, uid, ids, context=None):
		return_no = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note.return')

		cr.execute("""update delivery_note_line_material_return set return_no=%s where stock_picking_id=%s""", (return_no, ids))

		# Update Return No from Stock Picking 
		self.pool.get('stock.picking').write(cr,uid,ids,{'return_no':return_no},context=None)
		self.pool.get('stock.picking.in').write(cr,uid,ids,{'return_no':return_no},context=None)
		return True
stock_return_picking()
