import openerp.exceptions
import datetime,time
import csv

from openerp import tools
from openerp.tools.translate import _
from osv import osv, fields
import urllib
from cStringIO import StringIO

# import web.http as openerpweb

import openerp.addons.web.http as oeweb


class acount_invoice(osv.osv):
	_inherit = 'account.invoice'
	_columns = {
		'faktur_pajak_no': fields.char('No Faktur Pajak',size=20,required=True),
		'state': fields.selection([
			('draft','Draft'),
			('submited','Submited'), #NEW FLOW TO SUBMIT TO VALIDATE THE INVOICE
			('proforma','Pro-forma'),
			('proforma2','Pro-forma'),
			('open','Open'),
			('paid','Paid'),
			('cancel','Cancelled'),
			],'Status', select=True, readonly=True, track_visibility='onchange',
			help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Invoice. \
			\n* The \'Pro-forma\' when invoice is in Pro-forma status,invoice does not have an invoice number. \
			\n* The \'Open\' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice. \
			\n* The \'Paid\' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
			\n* The \'Cancelled\' status is used when user cancel invoice.'),
	}

	def draft_submited(self,cr,uid,ids,context={}):
		for s in self.browse(cr,uid,ids,context=context):
			if s.state != 'submited':
				raise osv.except_osv(_('Error'),_('Tidak bisa merubah status menjadi draft karena status sudah validate!'))
			
		self.write(cr,uid,ids,{'state':'draft'})

		return True
	def submit_to_validate(self,cr,uid,ids,context={}):
		# res = {}
		res = False
		for d in self.browse(cr,uid,ids,context=context):
			if d.faktur_pajak_no != '000.000-00.00000000':
				num = d.faktur_pajak_no.split('.')
				fp = num[2]
				# search same number
				sameFP = self.search(cr,uid,[('faktur_pajak_no','like',fp),('state','!=','cancel'),('id','!=',d.id)])
				# print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",sameFP
				if len(sameFP) > 0:
					# if exist
					res = False
					browseAllSame = self.browse(cr,uid,sameFP,context=context)
					errSame = [str(bs.id) for bs in browseAllSame]
					print "==============================",errSame
					raise osv.except_osv(_('Error'),_('Nomor Faktur Pajak Sudah dipakai, tidak bisa menggunakan nomor faktur lebih dari 1 kali, Jika Nomor tersebut diganti silahkan cancel terlebih dahulu invoice yang lama\r\n.'+',\r\n'.join(errSame)))

				res=  True
				if res:
					self.write(cr,uid,d.id,{'state':'submited'},context=context)

		
		
		return True
	def efak_invoices_export(self,cr,uid,ids,context={}):
		if context is None:
			context = {}
		try:
			ids = context['active_ids']
		except:
			ids = ids

		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"service/get-invoices-csv&ids="+str(','.join(map(str,ids)))+"&uid="+str(uid)
		for browse in self.browse(cr,uid,ids):
			if browse.partner_id.npwp == '11111111111111111111':
				raise osv.except_osv(_('Error!'),_('NPWP '+browse.partner_id.name+' = '+browse.partner_id.npwp+'\r\n\r\nTolong Update NPWP terlebih dahulu untuk export data. Jika Customer ini tidak mempunyai NPWP atau merupakan Customer Perorangan maka Update NPWP menjadi 00.000.000.0-000.000'))
			elif browse.partner_id.npwp == False:
				raise osv.except_osv(_('Error'),_('NPWP '+browse.partner_id.name+' kosong.\r\n\r\nHarus diisi..!!!'))
		
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.out',
			'params': {
				'redir'	: urlTo
			},
		}
	def efak_invoice_data(self,cr,uid,ids,context={}):

		faktur_data = []
		res = False
		outp = StringIO()
		# sw = csv.writer(outp,delimiter=',',quotechar='"')
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
			# sw.writerows(faktur_data)
		# outp.seek(0)
		# data = outp.read()
		# outp.close()
		return faktur_data

