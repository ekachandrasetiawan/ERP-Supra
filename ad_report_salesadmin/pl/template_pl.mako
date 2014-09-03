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
						<tr width='100%' height='35px'>
							<td width='15%'>
								<a>TO</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='83%'>
								${o.partner_id.name or '-'}
							</td>
						</tr>
						<tr width='100%' height='35px'>
							<td width='15%'>
								<a>ATTN</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='83%'>
								${o.prepare_id.sale_id.attention.name or '-'}
							</td>
						</tr>
						<tr width='100%' height='35px'>
							<td width='15%'>
								<a>DATE</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='83%'>
								${o.tanggal!='False' and time.strftime('%d %B %Y', time.strptime(o.tanggal,'%Y-%m-%d')) or '-'}
							</td>
						</tr>
						<tr width='100%' height='35px'>
							<td width='15%'>
								<a>REF.</a>
							</td>
							<td width='2%'>
								<a>:</a>
							</td>
							<td width='83%'>
								${o.name or '-'}
							</td>
						</tr>
						<tr width='100%' height='70px'>
							<td colspan='3' align='center'>
								PACKING LIST
							</td>
						</tr>
					</table>
				</td>
			</tr>
		</table>
		<br/>
		<table class='listitem' width='100%'>
			<tr width='100%' height='35px'>
				<td width="12%"><a><b>Item No.</b></a></td>
				<td width="10%"><a><b>Q'tity</b></a></td>
				<td width="50%"><a><b>Description</b></a></td>
				<td width="10%"><a><b>Weight</b></a></td>
				<td width="18%"><a><b>Measurement</b></a></td>
			</tr>
			<tr width='100%'>
				<td width='12%' valign='top' align='center'>
					${line.itemno}
				</td>
				<td width='10%' valign='top' align='left'>
					${line.product_qty} ${line.product_uom.name}
				</td>
				<td width='50%' valign='top' align='left'>
					${line.product_id.name}<br/>
					%if line.name==False:
					
					%else:
					    ${line.name.replace('\n','<br/>')}
					%endif
				</td>
				<td width='10%'>
					${line.weight or '-'}
				</td>
				<td width='18%'>
					${line.measurement or '-'}
				</td>
			</tr>
			<tr width='100%'>
				<td colspan='5'> 
				</td>
			</tr>
			<tr width='100%'>
				<td width='12%'>
				</td>
				<td width='10%'>
				</td>
				<td width='50%'>
					%if o.note==False:
					
					%else:
					    Note : <br/>
					    ${o.note.replace('\n','<br/>')}
					%endif
				</td>
				<td width='10%'>
				</td>
				<td width='18%'>
				</td>
			</tr>
		</table>
		<table class='footer' width='100%'>
			<tr width="100%">
				<td width="22%"></td>
				<td width="50%">
					<b>Purchase Order No : </b>${o.poc or '-'}, ${o.prepare_id.sale_id.date_order!='False' and time.strftime('%d %B %Y', time.strptime(o.prepare_id.sale_id.date_order,'%Y-%m-%d')) or '-'}<br>
					<b>Color Code :</b> ${o.color_code or '-'}</td>
				<td width="28%"></td>
			</tr>
		</table>
	</body>
</html>