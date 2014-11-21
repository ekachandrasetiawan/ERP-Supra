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


class PurchaseOrder(osv.osv):
    _inherit = "purchase.order"

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                # print '====================',line.state
                val1 += line.price_subtotal
                pajak = self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, order.partner_id)['taxes']
                if line.discount_nominal:
                    harga = (line.price_unit*line.product_qty-line.discount_nominal)
                    pajak = self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, harga, 1, line.product_id, order.partner_id)['taxes']
                if line.discount:
                    pricediscount = (line.price_unit *line.product_qty) * (1 - (line.discount or 0.0) / 100.0)      
                    subtotalPrice = (line.price_unit*line.product_qty)-pricediscount
                    harga=(line.price_unit*line.product_qty)-subtotalPrice
                    pajak = self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, harga, 1, line.product_id, order.partner_id)['taxes']
                if pajak:
                    val += pajak[0].get('amount', 0.0)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            # res[order.id]['amount_untaxed']=0
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
            # print '==================EKA CHANDRA'
        return res

    def action_cancel_draft(self, cr, uid, ids, context=None):
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state':'draft','shipped':0})
        for p_id in ids:
            a=self.browse(cr, uid, ids)[0].order_line
            for line in a:
                self.pool.get("purchase.order.line").write(cr, uid, [line.id], {'state':'draft'})
        return super(PurchaseOrder,self).action_cancel_draft(cr,uid,ids,context=context)

    _columns = {       
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'purchase.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
    }
 
PurchaseOrder()



class PurchaseOrderLine(osv.osv):
    _inherit = "purchase.order.line"
 
    # def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
    #     tax_obj = self.pool.get('account.tax')
    #     cur_obj = self.pool.get('res.currency')
    #     res = {}
    #     if context is None:
    #         context = {}
    #     for line in self.browse(cr, uid, ids, context=context):
    #         price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
    #         if line.discount_nominal:
    #             harga = (price*line.product_uom_qty-line.discount_nominal)
    #             taxes = tax_obj.compute_all(cr, uid, line.tax_id, harga, 1, line.product_id, line.order_id.partner_id)
    #         cur = line.order_id.pricelist_id.currency_id
    #         res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
    #     return res

    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, line.order_id.partner_id)
            if line.discount_nominal:
                harga = (line.price_unit*line.product_qty-line.discount_nominal)
                taxes = tax_obj.compute_all(cr, uid, line.taxes_id, harga, 1, line.product_id, line.order_id.partner_id)
            if line.discount:
                pricediscount = (line.price_unit *line.product_qty) * (1 - (line.discount or 0.0) / 100.0)      
                harga = (line.price_unit*line.product_qty)-pricediscount
                subtotalPrice=(line.price_unit*line.product_qty)-harga
                taxes = tax_obj.compute_all(cr, uid, line.taxes_id, subtotalPrice, 1, line.product_id, line.order_id.partner_id)

            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'discount_nominal': fields.float('Amount Discount', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),
    }

    _defaults = {
        'state': 'draft'
    }
 
PurchaseOrderLine()
