from osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime

class account_invoice(osv.osv):
	PERIODS = [('01','01 - January'),('02','02 - February'),('03','03 - March'),('04','04 - April'),('05','01 - Mey'),('06','06 - June'),('07','07 - July'),('08','08 - August'),('09','09 - September'),('10','10 - October'),('11','11 - November'),('12','12 - December')]
	def _get_month(self,date,date_format='%Y-%m-%d'):
		date_obj = datetime.strptime(date,date_format)
		return date_obj.strftime('%m')
	
	def onchange_format_faktur(self, cr, uid, ids, no):
		no = no.replace('.','').replace('-','')

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
		

	def onchange_date_invoice(self,cr,uid,ids,date):
		return {
			'value':{
				'tax_period':self._get_month(date)
			}
		}

	_inherit = 'account.invoice'
	_columns = {
		'tax_period': fields.selection(PERIODS,string="Tax Period"),
	}

	"""
	action_to_tax_replacement
	@override from sbm_inherit.action_to_tax_replacement (account.invoice)
	"""
	def action_to_tax_replacement(self,cr,uid,ids,context={}):
		res = False
		invs = self.browse(cr,uid,ids,context=context)
		order_obj = self.pool.get('sale.order')
		newids = []
		for inv in invs:
			picking_ids = [(6,0, [pick.id]) for pick in inv.picking_ids]
			# res = [(0,0,self._im_line_preparation(cr,uid,line)) for line in request.lines if (line.qty-line.processed_item_qty) > 0]
			invoice_lines =  [(0, 0, self.pool.get('account.invoice.line').copy_data(cr,uid,line.id,{'invoice_id':False},context=context)) for line in inv.invoice_line]

			
			# print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<----",res_order

			# newid = self.copy(cr,uid,inv.id,default=default,context=context)
			# override copy new
			copy_new = self.copy_data(cr, uid, inv.id, context=context, default={'invoice_line':invoice_lines,'picking_ids':picking_ids})
			
			newid = self.create(cr,uid,copy_new,context=context)
			
			# raise osv.except_osv(_('Error!'),_('Tes'))
			newids = [newid]
			newInv = self.browse(cr,uid,newid,context=context)
			
			fp_no = newInv.faktur_pajak_no[0:2]+'1.'+newInv.faktur_pajak_no[4:20]

			
			# self.write(cr,uid,newid,{'faktur_pajak_no':fp_no})
			# canceling old invoice
			self.write(cr,uid,[inv.id],{'state':'cancel'})
			# new faktur  number
			self.write(cr,uid,newid,{'faktur_pajak_no':fp_no,'tax_invoice_origin_id':inv.id,'tax_period':self._get_month(inv.date_invoice)})


			res_order = order_obj.search(cr,uid,[('invoice_ids','in',[inv.id])])
			if res_order:
				order_obj.browse(cr,uid,res_order)
			# raise osv.except_osv(_('Error'),_('ERROR'))

		mod_obj = self.pool.get('ir.model.data')
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
			'res_id': newids and newids[0] or False,
		}



	def create_invoice(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_invoice = self.pool.get('account.invoice')
		obj_invoice_line = self.pool.get('account.invoice.line')
		res = {};
		line = []

		for x in val.invoice_line:
			line.append((0,0,{
					'origin':x.origin,
					'uos_id':x.uos_id.id,
					'account_id':x.account_id.id,
					'name':x.name,
					'sequence':x.sequence,
					'price_unit':x.price_unit,
					'price_subtotal':x.price_subtotal,
					'company_id':x.company_id.id,
					'discount':x.discount,
					'quantity':x.quantity,
					'partner_id':x.partner_id.id,
					'product_id':x.product_id.id,
					'amount_discount':x.amount_discount,
					'sub_total_main':x.sub_total_main,
					'amount_bruto_main':x.amount_bruto_main,
					'price_subtotal_netto':x.price_subtotal_netto,
					'tax_amount':x.tax_amount,
					'sub_total_netto_main':x.sub_total_netto_main,
					'tax_amount_main':x.tax_amount_main,
					'ppn_tax_amount_main':x.ppn_tax_amount_main,
					'unit_price_main':x.unit_price_main,
					'amount_discount_main':x.amount_discount_main,
					'invoice_line_tax_id':[(6, 0, [y.id for y in x.invoice_line_tax_id])],
					'amount_bruto':x.amount_bruto
				}))

		# Create Sale Order
		invoice_id =obj_invoice.create(cr, uid, {
					'origin':val.origin,
					'date_due':val.date_due,
					'check_total':val.check_total,
					'reference':val.reference,
					'account_id':val.account_id.id,
					'company_id':val.company_id.id,
					'currency_id':val.currency_id.id,
					'partner_id':val.partner_id.id,
					'user_id':val.user_id.id,
					'payment_term':val.payment_term.id,
					'reference_type':val.reference_type,
					'journal_id':val.journal_id.id,
					'amount_tax':val.amount_tax,
					'state':'draft',
					'type':'out_invoice',
					'reconciled':val.reconciled,
					'date_invoice':val.date_invoice,
					'residual':val.residual,
					'amount_untaxed':val.amount_untaxed,
					'amount_total':val.amount_total,
					'name':val.name,
					'comment':val.comment,
					'sent':val.sent,
					'commercial_partner_id':val.commercial_partner_id.id,
					'faktur_pajak_no':val.faktur_pajak_no[0:2]+'1.'+val.faktur_pajak_no[4:20],
					'kwitansi':val.kwitansi,
					'pajak':val.pajak,
					'group_id':val.group_id.id,
					'dp_percentage':val.dp_percentage,
					'tax_period':val.tax_period,
					'total_bruto_main':val.total_bruto_main,
					'amount_tax_main':val.amount_tax_main,
					'amount_untaxed_main':val.amount_untaxed_main,
					'ppn_amount_tax_main':val.ppn_amount_tax_main,
					'amount_total_main':val.amount_total_main,
					'total_discount_main':val.total_discount_main,
					'invoice_line':line
					})
		

		return invoice_id


	def create_invoice_replace_tax(self, cr, uid, ids, context=None):
		invoice_id=self.create_invoice(cr, uid, ids, context=None)
		if invoice_id:
			
			pool_data=self.pool.get("ir.model.data")
			action_model,action_id = pool_data.get_object_reference(cr, uid, 'account', "invoice_form")     
			action_pool = self.pool.get(action_model)
			res_id = action_model and action_id or False
			action = action_pool.read(cr, uid, action_id, context=context)
			action['name'] = 'account.invoice.form'
			action['view_type'] = 'form'
			action['view_mode'] = 'form'
			action['view_id'] = [res_id]
			action['res_model'] = 'account.invoice'
			action['type'] = 'ir.actions.act_window'
			action['target'] = 'current'
			action['res_id'] = invoice_id

			# Update Tax
			self.button_reset_taxes(cr, uid, [invoice_id], context=context)
			
			return action
