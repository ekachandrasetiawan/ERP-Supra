from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import openerp.exceptions
from lxml import etree
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp.tools.float_utils import float_compare


class delivery_note(osv.osv):
	_inherit = "delivery.note"
	_columns = {
		'note_lines': fields.one2many('delivery.note.line', 'note_id', 'Note Lines', readonly=True, states={'draft': [('readonly', False)]}),
		'picking_id': fields.many2one('stock.picking', 'Stock Picking', domain=[('type', '=', 'out')], required=False),
		'postpone_picking': fields.many2one('stock.picking', 'Postpone Picking', required=False),
		'state': fields.selection([('draft', 'Draft'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel'), ('torefund', 'To Refund'), ('refunded', 'Refunded'),('postpone', 'Postpone')], 'State', readonly=True,track_visibility='onchange'),
	}

	def prepare_change(self, cr, uid, ids, pre):
		res = super(delivery_note,self).prepare_change(cr, uid, ids, pre)
		if pre :
			res = {}; line = []
			

			data = self.pool.get('order.preparation').browse(cr, uid, pre)
			dnid = self.pool.get('delivery.note').search(cr, uid, [('prepare_id', '=', pre), ('state', '=', 'done')])

			product =[x.sale_line_material_id.sale_order_line_id.id for x in data.prepare_lines if x.sale_line_material_id]

			
			if product == []:
				raise openerp.exceptions.Warning("Order Preparation Tidak Memiliki Material Lines")

			order_line = self.pool.get('sale.order.line').search(cr, uid, [('id', 'in', product)])
			data_order_line = self.pool.get('sale.order.line').browse(cr, uid, order_line)

			for y in data_order_line:
				so_material_line = self.pool.get('sale.order.material.line').search(cr, uid, [('sale_order_line_id', '=', [y.id])])
				data_material_line = self.pool.get('sale.order.material.line').browse(cr, uid, so_material_line)

				material_line = []

				for dline in data_material_line:
					op_line = self.pool.get('order.preparation.line').search(cr, uid, [('sale_line_material_id', '=', [dline.id])])
					data_op_line = self.pool.get('order.preparation.line').browse(cr, uid, op_line)
					if data_op_line:
						for dopline in data_op_line:
							material_line.append({
								'name':dopline.product_id.id,
								'desc':dopline.name,
								'qty':dopline.product_qty,
								'product_uom':dopline.product_uom.id
								})
				line.append({
					'no': y.sequence,
					'product_id' : y.product_id.id,
					'product_qty': 0,
					'product_uom': x.product_uom.id,
					'name': y.name,
					'note_lines_material': material_line
					})

			res['note_lines'] = line
			res['poc'] = data.sale_id.client_order_ref
			res['tanggal'] = data.duedate
			res['partner_id'] = data.sale_id.partner_id.id
			res['partner_shipping_id'] = data.sale_id.partner_shipping_id.id
			res['attn'] = data.sale_id.attention.id

		return  {'value': res}

delivery_note()

class delivery_note_line(osv.osv):
	def _get_refunded_item(self,cr,uid,ids,field_name,arg,context={}):

		return super(delivery_note_line,self)._get_refunded_item(cr,uid,ids,field_name,arg,context={})

	_inherit = "delivery.note.line"
	_columns = {
		'no': fields.integer('No'),
		'name': fields.text('Description'),
		'note_id': fields.many2one('delivery.note', 'Delivery Note', required=True, ondelete='cascade'),
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)]),
		'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
		'product_uom': fields.many2one('product.uom', 'UoM'),
		'product_packaging': fields.many2one('product.packaging', 'Packaging'),
		'op_line_id':fields.many2one('order.preparation.line','OP Line',required=True),
		'note_line_return_ids': fields.many2many('stock.move','delivery_note_line_return','delivery_note_line_id',string="Note Line Returns"),
		'refunded_item': fields.function(_get_refunded_item, string='Refunded Item', store=False),
		'state': fields.selection([('torefund', 'To Refund'), ('refunded', 'Refunded'),('donerefund', 'Done Refund')], 'State', readonly=True),
		'note_lines_material': fields.one2many('delivery.note.line.material', 'note_line_id', 'Note Lines Material', readonly=False),
	}

delivery_note_line()


class delivery_note_line_material(osv.osv):
	_name = "delivery.note.line.material"
	_columns = {
		'name' : fields.many2one('product.product',required=True, string="Product"),
		'note_line_id': fields.many2one('delivery.note.line', 'Delivery Note Line', required=True, ondelete='cascade'),
		'qty': fields.float('Qty',required=True),
		'product_uom': fields.many2one('product.uom',required=True, string='UOM'),
		'stock_move_id': fields.many2one('stock.move',required=True, string='Stock Move'),
		'desc': fields.text('Description',required=False),
		'state': fields.related('note_line_id','state', type='many2one', relation='delivery.note.line', string='State'),
	}

delivery_note_line_material()


class stock_picking(osv.osv):
	_name = 'stock.picking'
	_inherit = ["stock.picking","mail.thread"]
	_columns = {
		'is_postpone': fields.boolean('Is Postpone'),
	}

stock_picking()