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



class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
 
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
            if line.discount_nominal:
                harga = (price*line.product_uom_qty-line.discount_nominal)
                taxes = tax_obj.compute_all(cr, uid, line.tax_id, harga, 1, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'discount_nominal': fields.float('Amount Discount', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),
    }
 
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

