from datetime import datetime
import math
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class account_invoice_line_tax_amount(osv.osv):
	
	_name = 'account.invoice.line.tax.amount'
	_description = 'Account Invoice Line Tax Amount'
	_columns = {
		'invoice_line_id':fields.many2one('account.invoice.line',string="Invoice Line",required=True,ondelete='CASCADE',onupdate='RESTRICT'),
		'tax_id': fields.many2one('account.tax',string="Tax Applied",required=True),
		'base_amount': fields.float(string="Base Line Tax Amount",required=True),
		'tax_amount': fields.float(string="Tax Amount",digits_compute=dp.get_precision('TaxLine'),required=True),
		'name': fields.related('tax_id','name',string="Tax",type="char",store=False),
		'is_manual': fields.boolean('Is Manual Fill'),
	}

	def _prepare_and_create(self,cr,uid,line_id,vals,context={}):
		ailta = self.pool.get('account.invoice.line.tax.amount')

		# raise osv.except_osv(_('Error'),_('Error!!!'))
		print "call Ailta createeeeeeeee-----------------------",vals
		return ailta.create(cr,uid,vals,context=context)

	def write(self,cr,uid,ids,vals,context={}):
		print "HAYOOOOO",vals
		res = super(account_invoice_line_tax_amount,self).write(cr,uid,ids,vals,context=context)

		manual = vals.get('is_manual',0)
		inv_line = {
			'tax_amount':0.0,
		}
		
		# if manual:
		# get account.invoice.tax.amount record
		for tax_am in self.browse(cr,uid,ids,context=context):
			# get base code

			# get invoice.tax_line
			# loop each tax_line find the same tax base_code_id
			for tax_line in tax_am.invoice_line_id.invoice_id.tax_line:
				tax_amount = self.pool.get('account.invoice').get_tax_amount_grouped(cr,uid,[tax_line.invoice_id.id],context=context)
				if tax_line.base_code_id.id == tax_am.tax_id.base_code_id.id:
					# if base code id in account invoice tax same with account invoice tax amount tax base code id
					# then update and set is_manual on account.invoice.tax set to True
					amount = tax_amount[tax_line.invoice_id.id]['tax_amount'][tax_am.tax_id.id]
					
					write_into = {'manual':True,'amount':amount}
					
					self.pool.get('account.invoice.tax').write(cr,uid,tax_line.id,write_into,context=context)


			for taxes_amount_line in tax_am.invoice_line_id.tax_amount_ids:
				# write tax_amount invoice line ids
				inv_line['tax_amount'] += taxes_amount_line['tax_amount']
			
			self.pool.get('account.invoice.line').write(cr,uid,tax_am.invoice_line_id.id,inv_line,context=context)

			invL = self.pool.get('account.invoice.line').browse(cr,uid,tax_am.invoice_line_id.id,context=context)
			
			
		
		return res

	def on_change_tax_amount(self,cr,uid,ids,base_amount,tax_amount):
		res = {}
		ai = self.pool.get('account.invoice')

		for line_tax_amount in self.browse(cr,uid,ids,{}):
			base_code_line_id = line_tax_amount.tax_id.base_code_id.id
			
			res['value'] = {'is_manual':True,'invoice_line_id':{'tax_amount':0.00}}
		return res

