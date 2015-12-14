from osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime

class account_invoice(osv.osv):
	PERIODS = [('01','01 - January'),('02','02 - February'),('03','03 - March'),('04','04 - April'),('05','01 - Mey'),('06','06 - June'),('07','07 - July'),('08','08 - August'),('09','09 - September'),('10','10 - October'),('11','11 - November'),('12','12 - December')]
	def _get_month(self,date,date_format='%Y-%m-%d'):
		date_obj = datetime.strptime(date,date_format)
		return date_obj.strftime('%m')
		

	def onchange_date_invoice(self,cr,uid,ids,date):
		return {
			'value':{
				'tax_period':self._get_month(date)
			}
		}

	_inherit = 'account.invoice'
	_columns = {
		'tax_period': fields.selection(PERIODS,string="Tax Period"),
	}


	def action_to_tax_replacement(self,cr,uid,ids,context={}):
		res = False
		invs = self.browse(cr,uid,ids,context=context)
		newids = []
		for inv in invs:
			picking_ids = [(6,0, [pick.id]) for pick in inv.picking_ids]
			# res = [(0,0,self._im_line_preparation(cr,uid,line)) for line in request.lines if (line.qty-line.processed_item_qty) > 0]
			invoice_lines =  [(0, 0, self.pool.get('account.invoice.line').copy_data(cr,uid,line.id,{'invoice_id':False},context=context)) for line in inv.invoice_line]

			

			# newid = self.copy(cr,uid,inv.id,default=default,context=context)
			# override copy new
			copy_new = self.copy_data(cr, uid, inv.id, context=context, default={'invoice_line':invoice_lines,'picking_ids':picking_ids})
			
			newid = self.create(cr,uid,copy_new,context=context)
			
			# raise osv.except_osv(_('Error!'),_('Tes'))
			newids = [newid]
			newInv = self.browse(cr,uid,newid,context=context)
			
			fp_no = newInv.faktur_pajak_no[0:2]+'1.'+newInv.faktur_pajak_no[4:20]

			
			# self.write(cr,uid,newid,{'faktur_pajak_no':fp_no})
			# canceling old invoice
			self.write(cr,uid,[inv.id],{'state':'cancel'})
			# new faktur  number
			self.write(cr,uid,newid,{'faktur_pajak_no':fp_no,'tax_invoice_origin_id':inv.id,'tax_period':self._get_month(inv.date_invoice)})

		mod_obj = self.pool.get('ir.model.data')
		res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
		res_id = res and res[1] or False,

		return {
			'name': _('Customer Invoices'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [res_id],
			'res_model': 'account.invoice',
			'context': "{'type':'out_invoice'}",
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': newids and newids[0] or False,
		}