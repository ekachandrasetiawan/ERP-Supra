##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from osv import fields
from osv import osv
import decimal_precision as dp
from openerp.tools.float_utils import float_round


class sale_order(osv.osv):
	_inherit = "sale.order"
	
	def _amount_line_tax(self, cr, uid, line, context=None):
		val = 0.0
		data = self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']
		if line.discount_nominal:
			harga = (line.price_unit*line.product_uom_qty-line.discount_nominal)
			data = self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, harga, 1, line.product_id, line.order_id.partner_id)['taxes']
		for c in data:
			val += c.get('amount', 0.0)
		return val

	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
			result[line.order_id.id] = True
		return result.keys()

	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		cur_obj = self.pool.get('res.currency')
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0,
			}
			val = val1 = 0.0
			cur = order.pricelist_id.currency_id

			user_obj = self.pool.get('res.users')
			currency_obj = self.pool.get('res.currency')
			user = user_obj.browse(cr, uid, uid, context=context)

			if cur.id ==user.company_id.currency_id.id:
				# Rounding Tax dan Subtotal 
				for line in order.order_line:
					val1 += round(line.price_subtotal)
					val += round(self._amount_line_tax(cr, uid, line, context=context))
			else:
				for line in order.order_line:
					val1 += line.price_subtotal
					val += self._amount_line_tax(cr, uid, line, context=context)
					
			res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
			res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
			res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
		return res


	_columns = {       
		'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
			},
			multi='sums', help="The amount without tax.", track_visibility='always'),
		'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
			},
			multi='sums', help="The tax amount."),
		'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
			store={
				'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
				'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
			},
			multi='sums', help="The total amount."),
	}
 
sale_order()


class res_currency(osv.osv):

	_inherit = "res.currency"

	def round(self, cr, uid, currency, amount):
		"""Return ``amount`` rounded  according to ``currency``'s
		   rounding rules.

		   :param browse_record currency: currency for which we are rounding
		   :param float amount: the amount to round
		   :return: rounded float
		"""
		res = super(res_currency, self).round(cr,uid,currency,amount)

		user_obj = self.pool.get('res.users')
		currency_obj = self.pool.get('res.currency')
		user = user_obj.browse(cr, uid, uid, {})

		if (currency.id==user.company_id.currency_id.id):
			res = round(amount)
		return res

res_currency()

		
class sale_order_line(osv.osv):
	_inherit = "sale.order.line"

	def _amount_line(self, cr, uid, ids, field_name, arg, context=None):

		# res = super(sale_order_line, self)._amount_line(cr,uid,ids, field_name, arg, context=None)

		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		
		user_obj = self.pool.get('res.users')
		currency_obj = self.pool.get('res.currency')
		user = user_obj.browse(cr, uid, uid, context=context)

		res = {}
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			price = line.price_unit
			taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
			cur = line.order_id.pricelist_id.currency_id
			if (line.order_id.pricelist_id.currency_id.id==user.company_id.currency_id.id):
				res[line.id] = cur_obj.round(cr, uid, cur, taxes['total']- line.discount_nominal)
			else:
				res[line.id] = cur_obj.round(cr, uid, cur, taxes['total']-line.discount_nominal)
				
		return res

	_columns = {
		'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
		'discount_nominal': fields.float('Amount Discount', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),
		'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),
	}
 

	def replace_discount(self,cr,uid,ids,qty,price, disc):
		subtotal = qty*price
		nilai = (subtotal*disc)/100
		return {'value':{ 'discount_nominal':nilai} }

	def on_change_price_unit(self,cr,uid,ids,price):

		return {'value':{ 'discount_nominal':0, 'discount':0,} }

		
sale_order_line()