class account_tax(osv.osv):
	_inherit = 'account.tax'
	def _unit_compute(self, cr, uid, taxes, price_unit, product=None, partner=None, quantity=0):
		
		taxes = self._applicable(cr, uid, taxes, price_unit ,product, partner)

		res = []
		dec_precision_tax_line = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
		cur_price_unit=price_unit

		for tax in taxes:

			# we compute the amount for the current tax object and append it to the result
			data = {
				'id':tax.id,
				'name':tax.description and tax.description + " - " + tax.name or tax.name,
				'account_collected_id':tax.account_collected_id.id,
				'account_paid_id':tax.account_paid_id.id,
				'account_analytic_collected_id': tax.account_analytic_collected_id.id,
				'account_analytic_paid_id': tax.account_analytic_paid_id.id,
				'base_code_id': tax.base_code_id.id,
				'ref_base_code_id': tax.ref_base_code_id.id,
				'sequence': tax.sequence,
				'base_sign': tax.base_sign,
				'tax_sign': tax.tax_sign,
				'ref_base_sign': tax.ref_base_sign,
				'ref_tax_sign': tax.ref_tax_sign,
				'price_unit': float(cur_price_unit),
				'tax_code_id': tax.tax_code_id.id,
				'ref_tax_code_id': tax.ref_tax_code_id.id,
			}
			res.append(data)
			
			if tax.type=='percent':

				amount = cur_price_unit * tax.amount

				data['amount'] = round(amount,dec_precision_tax_line) # TAX / PAJAK
				


			elif tax.type=='fixed':
				data['amount'] = tax.amount
				data['tax_amount']=quantity
			   # data['amount'] = quantity
			elif tax.type=='code':
				localdict = {'price_unit':cur_price_unit, 'product':product, 'partner':partner}
				exec tax.python_compute in localdict
				amount = localdict['result']
				data['amount'] = amount
			elif tax.type=='balance':
				data['amount'] = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)
				data['balance'] = cur_price_unit


			amount2 = data.get('amount', 0.0)
			
			
			
			if tax.child_ids:
				
				if tax.child_depend:
					latest = res.pop()
				amount = amount2
				child_tax = self._unit_compute(cr, uid, tax.child_ids, amount, product, partner, quantity)
				res.extend(child_tax)
				if tax.child_depend:
					for r in res:
						for name in ('base','ref_base'):
							if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
								r[name+'_code_id'] = latest[name+'_code_id']
								r[name+'_sign'] = latest[name+'_sign']
								r['price_unit'] = latest['price_unit']
								latest[name+'_code_id'] = False
						for name in ('tax','ref_tax'):
							if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
								r[name+'_code_id'] = latest[name+'_code_id']
								r[name+'_sign'] = latest[name+'_sign']
								r['amount'] = data['amount']
								latest[name+'_code_id'] = False
			if tax.include_base_amount:
				cur_price_unit+=amount2
		return res


	def _compute(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None, line_id=0,context={}):
		"""
		Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

		RETURN:
			[ tax ]
			tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
			one tax for each tax id in IDS and their children
		"""
		tax_line_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')

		ailta = self.pool.get('account.invoice.line.tax.amount')


		
		if not precision:
			precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
		
		res = self._unit_compute(cr, uid, taxes, price_unit, product, partner, quantity)

		

		total = 0.0
		for r in res:
			if r.get('balance',False):
				r['amount'] = round(r.get('balance', 0.0) * quantity, tax_line_precision) - total
			else:
				r['amount'] = round(r.get('amount', 0.0) * quantity, tax_line_precision)
				total += r['amount']
			
			
			if 'button_reset_taxes' in context:
				# if context button_reset_taxes exist on context dictionary than it means update triggered with button
				
				# so it can use for flag to sign that if compute_all call from this module will be sign line_id
				# and if not define line_id it will not call this part anymore
				# insert into account invoice line tax amount
				ailta_vals = {
					'invoice_line_id': line_id,
					'tax_id': r['id'],
					'base_amount': round(r['price_unit']*quantity,precision),
					'tax_amount': r['amount'],
				}

				ailta_vals = self.pool.get('account.invoice.line.tax.amount')._prepare_and_create(cr,uid,line_id,ailta_vals,context=context)

		return res



	def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, force_excluded=False,line_id=0,context={}):
		
		"""
		:param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
			tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
			False
		RETURN: {
				'total': 0.0,                # Total without taxes
				'total_included: 0.0,        # Total with taxes
				'taxes': []                  # List of taxes, see compute for the format
			}
		"""

		# By default, for each tax, tax amount will first be computed
		# and rounded at the 'Account' decimal precision for each
		# PO/SO/invoice line and then these rounded amounts will be
		# summed, leading to the total amount for that tax. But, if the
		# company has tax_calculation_rounding_method = round_globally,
		# we still follow the same method, but we use a much larger
		# precision when we round the tax amount for each line (we use
		# the 'Account' decimal precision + 5), and that way it's like
		# rounding after the sum of the tax amounts of each line
		ailta = self.pool.get('account.invoice.line.tax.amount')
		alita_vals = {}

		if 'button_reset_taxes' in context:
			
			# line_id parameters is not an original parameter
			# so it can use for flag to sign that if compute_all call from this module will be sign line_id
			# and if not define line_id it will not call this part anymore
			cr.execute("DELETE FROM account_invoice_line_tax_amount WHERE invoice_line_id=%s",[int(line_id)])
				

		precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'TaxLine')
		tax_compute_precision = precision
		if taxes and taxes[0].company_id.tax_calculation_rounding_method == 'round_globally':
			tax_compute_precision += 5
		totalin = totalex = round(price_unit * quantity, precision)

		# raise osv.except_osv(_('Error!'),_('Error'))
		tin = []
		tex = []
		for tax in taxes:
			if not tax.price_include or force_excluded:
				tex.append(tax)
			else:
				tin.append(tax)
		tin = self.compute_inv(cr, uid, tin, price_unit, quantity, product=product, partner=partner, precision=tax_compute_precision)
		
		for r in tin:
			totalex -= r.get('amount', 0.0)
		totlex_qty = 0.0
		try:
			totlex_qty = totalex/quantity
		except:
			pass

		
		tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=tax_compute_precision, line_id=line_id,context=context)

		for r in tex:
			
			totalin += r.get('amount', 0.0)
		
		# per invoice line taxes total
		# only 1 line
		res = {
			'total': round(totalex,precision),
			'total_included': round(totalin,precision),
			'taxes': tin + tex
		}

		# raise osv.except_osv(_('Error!'),_('Error'))
		return res

