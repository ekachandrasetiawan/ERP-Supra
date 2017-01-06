import time
from report import report_sxw
from osv import osv
import pooler

class ReportPB(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(ReportPB, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'sum' : sum,
			'get_lines':self.get_lines,
			'proyek':self.proyek,
			})

	def proyek(self,obj):
		res = ''
		partner_id = False
		detail_pb_ids= obj.detail_pb_ids
		for x in detail_pb_ids:
			if x.sale_line_ids:

				if partner_id != x.sale_line_ids.order_id.partner_id.id:
					res += x.sale_line_ids.order_id.partner_id.name+','
				partner_id = x.sale_line_ids.order_id.partner_id.id

		res = res[:-1]

		return res

	def get_lines(self,obj):
		detail_pb_ids= obj.detail_pb_ids
		res=[]
		arrLine={}
		i=1
		# customer= ''
		for x in detail_pb_ids:

			if x.variants.id==False:
				name = x.name.name
			else:
				name = x.variants.name

			so_name = False
			if x.sale_line_ids.id:
				so_name = x.sale_line_ids.order_id.name

			part_no = x.part_no
			if x.detail_pb_id.proc_type=='sales':
				part_no = x.name.default_code


			keterangan =  x.keterangan
			if x.keterangan and len(x.keterangan)>64:
				name += "\r\n\r\n"+x.keterangan
				keterangan = ""

			arrLine.update({'no':i,'name':name,'desc':x.desc,'satuan':x.satuan,'part_no':part_no,'jumlah_diminta':x.jumlah_diminta,'stok':x.stok,'keterangan':keterangan,'so_name':so_name})
			res.append(arrLine)
			arrLine={}
			i+=1
		return res

report_sxw.report_sxw('report.print.pb', 'pembelian.barang', 'addons/sbm_purchase/report/report_pb.rml', parser = ReportPB, header = False)