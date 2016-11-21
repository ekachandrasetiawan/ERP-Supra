import time
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.exceptions


class purchase_order_warehouse(osv.osv):
	_name = "purchase.order.warehouse"
	_inherit = "purchase.order"
	_table = "purchase_order"
	_description = "Purchase Order"

	
purchase_order_warehouse()


class stock_picking(osv.osv):
	_inherit = "stock.picking"
	_name = "stock.picking"


	def send_email(self, cr, uid, ids, subject, partner_id, po_id, partner_name, partial_datas, context=None):
		val = self.browse(cr, uid, ids)[0]
		mail_mail = self.pool.get('mail.mail')
		obj_usr = self.pool.get('res.users')
		obj_partner = self.pool.get('res.partner')

		username = obj_usr.browse(cr, uid, uid)

		count = len(partial_datas) - 1

		data_table = '<table border="1"><tr><th>No</th><th>Product</th><th>Qty</th><th>UOM</th></tr>'
		no = 1
		count_line = 0
		count_partial_data = 0
		for pick in self.browse(cr, uid, ids, context=context):
			count_partial_data = len(pick.move_lines)
			for move in pick.move_lines:
				partial_data = partial_datas.get('move%s'%(move.id), {})
				product_qty = partial_data.get('product_qty',0.0)
				
				
				if product_qty <> 0:

					product = self.pool.get('product.product').browse(cr,uid,partial_data.get('product_id'),context=None)
					uom = self.pool.get('product.uom').browse(cr,uid,partial_data.get('product_uom'),context=None)

					data_table += '<tr><th>'+ str(no) +'</th><th>' + '['+ product.default_code +']' + product.name +'</th><th>'+ str(product_qty) +'</th><th>'+ uom.name +'</th></tr>'
					count_line += 1
					no += 1

		data_table += '</table>'

		status = 'Full Receive'
		if count_partial_data > count:
			status = 'Partail Receive'

		ip_address = '192.168.9.26:10001'
		db = 'LIVE_2014'
		url = 'http://'+ip_address+'/?db='+db+'#id=' +str(val.id)+'&view_type=form&model=purchase.order&menu_id=330&action=394'

		p  = self.pool.get('ir.model.data')
		warehouse_user = p.get_object(cr, uid, 'stock', 'group_stock_user').id
		user_warehouse = self.pool.get('res.groups').browse(cr, uid, warehouse_user)

		body = """\
			<html>
			  <head></head>
			  <body>
				<p>
					Dear %s!<br/><br/>
					%s Telah Receive Product di Purchase Oder No <b> %s </b> Dengan Cara %s <br/>
					<br/>
					<b>Detail :</b><br/>
					%s
					<br/>
					Silahkan klik Link ini untuk melihat Purchase Oder. <a href="%s">View Purchase Order</a>
				</p>
				<br/>
				Best Regards,<br/>
				Administrator ERP
			  </body>
			</html>
			""" % (partner_name, username.name, val.purchase_id.name, status, data_table, url)

		mail_id = mail_mail.create(cr, uid, {
			'model': 'purchase.order',
			'res_id': po_id,
			'subject': subject,
			'body_html': body,
			'auto_delete': True,
			}, context=context)

		mail_mail.send(cr, uid, [mail_id], recipient_ids=[partner_id], context=context)

		return True


	def do_partial(self, cr, uid, ids, partial_datas, context=None):
		pick = self.browse(cr,uid,ids)[0]
		obj_partner = self.pool.get('res.partner')

		if pick.purchase_id:
			po_id = pick.purchase_id.id

			#  Saerch Mail Followers
			cr.execute("SELECT partner_id FROM mail_followers WHERE res_model = 'purchase.order' AND res_id = %s", [po_id])
			id_mail_followers = map(lambda partner_id: partner_id[0], cr.fetchall())

			subject = 'Purchase Order No' + pick.purchase_id.name + ' Proses Receive'

			for l in id_mail_followers:
				usr = obj_partner.browse(cr, uid, [l])[0]
				for s in usr.user_ids:
					if s.email:
						partner_id = s.partner_id.id
						partner_name = s.partner_id.name

						self.send_email(cr, uid, ids, subject, partner_id, po_id, partner_name, partial_datas, context=None)
		
		res = super(stock_picking,self).do_partial(cr,uid,ids,partial_datas,context)
		return res


stock_picking()