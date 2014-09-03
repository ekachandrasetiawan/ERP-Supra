from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
import openerp.addons.decimal_precision as dp

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _defaults = {
        'invoice_method': 'picking',
    }

purchase_order()


class purchase_partial_invoice(osv.osv_memory):
    _name = "purchase.partial.invoice"
    _columns = {
        'amount': fields.float('Advance Amount (%)', required=True, digits_compute= dp.get_precision('Account')),
    }

    _defaults = {
        'amount': 10,
    }

    def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        purchase_obj = self.pool.get('purchase.order')
        inv_line_obj = self.pool.get('account.invoice.line')
        wizard = self.browse(cr, uid, ids[0], context)
        purchase_ids = context.get('active_ids', [])

        result = []
        for purchase in purchase_obj.browse(cr, uid, purchase_ids, context=context):
            val = inv_line_obj.product_id_change(cr, uid, [], purchase.order_line[0].product_id.id, uom_id=False, partner_id=purchase.partner_id.id, fposition_id=purchase.fiscal_position.id)
            res = val['value']

            # determine invoice amount
            if wizard.amount <= 0.00:
                raise osv.except_osv(_('Incorrect Data'), _('The value of Advance Amount must be positive.'))
            
            inv_amount = purchase.amount_total * wizard.amount / 100
            if not res.get('name'):
                res['name'] = _("Advance of %s %%") % (wizard.amount)
           
#             if res.get('invoice_line_tax_id'):
#                 res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
#             else:
#                 res['invoice_line_tax_id'] = False

            # create the invoice
            inv_line_values = {
                'name': res.get('name'),
                'origin': purchase.name,
                'account_id': res['account_id'],
                'price_unit': inv_amount,
                'quantity': 1.0,
                'uos_id': res.get('uos_id', False),
                'product_id': purchase.order_line[0].product_id.id,
                'invoice_line_tax_id': False #res.get('invoice_line_tax_id'),
            }
            
            inv_values = {
                'name': purchase.partner_ref or purchase.name,
                'origin': purchase.name,
                'type': 'in_invoice',
                'account_id': purchase.partner_id.property_account_payable.id,
                'partner_id': purchase.partner_id.id,
                'invoice_line': [(0, 0, inv_line_values)],
                'currency_id': purchase.pricelist_id.currency_id.id,
                'fiscal_position': purchase.fiscal_position.id or purchase.partner_id.property_account_position.id
            }
            result.append((purchase.id, inv_values))
        return result

    def _create_invoices(self, cr, uid, inv_values, purchase_id, context=None):
        inv_obj = self.pool.get('account.invoice')
        purchase_obj = self.pool.get('purchase.order')
        inv_id = inv_obj.create(cr, uid, inv_values, context=context)
        inv_obj.button_reset_taxes(cr, uid, [inv_id], context=context)
        # add the invoice to the sales order's invoices
        purchase_obj.write(cr, uid, purchase_id, {'invoice_ids': [(4, inv_id)]}, context=context)
        return inv_id


    def create_invoices(self, cr, uid, ids, context=None):
        purchase_obj = self.pool.get('purchase.order')
        wizard = self.browse(cr, uid, ids[0], context)
        purchase_ids = context.get('active_ids', [])
        
        inv_ids = []
        for purchase_id, inv_values in self._prepare_advance_invoice_vals(cr, uid, ids, context=context):
            inv_ids.append(self._create_invoices(cr, uid, inv_values, purchase_id, context=context))

        return {'type': 'ir.actions.act_window_close'}


purchase_partial_invoice()




