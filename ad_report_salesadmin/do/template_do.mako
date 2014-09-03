<html>
	<head>
	<style>
		table{
			border:1px solid black;
		}
		body {
		font-family:helvetica;
		font-size:12;
		}
		
		.footer td{
		font-size:12;
		}
		
		.header {
		margin-left:0;
		text-align:left;
		}
		
		.header td {
		font-size:12;
		}
		
		.listitem td{
		font-size:12;
		}
		
		.listitem th{
		font-size:12;
		}
		
		a{
			font-size:12;
			opacity:0;
		}
	</style>
	</head>
	<body>
		<table class='header' width='100%' >
			<tr class='kopsurat' height='80px' width='100%'>
				<td></td>
			</tr>
			<tr width='100%'>
				<td width='100%'>
					<table width='100%'>
						<tr width='100%'>
							<td width='65%' align='left'>
								<a>Kepada Yth.<br/>
								Sdr. Kepala Gudang<br/>
								Di tempat<br/>
								<br/>
								<br/>
								Harap disiapkan sejumlah barang dibawah ini :
								</a>
							</td>
							<td width='35%'>
								${o.partner_id.name or '-'}<br/>
								${o.partner_shipping_id.street or '-'}<br/>
								${o.partner_shipping_id.city or '-'} ${o.partner_shipping_id.zip or '-'}<br>
								Telp. ${o.partner_shipping_id.phone or '-'} 
							</td>
						</tr>
					</table>
				</td>
			</tr>
			<tr width='100%'>
				<td width='100%'>
					<table width='100%'>
						<tr width='100%' height='20px'>
							<td width='10%' align='left'>
								 <a>No.DO</a>
							</td>
							<td width='2%' align='center'>
								 <a>:</a>
							</td>
							<td width='21%' align='left'>
								 
							</td>
							<td width='10%' align='left'>
								 <a>No.SC</a>
							</td>
							<td width='2%' align='center'>
								 <a>:</a>
							</td>
							<td width='21%' align='left'>
								 
							</td>
							<td width='10%' align='left'>
								 <a>No.WC</a>
							</td>
							<td width='2%' align='center'>
								 <a>:</a>
							</td>
							<td width='21%' align='left'>
								 
							</td>
						</tr>
						<tr width='100%' height='20px'>
							<td width='10%' align='left'>
								 <a>Tanggal DO</a>
							</td>
							<td width='2%' align='center'>
								 <a>:</a>
							</td>
							<td width='21%' align='left'>
								 
							</td>
							<td width='10%' align='left'>
								 <a>No.PO</a>
							</td>
							<td width='2%' align='center'>
								 <a>:</a>
							</td>
							<td width='21%' align='left'>
								 
							</td>
							<td width='10%' align='left'>
								 <a>No.SPK</a>
							</td>
							<td width='2%' align='center'>
								 <a>:</a>
							</td>
							<td width='21%' align='left'>
								 
							</td>
						</tr>
					</table>
				</td>
			</tr>
		</table>
		<br/>
		<table class='listitem' width='100%'>
			<tr width='100%'>
				<th width='5%'>
					<a>No.<a/>
				</th>
				<th width='23%'>
					<a>Jumlah<a/>
				</th>
				<th width='72%'>
					<a>Nama Barang<a/>
				</th>
			</tr>
			<tr width='100%'>
				<td width='5%' valign='top' align='center'>
					${line.itemno}
				</td>
				<td width='23%' valign='top' align='left'>
					${line.product_qty} ${line.product_uom.name}
				</td>
				<td width='72%'>
					${line.product_id.name}<br/>
					%if line.name==False:
					
					%else:
					    ${line.name.replace('\n','<br/>')}
					%endif
				</td>
			</tr>
			<tr width='100%'>
				<td colspan='3'> 
				</td>
			</tr>
			<tr width='100%'>
				<td width='5%'>
				</td>
				<td width='23%'>
				</td>
				<td width='72%'>
					%if o.note==False:
					
					%else:
					    Note : <br/>
					    ${o.note.replace('\n','<br/>')}
					%endif
				</td>
			</tr>
		</table>
		<table class='footer' width='100%'>
			<tr width='100%' height='35'>
				<th colspan='4' width='60%'>
					<a>a</a>
				</th>
				<th width='40%' colspan='3'>
					<a>DIISI OLEH GUDANG</a>
				</th>
			</tr>
			<tr width='100%' height='35'>
				<td width='20%'>
					<a>Dibuat oleh :</a>
				</td>
				<td width='20%' colspan='2'>
					<a>Dicek oleh :</a>
				</td>
				<td width='20%'>
					<a>Disetujui Oleh,<br/>General Manager,</a>
				</td>
				<td width='18%'>
					<a>No.BPB</a>
				</td>
				<td width='2%'>
					<a>:</a>
				</td>
				<td width='20%'>
				</t>
			</tr>
			<tr width='100%' height='35'>
				<td width='60%' rowspan='2' colspan='4'>
					<a> </a>
				</td>
				<td width='18%'>
					<a>Tgl. Pengambilan</a>
				</td>
				<td width='2%'>
					<a>:</a>
				</td>
				<td width='20%'>
				</td>
			</tr>
			<tr width='100%' height='35'>
				<td width='18%'>
					<a>Diambil Oleh</a>
				</td>
				<td width='2%'>
					<a>:</a>
				</td>
				<td width='20%'>
				</td>
			</tr>
			<tr width='100%' height='35'>
				<td width='100%' colspan='7'>
					<a> </a>
				</td>
			</tr>
			<tr width='100%' height='30%'>
				<td width='30%' colspan='2'>
					<a>No.SJ :</a>
				</td>
				<td width='30%' colspan='2'>
					<a>No.SJ :</a>
				</td>
				<td width='40%' colspan='3'>
					<a> </a>
				</td>
			</tr>
		</table>
	</body>
</html>