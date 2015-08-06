import re
import time
import netsvc
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta


class account_invoice(osv.osv):
	def _amount_all_main(self, cr, uid, ids, name, args, context=None):
		res = {}
		for invoice in self.browse(cr, uid, ids, context=context):
			res[invoice.id] = {
				'amount_untaxed_main': 0.0,
				'amount_tax_main': 0.0,
				'amount_total_main': 0.0
			}
			
			if invoice.pajak==0.0:
				for line in invoice.invoice_line:
					res[invoice.id]['amount_untaxed_main'] += round(line.price_subtotal)
				for line in invoice.tax_line:
					res[invoice.id]['amount_tax_main'] += round(line.amount)
				res[invoice.id]['amount_total_main'] = res[invoice.id]['amount_tax_main'] + res[invoice.id]['amount_untaxed_main']
			else: 
				for line in invoice.invoice_line:
					res[invoice.id]['amount_untaxed_main'] += round(line.price_subtotal*invoice.pajak)
				for line in invoice.tax_line:
					res[invoice.id]['amount_tax_main'] += round(line.amount*invoice.pajak)
				res[invoice.id]['amount_total_main'] = res[invoice.id]['amount_tax_main'] + res[invoice.id]['amount_untaxed_main']
		return res

	_inherit = "account.invoice"
	_columns = {
			'invoice_line_main': fields.one2many('account.invoice.line', 'invoice_id', 'Invoice Lines Main', readonly=True, states={'draft':[('readonly',True)]}),
			'amount_untaxed_main': fields.function(_amount_all_main, digits_compute=dp.get_precision('Account'), string='Subtotal IDR', track_visibility='always',
			store=True,
			multi='all'),
			'amount_tax_main': fields.function(_amount_all_main, digits_compute=dp.get_precision('Account'), string='Tax IDR',
				store=True,
				multi='all'),
			'amount_total_main': fields.function(_amount_all_main, digits_compute=dp.get_precision('Account'), string='Total IDR',
				store=True,
				multi='all'),
	}

	def write(self,cr,uid,ids,vals,context={}):
		line_obj = self.pool.get('account.invoice.line')
		line_tax = self.pool.get('account.invoice.tax')
		if 'pajak' in vals:
			pajak=vals['pajak']
			for invoice in self.browse(cr, uid, ids, context=context):
				if pajak==0.0:
					for line in invoice.invoice_line:
						unit_price_main = round(line.price_unit)
						sub_total_main = round(line.price_unit*line.quantity)
						# Update Invoice Line
						line_obj.write(cr, uid, [line.id], {'unit_price_main': unit_price_main})
						line_obj.write(cr, uid, [line.id], {'sub_total_main': unit_price_main})
				else:
					for line in invoice.invoice_line:
						unit_price_main = round(line.price_unit*pajak)
						sub_total_main = round((line.price_unit*line.quantity)*pajak)

						# Update Line Invoice dikali dengan Rate Tax
						line_obj.write(cr, uid, [line.id], {'unit_price_main': unit_price_main})
						line_obj.write(cr, uid, [line.id], {'sub_total_main': sub_total_main})

					for linetax in invoice.tax_line:
						base_main = round(linetax.base*pajak)
						tax_main = round(linetax.amount*pajak)

						# Update Line tax Invoice dikali dengan Rate
						line_tax.write(cr, uid, [linetax.id], {'base_main': base_main})
						line_tax.write(cr, uid, [linetax.id], {'tax_main': tax_main})
		return super(account_invoice, self).write(cr, uid, ids, vals, context=context)
		
account_invoice()


class account_invoice_line(osv.osv):
	
	_inherit = "account.invoice.line"
	_description = "Invoice Line"

	def _sub_total_main(self, cr, uid, ids, prop, unknow_none, unknow_dict):	
		res = {}
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		for line in self.browse(cr, uid, ids):
			price = line.price_unit * (1-(line.discount or 0.0)/100.0)
			taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			res[line.id] = taxes['total']
			if line.invoice_id:
				cur = line.invoice_id.currency_id
				res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
		return res

	def _unit_price_main(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		for line in self.browse(cr, uid, ids):
			price = line.price_unit * (1-(line.discount or 0.0)/100.0)
			taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
			res[line.id] = taxes['total']
			if line.invoice_id:
				cur = line.invoice_id.currency_id
				res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
		return res

	_columns = {
		'unit_price_main': fields.float('Unit Price Main'),
		'sub_total_main': fields.float('Sub Total Main'),
	}

account_invoice_line()



class account_invoice_line_main(osv.osv):
	_name = "account.invoice.line.main"
	_description = "Invoice Line Main"
	_columns = {
		'name': fields.text('Description', required=True),
		'origin': fields.char('Source Document', size=256, help="Reference of the document that produced this invoice."),
		'sequence': fields.integer('Sequence', help="Gives the sequence of this line when displaying the invoice."),
		'invoice_id': fields.many2one('account.invoice', 'Invoice Reference', ondelete='cascade', select=True),
		'uos_id': fields.many2one('product.uom', 'Unit of Measure', ondelete='set null', select=True),
		'product_id': fields.many2one('product.product', 'Product', ondelete='set null', select=True),
		'account_id': fields.many2one('account.account', 'Account', required=False, domain=[('type','<>','view'), ('type', '<>', 'closed')], help="The income or expense account related to the selected product."),
		'price_unit_main': fields.float('Unit Price Main'),
		'price_subtotal_main': fields.float('Unit Price Main'),
		'quantity': fields.float('Quantity', digits_compute= dp.get_precision('Product Unit of Measure'), required=False),
		'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
		'invoice_line_tax_id': fields.many2many('account.tax', 'account_invoice_line_tax', 'invoice_line_id', 'tax_id', 'Taxes', domain=[('parent_id','=',False)]),
		'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
		'company_id': fields.related('invoice_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
		'partner_id': fields.related('invoice_id','partner_id',type='many2one',relation='res.partner',string='Partner',store=True)
	}

class account_invoice_tax(osv.osv):
	_inherit = 'account.invoice.tax'

	_columns = {
		'base_main': fields.float('Base Main'),
		'tax_main': fields.float('Tax Main'),
	}

account_invoice_tax()
