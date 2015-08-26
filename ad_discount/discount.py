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


class account_tax(osv.osv):

	_inherit = 'account.tax'

	def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, force_excluded=False):
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
		precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
		tax_compute_precision = precision
		if taxes and taxes[0].company_id.tax_calculation_rounding_method == 'round_globally':
			tax_compute_precision += 5
		totalin = totalex = float_round(price_unit * quantity, precision)
		# totalin = totalex = round(price_unit * quantity)
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
		tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=tax_compute_precision)
		for r in tex:
			totalin += r.get('amount', 0.0)
		return {
			'total': totalex,
			'total_included': totalin,
			'taxes': tin + tex
		}
		return super( account_tax, self)._invoice_line_hook( cr, uid, move_line,invoice_line_id )

account_tax()
	   
class sale_order_line(osv.osv):
	_inherit = "sale.order.line"

	def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
		
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		
		user_obj = self.pool.get('res.users')
		currency_obj = self.pool.get('res.currency')
		user = user_obj.browse(cr, uid, uid, context=context)

		res = {}
		if context is None:
			context = {}
		for line in self.browse(cr, uid, ids, context=context):
			# if (line.order_id.pricelist_id.currency_id.id==user.company_id.currency_id.id):
			# 	# Jika IDR maka di Rounding
			# 	# price=(line.price_unit*line.product_uom_qty)-line.discount_nominal
			# 	price = line.price_unit
			# 	# price = round(nilai1/line.product_uom_qty)
			# else:
			price = line.price_unit

			taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
			
			
			cur = line.order_id.pricelist_id.currency_id
			if (line.order_id.pricelist_id.currency_id.id==user.company_id.currency_id.id):
				res[line.id] = cur_obj.round(cr, uid, cur, round(taxes['total']))
			else:
				res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
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

		
sale_order_line()


# class purchase_order_line(osv.osv):
#     _name = "purchase.order.line"
#     _inherit = "purchase.order.line"
# 
#     def _amount_line(self, cr, uid, ids, prop, unknow_none,unknow_dict):
#         res = {}
#         cur_obj = self.pool.get('res.currency')
#         for line in self.browse(cr, uid, ids):
#             cur = line.order_id.pricelist_id.currency_id
#             res[line.id] = cur_obj.round(cr, uid, cur, (line.price_unit-line.discount_nominal) * line.product_qty)
#             if line.discount:
#                 res[line.id] = cur_obj.round(cr, uid, cur, line.price_unit * line.product_qty * (1 - (line.discount or 0.0) /100.0))
#         return res
# 
#     _columns = {
#         'discount': fields.float('Discount (%)', digits=(16,2)),
#         'discount_nominal': fields.integer('Discount (Rp)'),
#         'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
#     }
# 
# purchase_order_line()
# 
# class purchase_order(osv.osv):
#     _name = "purchase.order"
#     _inherit = "purchase.order"
#     
#     def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
#         res = {}
#         cur_obj=self.pool.get('res.currency')
#         for order in self.browse(cr, uid, ids, context=context):
#             res[order.id] = {
#                 'amount_untaxed': 0.0,
#                 'amount_tax': 0.0,
#                 'amount_total': 0.0,
#             }
#             harga = 0.0
#             val = val1 = 0.0
#             cur = order.pricelist_id.currency_id
#             for line in order.order_line:
#                val1 += line.price_subtotal
#                harga = line.price_unit - line.discount_nominal
#                if line.discount:
#                    harga = line.price_unit * (1-(line.discount or 0.0)/100.0)
#                for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, harga, line.product_qty, order.partner_address_id.id, line.product_id.id, order.partner_id)['taxes']:
#                     val += c.get('amount', 0.0)
#             res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
#             res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
#             res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']              
#         return res
#     
#     def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
#         return {
#             'name': order_line.name,
#             'account_id': account_id,
#             'price_unit': order_line.price_unit or 0.0,
#             'quantity': order_line.product_qty,
#             'discount': order_line.discount,
#             'discount_nominal': order_line.discount_nominal,
#             'product_id': order_line.product_id.id or False,
#             'uos_id': order_line.product_uom.id or False,
#             'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
#             'account_analytic_id': order_line.account_analytic_id.id or False,
#         }
# 
#     def _get_order(self, cr, uid, ids, context=None):
#         result = {}
#         for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
#             result[line.order_id.id] = True
#         return result.keys()
# 
#     _columns = {
#         'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
#             store={
#                 'purchase.order.line': (_get_order, None, 10),
#             }, multi="sums", help="The amount without tax"),
#         'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Taxes',
#             store={
#                 'purchase.order.line': (_get_order, None, 10),
#             }, multi="sums", help="The tax amount"),
#         'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Account'), string='Total',
#             store={
#                 'purchase.order.line': (_get_order, None, 10),
#             }, multi="sums",help="The total amount"),
#     }
# 
# purchase_order()
# 
# 
# 
# class account_invoice_line(osv.osv):
#     _inherit = "account.invoice.line"
#     _columns = {
#         'discount_nominal': fields.integer('Discount (Rp)'),
#     }
#     
# account_invoice_line()
# 
# class stock_picking( osv.osv ):
#     _inherit =  'stock.picking'
# 
#     def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
#         if move_line.purchase_line_id:
#             self.pool.get('account.invoice.line').write( cr, uid, [invoice_line_id], {        
#                 'discount':move_line.purchase_line_id.discount or move_line.purchase_line_id.discount_nominal, 
#                 } )
#         return super( stock_picking, self)._invoice_line_hook( cr, uid, move_line,invoice_line_id )
# 
# stock_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

