import time

from openerp.osv import fields, osv
from openerp.tools.translate import _


class SaleOrderLine(osv.osv):
	_inherit = 'sale.order.line'
	_columns = {
		'item_pb': fields.many2many('sale.order.line.from.requisition.lines', 'so_item_rel', 'line_id', 'permintaan_id', 'Item Detail PB'),
	}


SaleOrderLine()
		

class sale_order_line_from_requisition_lines(osv.osv_memory):
	_name = "sale.order.line.from.requisition.lines"
	_description = "Entries by SO Lines from Requisition Lines"
	_columns = {
		'line_ids': fields.many2many('sale.order.line', 'so_item_rel', 'permintaan_id', 'line_id', 'Sale Order Line'),
	}

	def populate_order_lines(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		detail_pb = self.pool.get("detail.pb")

		if context is None:
			context={}
		pb_id=context.get('active_id')

		for line in val.line_ids:
			detail_pb.create(cr,uid, {
				'name':line.product_id.id,
				'jumlah_diminta':line.product_uom_qty,
				'qty_available':line.product_uom_qty,
				'satuan':line.product_uom.id,
				'detail_pb_id':pb_id,
			},context=context)


			print '================PB ID',pb_id

			
		return {'type': 'ir.actions.act_window_close'}

sale_order_line_from_requisition_lines()
