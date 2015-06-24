import openerp.exceptions
import datetime,time
import csv

from openerp import tools
from openerp.tools.translate import _
from osv import osv, fields

from cStringIO import StringIO

# import web.http as openerpweb

import openerp.addons.web.http as oeweb


class acount_invoice(osv.osv):
	_inherit = 'account.invoice'
	
	def efak_invoices_export(self,cr,uid,ids,context={}):
		res = {
			'type':'ir.actions.act_url',
			'url': '/my',
			'target':'new'
		}
		return res
	def efak_invoice_data(self,cr,uid,ids,context={}):

		faktur_data = []
		res = False
		outp = StringIO()
		sw = csv.writer(outp,delimiter=',',quotechar='"')
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency') 
		for inv in self.browse(cr,uid,ids,context):
			cur = inv.currency_id

			KD_JENIS_TRANSAKSI = '01'
			FG_PENGGANTI = '0'
			NOMOR_FAKTUR = inv.kwitansi
			date_invoice = datetime.datetime.strptime(inv.date_invoice,'%Y-%m-%d')
			MASA_PAJAK = date_invoice.month
			TAHUN_PAJAK = date_invoice.year
			TANGGAL_FAKTUR = datetime.datetime.strftime(date_invoice,'%d/%m/%Y')
			NPWP = inv.partner_id.parent_id.npwp or inv.partner_id.npwp
			NAMA = inv.partner_id.parent_id.name or inv.partner_id.name
			ALAMAT_LENGKAP = inv.partner_id.street
			JUMLAH_DPP = inv.amount_total
			JUMLAH_PPN = inv.amount_tax
			JUMLAH_PPNBM = 0
			ID_KETERANGAN_TAMBAHAN = ""
			FG_UANG_MUKA = "0"
			UANG_MUKA_DPP = "0"
			UANG_MUKA_PPN = "0"
			UANG_MUKA_PPNBM = "0"
			REFERENSI = inv.comment

			faktur_data.append(
				[
					'FK',
					KD_JENIS_TRANSAKSI,
					FG_PENGGANTI,
					NOMOR_FAKTUR,
					MASA_PAJAK,
					TAHUN_PAJAK,
					TANGGAL_FAKTUR,
					NPWP,
					NAMA,
					ALAMAT_LENGKAP,
					JUMLAH_DPP,
					JUMLAH_PPN,
					JUMLAH_PPNBM,
					ID_KETERANGAN_TAMBAHAN,
					FG_UANG_MUKA,
					UANG_MUKA_DPP,
					UANG_MUKA_PPN,
					UANG_MUKA_PPNBM,
					REFERENSI
				]
			)
			# CUSTOMER / SUPLIER DATA
			partner = inv.partner_id.parent_id or inv.partner_id

			faktur_data.append([
				"FAPR", 
				"PT. SUPRABAKRI MANDIRI",
				"Jl. Danau Sunter Utara Blok A No. 9 Tanjung Priok - Jakarta Utara",
				"","","","",""
			])

			# LOOP EACH INVOICE ITEM
			
			for item in inv.invoice_line:
				# print item.price_subtotal
				
				ppn_total = 0
				tax_compute =  tax_obj.compute_all(cr, uid, item.invoice_line_tax_id, (item.price_unit* (1-(item.discount or 0.0)/100.0)), item.quantity, item.product_id, inv.partner_id)['taxes'][0]
				# print tax_compute
				faktur_data.append(
					[
						"OF",item.product_id.default_code,item.name,item.price_unit,item.quantity,item.price_subtotal,
						inv.total_discount,item.price_subtotal,
						tax_compute['amount'],
						"0","0.0"
					]
				)

			# print faktur_data
			# sw.writerow(['FK',KD_JENIS_TRANSAKSI,FG_PENGGANTI,NOMOR_FAKTUR,MASA_PAJAK,TAHUN_PAJAK,TANGGAL_FAKTUR,NPWP,NAMA,ALAMAT_LENGKAP,JUMLAH_DPP,JUMLAH_PPN,JUMLAH_PPNBM,ID_KETERANGAN_TAMBAHAN,FG_UANG_MUKA,UANG_MUKA_DPP,UANG_MUKA_PPN,UANG_MUKA_PPNBM,REFERENSI])
			sw.writerows(faktur_data)
		# print outp.getvalue()
		outp.seek(0)
		data = outp.read()
		outp.close()
		return data