class account_invoice_tax(osv.osv):

	_inherit = 'account.invoice.tax'

	"""BASED ON SBM INHERIT"""

	def compute(self, cr, uid, invoice_id, context=None):
		# tax_grouped = super(account_invoice_tax,self).compute(cr,uid,invoice_id,context=context)
		tax_grouped = {}
		
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
		cur = inv.currency_id
		company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
		dec_precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')


		for line in inv.invoice_line:
			if line.discount!=0.0:
				
				price = line.price_unit * (1-(line.discount or 0.0)/100.0)
			elif line.amount_discount!=0.0:
				
				price = line.price_unit - (line.amount_discount/line.quantity)
			else:
				price = line.price_unit
			
			for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, line.product_id, inv.partner_id, line_id=line.id,context=context)['taxes']:
				val={}
				val['invoice_id'] = inv.id
				val['name'] = tax['name']
				val['amount'] = tax['amount']
				val['manual'] = False
				val['sequence'] = tax['sequence']
				# val['base'] = round(tax['price_unit'] * line['quantity'],dec_precision)
				val['base'] = line.price_subtotal

				if inv.type in ('out_invoice','in_invoice'):
					val['base_code_id'] = tax['base_code_id']
					val['tax_code_id'] = tax['tax_code_id']

					val['base_amount'] = round(val['base'] * tax['base_sign'],dec_precision)
					
					val['tax_amount'] = math.floor(val['amount'] * tax['tax_sign'])
					val['account_id'] = tax['account_collected_id'] or line.account_id.id
					val['account_analytic_id'] = tax['account_analytic_collected_id']
				else:
					val['base_code_id'] = tax['ref_base_code_id']
					val['tax_code_id'] = tax['ref_tax_code_id']
					val['base_amount'] = round(val['base'] * tax['ref_base_sign'], dec_precision)
					val['tax_amount'] = round(val['amount'] * tax['ref_tax_sign'],dec_precision)
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
			t['base'] = round(t['base'],dec_precision)
			t['amount'] = round(t['amount'],dec_precision)
			t['base_amount'] = round(t['base_amount'],dec_precision)
			t['tax_amount'] = round(t['tax_amount'],dec_precision)
		return tax_grouped



