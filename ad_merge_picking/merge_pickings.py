# -*- encoding: utf-8 -*-
import time
from osv import fields, osv
from tools.translate import _

class account_invoice(osv.osv):

    _inherit = "account.invoice"
    _columns = {
        'picking_ids': fields.one2many('stock.picking','invoice_id', 'Delivery Orders'),
    }
    
account_invoice()

class stock_picking(osv.osv):

    _inherit = "stock.picking"
    _columns = {
        'invoice_id': fields.many2one('account.invoice','Invoice')
    }
    
stock_picking()

    
class merge_pickings(osv.osv_memory):
    _name = "merge.pickings"
    _columns = {
        'partner_id': fields.many2one('res.partner','Partner', required=True),
        'type': fields.selection([('out', 'Customer Invoice (AR)'), ('in', 'Supplier Invoice (AP)')], 'Type', readonly=False, select=True, required=True),
        'picking_ids': fields.many2many('stock.picking','merge_do_picking_rel','merge_do_id','picking_id','Pickings', required=True, domain="[('state', '=', 'done'), ('type', '=', type), ('partner_id', '=', partner_id)]"),
    }
    
    _defaults = {'type' : 'in'}
    
    def partner_id_change(self, cr, uid, ids):
        return {'value':{'picking_ids': None}}
    
    def type_change(self, cr, uid, ids, tipe):
        domain = {'partner_id': [('customer', '=', True)]}
        if tipe == 'in':
            domain = {'partner_id': [('supplier', '=', True)]}
        return {'value':{'picking_ids':None, 'partner_id': None}, 'domain': domain}
                
    def merge_orders(self, cr, uid, ids, context={}):
        pool_data = self.pool.get('ir.model.data')
        journal_obj = self.pool.get('account.journal')
        pool_invoice = self.pool.get('account.invoice')
        pool_picking = self.pool.get('stock.picking')
        pool_partner = self.pool.get('res.partner')
        pool_invoice_line = self.pool.get('account.invoice.line')
        
        data = self.browse(cr, uid, ids, context=context)[0]
        picking_ids = [x.id for x in data['picking_ids']]
        partner_obj = data['partner_id']
        
        alamat = pool_partner.address_get(cr, uid, [partner_obj.id],['contact', 'invoice'])
        address_contact_id = alamat['contact']
        address_invoice_id = alamat['invoice']
               
        picking = pool_picking.browse(cr, uid, picking_ids[0], context=context)
                 
        if data.type == 'out':
            type_inv = 'out_invoice'
            account_id = partner_obj.property_account_receivable.id
            curency = picking.sale_id.pricelist_id.currency_id.id
            journal_ids = journal_obj.search(cr, uid, [('type','=','sale'),('company_id', '=', 1)], limit=1)
        elif data.type == 'in':
            type_inv = 'in_invoice'
            account_id = partner_obj.property_account_payable.id
            curency = picking.purchase_id.pricelist_id.currency_id.id
            journal_ids = journal_obj.search(cr, uid, [('type','=','purchase'),('company_id', '=', 1)], limit=1)
        
        if not journal_ids:
            raise osv.except_osv(('Error !'), ('There is no sale/purchase journal defined for this company'))            
         
        invoice_id = pool_invoice.create(cr, uid, {
            'name': 'Merged Invoice for '+ partner_obj.name + ' on ' + time.strftime('%Y-%m-%d %H:%M:%S'),
            'type': type_inv,
            'account_id': account_id,
            'partner_id': partner_obj.id,
            'journal_id': journal_ids[0] or False,
            'address_invoice_id': address_invoice_id,
            'address_contact_id': address_contact_id,
            'date_invoice': time.strftime('%Y-%m-%d'),
            'user_id': uid,
            'currency_id': curency or False,
            'picking_ids': [(6,0, picking_ids)]})

        for picking in pool_picking.browse(cr, uid, picking_ids, context=context):
            pool_picking.write(cr, uid, [picking.id], {'invoice_state': 'invoiced', 'invoice_id': invoice_id}) 
            disc_amount = 0
            for move_line in picking.move_lines:
                
                if data.type == 'out':
                    price_unit = pool_picking._get_price_unit_invoice(cr, uid, move_line, 'out_invoice')
                    tax_ids = pool_picking._get_taxes_invoice(cr, uid, move_line, 'out_invoice')
                    line_account_id = move_line.product_id.product_tmpl_id.property_account_income.id or move_line.product_id.categ_id.property_account_income_categ.id
                elif data.type == 'in':
                    price_unit = pool_picking._get_price_unit_invoice(cr, uid, move_line, 'in_invoice')
                    tax_ids = pool_picking._get_taxes_invoice(cr, uid, move_line, 'in_invoice')
                    line_account_id = move_line.product_id.product_tmpl_id.property_account_expense.id or move_line.product_id.categ_id.property_account_expense_categ.id
                    disc_amount = move_line.purchase_line_id.discount_nominal
                discount = pool_picking._get_discount_invoice(cr, uid, move_line)
                 
                origin = picking.origin +':'+ (picking.name).strip()
                #origin = (picking.delivery_note).strip() +';'+ (picking.name).strip()
                                                
                pool_invoice_line.create(
                    cr, uid, 
                    {
                        'name': move_line.name,
                        'picking_id': picking.id,
                        'origin': origin,
                        'uos_id': move_line.product_uos.id or move_line.product_uom.id,
                        'product_id': move_line.product_id.id,
                        'price_unit': price_unit,
                        'discount': discount,
                        'quantity': move_line.product_qty,
                        'invoice_id': invoice_id,
                        'invoice_line_tax_id': [(6, 0, tax_ids)],
                        'account_analytic_id': pool_picking._get_account_analytic_invoice(cr, uid, picking, move_line),
                        'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, partner_obj.property_account_position, line_account_id),
                        'amount_discount':disc_amount
                    }
                ),

        
        pool_invoice.button_compute(cr, uid, [invoice_id], context=context, set_total=False)           
        action_model,action_id = pool_data.get_object_reference(cr, uid, 'account', "invoice_form")
        if data.type == 'in':
            action_model,action_id = pool_data.get_object_reference(cr, uid, 'account', "invoice_supplier_form")
         
        action_pool = self.pool.get(action_model)
        res_id = action_model and action_id or False
        action = action_pool.read(cr, uid, action_id, context=context)
        action['name'] = 'Merged Invoice'
        action['view_type'] = 'form'
        action['view_mode'] = 'form'
        action['view_id'] = [res_id]
        action['res_model'] = 'account.invoice'
        action['type'] = 'ir.actions.act_window'
        action['target'] = 'current'
        action['res_id'] = invoice_id
        return action
    
merge_pickings()






