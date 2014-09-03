<html>
<head>
<style>
	body{
	font-family:Arial,Helvetica,sans-serif;	
	}
	table{
		font-size:12px;
	}
	div{
		font-size:12px;
	}
	.main{
		min-height:1290px;
		height:1290px;
		margin-top:20px;
		margin-bottom:20px;
		position:relative;
		width:23.7cm;
	}
	#kepada{
	position:absolute;
	margin-top:92px;
	margin-left:105px;
	z-index:11;
	}
	#attn{
	position:absolute;
	margin-top:113px;
	margin-left:105px;
	z-index:11;
	}
	#date{
	position:absolute;
	margin-top:135px;
	margin-left:105px;
	}
	#ref{
	position:absolute;
	margin-top:158px;
	margin-left:105px;
	z-index:11;
	}
	#itemno{
	position:absolute;
	margin-top:275px;
	margin-left:5px;
	z-index:11;
	}
	.item_desc{
	width:250px;
	}
</style>
</head>
<body>
%for o in objects :
<%
	res=get_note_lines(o)
	tot_box=set([x['packing'] for x in res])
%>

<div class="main" style="clear:both">

<div id="kepada"><p>${o.partner_id.name or '-'}</p></div>
<div id="attn"><p>${o.prepare_id.sale_id.attention or '-'}</p></div>
<div id="date"><p>${o.tanggal or '-'}</p></div>
<div id="ref"><p>${o.name or '-'}</p></div>
<div id="itemno">
<table width="100%" border="0">

%for x in o.note_lines :
	<tr width="100%" valign="top">
		<td width="12%"><div class="item_no">${x.itemno or '-'}</div></td>
		<td width="10%"><div class="item_qty">${x.product_qty or '-'} ${x.product_uom.name or '-'}</div></td>
		<td width="50%"><div class="item_desc">${x.packing or '-'} <br/> ${x.product_id.name}<br>${x.name or '-'}</div></td>
		<td width="10%"><div class="item_w">${x.measurement or '-'}</div></td>
		<td width="18%"><div class="item_m">${x.weight or '-'}</div></td>
	</tr>
%endfor
</table>
</div>

<div id="tamplate_table" style="display:;">
<TABLE width=100% border="0" >
	<TR id="header">
		<TD width="100%">
			<table id="header" width=100% border="0">
				<tr>
					<td width="10%">
						<img src="logo_msquare.jpg" width="128px" height="89px" />
					</td>
					<td align="left">
						<font size="3"><b>PT.SUPRABAKTI MANDIRI</b></font>
					</td>
				</tr>
			</table>
		</TD>
	</TR>
	<TR>
		<TD width="100%">
			<table width="100%" border="0">
				<tr>
					<td>
						<table width="50%">
							<tr width="100%">
								<td width="35%"><font size="3">TO
								</td></font>
								<td width="5%"><font size="3">:
								</td></font>
								<td width="60%"><font size="3">........................
								</td></font>
							</tr>
							<tr  width="100%">
								<td width="35%"><font size="3">ATTN
								</td></font>
								<td width="5%"><font size="3">:
								</td></font>
								<td width="60%"><font size="3">........................
								</td></font>
							</tr>
							<tr  width="100%">
								<td width="35%"><font size="3">DATE
								</td></font>
								<td width="5%"><font size="3">:
								</td></font>
								<td width="60%"><font size="3">........................
								</td></font>
							</tr>
							<tr  width="100%">
								<td width="35%"><font size="3">REF.
								</td></font>
								<td width="5%"><font size="3">:
								</td></font>
								<td width="60%"><font size="3">........................
								</td></font>
							</tr>
						</table>
					</td>
				</tr>
			</table>
		</TD>
	</TR>
	<TR>
		<TD width="100%" align="center">
			<font size="6"><b>PACKING LIST</b></font>
		</TD>
	</TR>
	<TR>
		<TD width="100%">
			<table width="100%" border="1">
				<tr width="100%" align="center">
					<td width="12%"><font size="3"><b>Item No.</b></font></td>
					<td width="10%"><font size="3"><b>Q'tity</b></font></td>
					<td width="50%"><font size="3"><b>Description</b></font></td>
					<td width="10%"><font size="3"><b>Weight</b></font></td>
					<td width="18%"><font size="3"><b>Measurement</b></font></td>
				</tr>
				<tr width="100%" height="400">
					<td><font size="3"><b></b></font></td>
					<td><font size="3"><b></b></font></td>
					<td><font size="3"><b></b></font></td>
					<td><font size="3"><b></b></font></td>
					<td><font size="3"><b></b></font></td>
				</tr>
				<tr width="100%" height="25">
					<td><font size="3">Total: item</font></td>
					<td><font size="3"><b></b></font></td>
					<td>TOTAL= ${len(tot_box)} BOX</td>
					<td><font size="3"><b></b></font></td>
					<td><font size="3"><b></b></font></td>
				</tr>
			</table>
		</TD>
	</TR>
	<TR>
		<TD><font><b> </b></font>
		</TD>
	</TR>
	<TR>
		<TD>
			<table width="100%" border="1">
				<tr width="100%">
					<td width="12%"><font size="3"><b></b></font></td>
					<td width="10%"><font size="3"><b></b></font></td>
					<td width="50%"><b>Purchase Order No : </b>${o.poc}, ${o.prepare_id.sale_id.date_order or '-'}<br><b>Stock Code :</b> ${o.color_code or '-'}</td>
					<td width="10%"><font size="3"><b></b></font></td>
					<td width="18%"><font size="3"><b></b></font></td>
				</tr>
			</table>
		</TD>
	</TR>
</TABLE>
</div>
</div>
%endfor
</body>
</html>