class account_invoice(osv.osv):
	_inherit = 'account.invoice'
	def get_tax_amount_grouped(self,cr,uid,ids,context={}):
		res = {}
		total = {}
		for ai in self.browse(cr,uid,ids,context=context):

			for line in ai.invoice_line:

				tax_amount = {}
				base_amount = {}

				for ta in line.tax_amount_ids:				
					if ta.tax_id.id in tax_amount:
						tax_amount[ta.tax_id.id] += ta.tax_amount
					else:
						tax_amount[ta.tax_id.id] = ta.tax_amount


					if ta.tax_id.id in base_amount:
						base_amount[ta.tax_id.id] += ta.base_amount
					else:
						base_amount[ta.tax_id.id] = ta.base_amount

				res[ai.id] = {'tax_amount':tax_amount,'base_amount':base_amount}
			
		
		return res
	def button_reset_taxes(self, cr, uid, ids, context=None):
		
		if context is None:
			context = {}
		ctx = context.copy()
		ait_obj = self.pool.get('account.invoice.tax')
		# Update the stored value (fields.function), so we write to trigger recompute
		self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=ctx)
		print "AFTER CALLLLLLL---->"
		for id in ids:
			cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s", (id,))
			partner = self.browse(cr, uid, id, context=ctx).partner_id
			if partner.lang:
				ctx.update({'lang': partner.lang})
				ctx['button_reset_taxes'] = True
			for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
				# crate account.invoice.tax data
				
				ait_obj.create(cr, uid, taxe)
				# create account.invoice.line.tax.amount
		
		return True

	# def _get_analytic_lines(self, cr, uid, id, context=None):
	# 	if context is None:
	# 		context = {}
	# 	inv = self.browse(cr, uid, id)
	# 	cur_obj = self.pool.get('res.currency')

	# 	company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
	# 	if inv.type in ('out_invoice', 'in_refund'):
	# 		sign = 1
	# 	else:
	# 		sign = -1
	# 	iml = self.pool.get('account.invoice.line').move_line_get(cr, uid, inv.id, context=context)

	# 	for il in iml:
	# 		if il['account_analytic_id']:
	# 			if inv.type in ('in_invoice', 'in_refund'):
	# 				ref = inv.reference
	# 			else:
	# 				ref = self._convert_ref(cr, uid, inv.number)
	# 			if not inv.journal_id.analytic_journal_id:
	# 				raise osv.except_osv(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (inv.journal_id.name,))
	# 			il['analytic_lines'] = [(0,0, {
	# 				'name': il['name'],
	# 				'date': inv['date_invoice'],
	# 				'account_id': il['account_analytic_id'],
	# 				'unit_amount': il['quantity'],
	# 				'amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, il['price'], context={'date': inv.date_invoice}) * sign,
	# 				'product_id': il['product_id'],
	# 				'product_uom_id': il['uos_id'],
	# 				'general_account_id': il['account_id'],
	# 				'journal_id': inv.journal_id.analytic_journal_id.id,
	# 				'ref': ref,
	# 			})]
	# 	return iml

	# ****** ************************* *******
	# ****** ************************* *******
	# ****** REWRITE WORKFLOW FUNCTION *******
	# ****** ************************* *******
	# ****** ************************* *******
	def line_get_convert(self, cr, uid, x, part, date, context=None):
		return {
			'date_maturity': x.get('date_maturity', False),
			'partner_id': part,
			'name': x['name'] or 'INV '+str(part),
			'date': date,
			'debit': x['price']>0 and x['price'],
			'credit': x['price']<0 and -x['price'],
			'account_id': x['account_id'],
			'analytic_lines': x.get('analytic_lines', []),
			'amount_currency': x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
			'currency_id': x.get('currency_id', False),
			'tax_code_id': x.get('tax_code_id', False),
			'tax_amount': x.get('tax_amount', False),
			'ref': x.get('ref', False),
			'quantity': x.get('quantity',1.00),
			'product_id': x.get('product_id', False),
			'product_uom_id': x.get('uos_id', False),
			'analytic_account_id': x.get('account_analytic_id', False),
		}

		# return super(account_invoice,self).line_get_convert(cr,uid,x,part,date,context=context)

	def check_tax_lines(self, cr, uid, inv, compute_taxes, ait_obj):
		company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id
		if not inv.tax_line:

			for tax in compute_taxes.values():
				ait_obj.create(cr, uid, tax)

		else:
			tax_key = []
			for tax in inv.tax_line:
				key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id, tax.account_analytic_id.id)
				tax_key.append(key)
				if tax.manual:
					continue
				
				if not key in compute_taxes:
					raise osv.except_osv(_('Warning!'), _('Global taxes defined, but they are not in invoice lines !'))
				base = compute_taxes[key]['base']
				if abs(base - tax.base) > company_currency.rounding:
					raise osv.except_osv(_('Warning!'), _('Tax base different!\nClick on compute to update the tax base.'))

			for key in compute_taxes:
				
				if not key in tax_key:
					raise osv.except_osv(_('Warning!'), _('Taxes are missing!\nClick on compute button.'))
		# return super(account_invoice,self).check_tax_lines(cr,uid,inv,compute_taxes,ait_obj)

	def action_move_create(self, cr, uid, ids, context=None):
		"""Creates invoice related analytics and financial move lines"""
		
		ait_obj = self.pool.get('account.invoice.tax')
		cur_obj = self.pool.get('res.currency')
		period_obj = self.pool.get('account.period')
		payment_term_obj = self.pool.get('account.payment.term')
		journal_obj = self.pool.get('account.journal')
		move_obj = self.pool.get('account.move')
		move_line_obj = self.pool.get('account.move.line')
		
		if context is None:
			context = {}
		for inv in self.browse(cr, uid, ids, context=context):
			if not inv.journal_id.sequence_id:
				raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
			if not inv.invoice_line:
				raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
			if inv.move_id:
				continue

			ctx = context.copy()
			ctx.update({'lang': inv.partner_id.lang})
			if not inv.date_invoice:
				self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
			company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id

			# create the analytical lines
			# one move line per invoice line
			iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
			
			# check if taxes are all computed

			compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)

			
			self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

			# I disabled the check_total feature
			group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
			group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
			if group_check_total and uid in [x.id for x in group_check_total.users]:
				if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
					raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))


			if inv.payment_term:
				total_fixed = total_percent = 0
				for line in inv.payment_term.line_ids:
					if line.value == 'fixed':
						total_fixed += line.value_amount
					if line.value == 'procent':
						total_percent += line.value_amount
				total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)


				if (total_fixed + total_percent) > 100:
					raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

			# one move line per tax line
			iml += ait_obj.move_line_get(cr, uid, inv.id)

			entry_type = ''
			if inv.type in ('in_invoice', 'in_refund'):
				ref = inv.reference
				entry_type = 'journal_pur_voucher'
				if inv.type == 'in_refund':
					entry_type = 'cont_voucher'
			else:
				ref = self._convert_ref(cr, uid, inv.number)
				entry_type = 'journal_sale_vou'
				if inv.type == 'out_refund':
					entry_type = 'cont_voucher'

			diff_currency_p = inv.currency_id.id <> company_currency


			# create one move line for the total and possibly adjust the other lines amount
			total = 0
			total_currency = 0
			total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
			acc_id = inv.account_id.id
			# udah pak, silahkan dicoba dulu
			# if diff_currency_p:
			#     for i in iml:
			#         if inv.pajak:
			#             if i['price'] < 0:
			#                 i['price'] = cur_obj.round(cr,uid,self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id,(i['amount_currency'] * inv.pajak))
			#             else:
			#                 i['price'] = cur_obj.round(cr,uid,self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id,i['amount_currency'] * inv.pajak)
			
			name = inv['name'] or inv['supplier_invoice_number']
			# name = inv['name'] or inv['supplier_invoice_number'] or '/'
			totlines = False
			if inv.payment_term:
				totlines = payment_term_obj.compute(cr,
						uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
			if totlines:
				res_amount_currency = total_currency
				i = 0
				ctx.update({'date': inv.date_invoice})
				for t in totlines:
					if inv.currency_id.id != company_currency:
						amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)

					else:
						amount_currency = False
					# last line add the diff
					res_amount_currency -= amount_currency or 0
					i += 1
					if i == len(totlines):
						amount_currency += res_amount_currency

					iml.append({
						'type': 'dest',
						'name': name,
						'price': t[1],
						'account_id': acc_id,
						'date_maturity': t[0],
						'amount_currency': diff_currency_p \
								and amount_currency or False,
						'currency_id': diff_currency_p \
								and inv.currency_id.id or False,
						'ref': ref,
					})
			else:
				iml.append({
					'type': 'dest',
					'name': name,
					'price': total,
					'account_id': acc_id,
					'date_maturity': inv.date_due or False,
					'amount_currency': diff_currency_p \
							and total_currency or False,
					'currency_id': diff_currency_p \
							and inv.currency_id.id or False,
					'ref': ref
			})

			date = inv.date_invoice or time.strftime('%Y-%m-%d')

			part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

			line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

			line = self.group_lines(cr, uid, iml, line, inv)

			journal_id = inv.journal_id.id
			journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
			if journal.centralisation:
				raise osv.except_osv(_('User Error!'),
						_('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

			line = self.finalize_invoice_move_lines(cr, uid, inv, line)

			move = {
				'ref': inv.reference and inv.reference or inv.name,
				'line_id': line,
				'journal_id': journal_id,
				'date': date,
				'narration': inv.comment,
				'company_id': inv.company_id.id,
			}
			period_id = inv.period_id and inv.period_id.id or False
			ctx.update(company_id=inv.company_id.id,
					   account_period_prefer_normal=True)
			if not period_id:
				period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
				period_id = period_ids and period_ids[0] or False
			if period_id:
				move['period_id'] = period_id
				for i in line:
					i[2]['period_id'] = period_id

			ctx.update(invoice=inv)
			move_id = move_obj.create(cr, uid, move, context=ctx)
			
			new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
			# make the invoice point to that move
			self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
			# Pass invoice in context in method post: used if you want to get the same
			# account move reference when creating the same invoice after a cancelled one:
			
			move_obj.post(cr, uid, [move_id], context=ctx)
		self._log_event(cr, uid, ids)
		return True
		# return super(account_invoice,self).action_move_create(cr, uid, ids, context=context)

class account_invoice_line(osv.osv):
	_inherit = 'account.invoice.line'
	_columns = {
		'tax_amount_ids': fields.one2many('account.invoice.line.tax.amount','invoice_line_id',string="Tax Lines"),
	}

	# def move_line_get(self, cr, uid, invoice_id, context=None):
	# 	res = []
	# 	tax_obj = self.pool.get('account.tax')
	# 	cur_obj = self.pool.get('res.currency')
	# 	if context is None:
	# 		context = {}
	# 	inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
	# 	company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
	# 	for line in inv.invoice_line:
	# 		mres = self.move_line_get_item(cr, uid, line, context)
	# 		if not mres:
	# 			continue
	# 		res.append(mres)
	# 		tax_code_found= False
	# 		for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id,
	# 				(line.price_unit * (1.0 - (line['discount'] or 0.0) / 100.0)),
	# 				line.quantity, line.product_id,
	# 				inv.partner_id)['taxes']:

	# 			if inv.type in ('out_invoice', 'in_invoice'):
	# 				tax_code_id = tax['base_code_id']
	# 				tax_amount = line.price_subtotal * tax['base_sign']
	# 			else:
	# 				tax_code_id = tax['ref_base_code_id']
	# 				tax_amount = line.price_subtotal * tax['ref_base_sign']

	# 			if tax_code_found:
	# 				if not tax_code_id:
	# 					continue
	# 				res.append(self.move_line_get_item(cr, uid, line, context))
	# 				res[-1]['price'] = 0.0
	# 				res[-1]['account_analytic_id'] = False
	# 			elif not tax_code_id:
	# 				continue
	# 			tax_code_found = True

	# 			res[-1]['tax_code_id'] = tax_code_id
	# 			res[-1]['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, tax_amount, context={'date': inv.date_invoice})
	# 	return res