import time
from openerp.tools.translate import _
from osv import fields, osv, orm


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'opportunity_id': fields.many2one('sale.order', 'Qoutation')
    }
sale_order()


class crm_lead(osv.osv):
    
    _inherit = "crm.lead"
    _columns = {
        'project': fields.char('Project', size=64),
        'phone_lines': fields.one2many('crm.phonecall', 'opportunity_id', 'Logged Call'),
        'meeting_lines': fields.one2many('crm.meeting', 'opportunity_id', 'Meetings'),
        'status_lines': fields.one2many('log.status', 'opportunity_id', 'Status'),
        'quotation_lines': fields.one2many('sale.order', 'opportunity_id', 'Quotation', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)])
    }

crm_lead()


class log_status(osv.osv):
    _name = "log.status"
    _columns = {
        'name': fields.text('Status'),
        'week': fields.selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], 'Week'),
        'month':fields.selection([('01','January'), ('02','February'), ('03','March'), ('04','April'),
                                  ('05','May'), ('06','June'), ('07','July'), ('08','August'), ('09','September'),
                                  ('10','October'), ('11','November'), ('12','December')], 'Month'),
        'opportunity_id': fields.many2one('crm.lead', 'Opportunity', required=True, ondelete='cascade'),
    }
    
log_status()


class crm_meeting(osv.Model):
    _inherit = 'crm.meeting'
    
    def create(self, cr, uid, vals, context=None):
        if vals['phonecall_id']:
            phone = self.pool.get('crm.phonecall').browse(cr, uid, vals['phonecall_id'])
            vals['opportunity_id'] = phone.opportunity_id.id
            self.pool.get('crm.lead').log_meeting(cr, uid, [phone.opportunity_id.id], vals['name'], vals['date'], vals['duration'], context=context)
        return super(crm_meeting, self).create(cr, uid, vals, context=context)
 
crm_meeting()



class crm_make_sale(osv.osv_memory):
    _inherit = "crm.make.sale"
    
    def makeOrder(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.pop('default_state', False)        
        
        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id], ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id], ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))
                     
                vals = {
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'shop_id': make.shop_id.id,
                    'partner_id': partner.id,
                    'opportunity_id': case.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': fields.date.context_today(self,cr,uid,context=context),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals, context=context)
                
                order_line = []
                if case.product_id:
                    persen = 0.1
                    if case.probability:
                        persen = case.probability/100
                    order_line = [sale_line_obj.create(cr, uid, {
                            'order_id': new_id,
                            'name': '[' + case.product_id.code + '] ' + case.product_id.name,
                            'product_id': case.product_id.id,
                            'product_qty': 1,
                            'product_uom': 1,
                            'price_unit': case.planned_revenue * persen
                            #'company_id': 1,
                        })]
                    
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)
            if make.close:
                case_obj.case_close(cr, uid, data)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value
        
crm_make_sale()
