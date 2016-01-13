from datetime import datetime
from stock import stock
import math
import time
import webbrowser
import netsvc
import openerp.exceptions
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class quotation_line(osv.osv):	
	_inherit ='sale.order'
	def _count_total(self,cr,uid,ids,fields_name,args,context={}):
		return False

	def _count_tax(self,cr,uid,ids,fields_name,args,context={}):
	 	return False

	def _inv_base_total(self,cr,uid,ids,fields_name,args,context={}):
	 	return False


	_columns = {
		'quotation_no':fields.char(required=True,string='Quotation#'),
		'base_total':fields.function(fnct=_count_total,fnct_inv=_inv_base_total,string='Base Total',type="float"),
		'tax_total':fields.function(fnct=_count_tax, string='Tax'),
		'quotation_state':fields.selection([('draft','Draft'),('confirmed','Confirmed'),('win','Win'),('lost','Lost'),('cancel','Cancel')],string="Quotation State"),
		'cancel_stage':fields.selection([('internal user fault','Internal User Fault'),('external user fault','External User Fault'),('lose','Lose')]),
		'cancel_message':fields.text(string="Cancel Message"),
		'revised_histories':fields.one2many('sale.order.revision.history','sale_order_id')
	}
	_sql_constraints = [
	    ('quotation_no_unique', 'unique(quotation_no)', 'The quotation_no must be unique !')
	    ]
	_defaults={
		
		'quotation_state':'draft'
	}

	def confirm_quotation(self,cr,uid,ids,context={}):
		res = False
		quotation_obj = self.pool.get("sale.order")
		data_sekarang = self.browse(cr,uid,ids,context=context)[0]

		if data_sekarang.quotation_state == 'draft':
			if quotation_obj.write(cr,uid,ids,{'quotation_state':'confirmed'},context=context):
				res = True
		else:
			raise osv.except_osv(_('Warning'),_('Order Cant be confirmed'))

		return res

	def revisi_quotation(self,cr,uid,ids,context={}):
		res = False
		

		return res

	def cancel_quotation(self,cr,uid,ids,context={}):
		res = False
		quotation_obj = self.pool.get("sale.order")
		data_sekarang = self.browse(cr,uid,ids,context=context)[0]

		if data_sekarang.quotation_state == 'draft':
			if quotation_obj.write(cr,uid,ids,{'quotation_state':'cancel'},context=context):
				res = True
		else:
			raise osv.except_osv(_('Warning'),_('Order Cant be Cancel'))

		return res

# <record model='ir.actions.act_window' id="wizard_lost_quotation_form">
# 			<field name="name">wizard.lost.quotation.form</field>
# 			<field name="type">ir.actions.act_window</field>
# 			<field name="res_model">wizard.lost.quotation</field>
# 			<field name="view_type">form</field>
# 			<field name="view_mode">form</field>
# 			<field name="view_id" ref="lost_quotation_wizard"/>
# 			<field name="target">new</field>
# 		</record>


	# def wizard_lost_quotation_form(self,cr,uid,ids,context={}):
	# 	dir={
	# 		"name":"wizard.lost.quotation.form",
	# 		"type":"ir.actions.act_window",
	# 		"res_model":"wizard.lost.quotation",
	# 		"view_type":"form",
	# 		"view_mode":"form",
	# 		"view_id ref=lost_quotation_wizard",
	# 		"target":"new"


	# 	}

	# 	return dir

class sale_order_material_line(osv.osv):


	_name = 'sale.order.material.line'
	_description = 'Sale order material line'
	# _rec_name = 'kelasmana'
	_columns = {
		'sale_order_line_id':fields.many2one('sale.order.line',string="Sale Order Line"),
		'product_id':fields.many2one('product.product',string="Product", required=True, domain=[('sale_ok','==','True')], active=True),
		
		'desc':fields.text(string="Description"),
		'qty':fields.float(string="Qty",required=True),
		'uom':fields.many2one("product.uom",required=True,string="uom"),
		'picking_location':fields.many2one('stock.location',required="True")
		}


	def _get_ho_location(self,cr,uid,ids,context={}):
		test_obj = self.pool.get("sale.order")
		
		# print ["file.sql",],"aaaaaaaaaaaaaa"
		# return False
		
# def default_get(self, cr, uid, picking_location, context=None):
#    		 data = super(sale_order_material_line, self).default_get(cr, uid, picking_location, context=context)
#    		 data['picking_location']=64
#    		 return data

	# 	# product_obj = cr.execute('SELECT "id" FROM "stock_location" where "name" like "HO" ')

	# 	# args=["HO"]
	# 	# sql='SELECT id FROM stock_location WHERE name IN (%s)' 
	# 	# in_p=', '.join(list(map(lambda x: '%s', args)))
	# 	# sql = sql % in_p
	# 	# product_obj = cr.execute(sql, args)
	# 	# print product_obj,"aaaaaaaaaaaaaaaaaaaaaaaaaa"
		
		# args=['%HO%']
		# sql='SELECT id FROM stock_location WHERE name like (%s)' 
		# # name=', '.join(map(lambda x: '%s', args))
		# # sql = sql % name
		# product_obj = cr.execute(sql, args)

		# cari id dari stock.location where name like 'HO'
		seq_id = self.pool.get('stock.location').search(cr, uid, [('name','=','HO')]) 
		print seq_id,"+++++++++++++++++++++++++++++++++++++++++"
		# print "aaaaaaaaaaaaaaaaaaaaaaaaaa",product_obj
		return seq_id
	_defaults={
		
		'picking_location':_get_ho_location
	}


class quotation(osv.osv):	
	_inherit ='sale.order.line'
	_columns = {
		'material_lines':fields.one2many('sale.order.material.line','sale_order_line_id')		
	}
	def loadBomLine(self,cr,uid,product_id,product_uom_qty,product_uom):
		res = {}
		res = {
			
			'product_id':product_id.product_id.id,
			'uom':product_id.product_uom.id,
			'qty':product_uom_qty*product_id.product_qty,
			
		}
		return res

	def onchange_product_quotation(self,cr,uid,ids,product_id,product_uom_qty,product_uom):
		res={}
		if product_id:
			product= self.pool.get('product.product').browse(cr,uid,product_id,{})
			
			if product.bom_ids:	
				bom_line_set = self.pool.get('mrp.bom').browse(cr,uid,product.bom_ids[0].id)
				res['value'] = {
			'material_lines':[(0,0,self.loadBomLine(cr,uid,product_id,product_uom_qty,product_uom)) for product_id in bom_line_set.bom_lines]
		}
			else:
				print "tidak ada"
				res['value'] = {
			'material_lines': [
				(0,0,{'product_id':product_id,'qty':product_uom_qty,'uom':product_uom}),
			]
		}
		print res
		return res

	def onchange_product_quotation_qty(self,cr,uid,ids,product_id,product_uom_qty,product_uom):
		res={}
		if product_uom_qty == False:
			product_uom_qty=0
		if product_id:
			product= self.pool.get('product.product').browse(cr,uid,product_id,{})
			
			if product.bom_ids:	
				bom_line_set = self.pool.get('mrp.bom').browse(cr,uid,product.bom_ids[0].id)
				res['value'] = {
			'material_lines':[(0,0,self.loadBomLine(cr,uid,product_id,product_uom_qty,product_uom)) for product_id in bom_line_set.bom_lines]
		}
			else:
				print "tidak ada"
				res['value'] = {
			'material_lines': [
				(0,0,{'product_id':product_id,'qty':product_uom_qty,'uom':product_uom}),
			]
		}
		print res
		return res

	