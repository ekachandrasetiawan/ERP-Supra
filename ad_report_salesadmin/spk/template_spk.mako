<html>
	<head>
	<style>
		table{
			border:1px solid black;
		}
		table td{
			border:1px solid black;
		}
		table th{
			border:1px solid black;
		}
		table tr{
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
			opacity:1;
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
						<tr width='100%' height='35px'>
							<td width='60%' rowspan='2' colspan='3' align='left'>
								<a>Kepada Yth.<br/>
								Sdr. Koordinator<br/>
								di tempat<br/>
								</a>
							</td>
							<td width='6%'>
								<a>Nomor SPK</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='27%'>
								${o.name or '-'}
							</td>
						</tr>
						<tr width='100%' height='35px'>
							<td width='6%'>
								<a>Tanggal SPK</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='27%'>
								${o.date!='False' and time.strftime('%d %B %Y', time.strptime(o.date,'%Y-%m-%d')) or '-'}
							</td>
						</tr>
						<tr width='100%' height='35px'>
							<td width='60%' colspan='3' align='left'>
								<a><u><b>SURAT PERINTAH KERJA</b></u>
								</a>
							</td>
							<td width='6%'>
								<a>No. Kontrak</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='27%'>
								${o.kontrak or '-'}
							</td>
						</tr>
						<tr width='100%' height='35px'>
							<td width='20%'>
								<a>Untuk Customer</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='38%'>
								${o.partner_id.name or '-'}
							</td>
							<td width='6%'>
								<a>Tgl. Kontrak</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='27%'>
								${o.kontrakdate!='False' and time.strftime('%d %B %Y', time.strptime(o.kontrakdate,'%Y-%m-%d')) or '-'}
							</td>
						</tr>
						<tr width='100%' height='35px'>
							<td width='20%'>
								<a>Dikerjakan Di</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='38%'>
								${o.workshop or '-'}
							</td>
							<td width='6%'>
								<a>Delivery Time</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='27%'>
								${o.delivery_date!='False' and time.strftime('%d %B %Y', time.strptime(o.delivery_date,'%Y-%m-%d')) or '-'}
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
					<a>Uraian Pekerjaan<a/>
				</th>
			</tr>
			<tr width='100%'>
				<td width='5%' valign='top' align='center'>
					
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
				<td width='33%' align='center'>
					<a>Dibuat oleh,</a>
				</td>
				<td width='33%' align='center'>
					<a>Dicek oleh,</a>
				</td>
				<td width='33%' align='center'>
					<a>Disetujui oleh,<br/>General Manager</a>
				</td>
			</tr>
			<tr width='100%' height='105'>
				<td width='33%' align='center' valign='bottom'>
					${o.creator.name or '-'}
				</td>
				<td width='33%' align='center' valign='bottom'>
					${o.checker.name or '-'}
				</td>
				<td width='33%' align='center' valign='bottom'>
					${o.approver.name or '-'}
				</td>
			</tr>
			<tr width='100%' height='140'>
				<td width='100%' colspan='3' align='center'>
					<a>a</a>
				</td>
			</tr>
		</table>
	</body>
</html>