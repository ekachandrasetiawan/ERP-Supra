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
	margin-top:130px;
	margin-left:15px;
	z-index:11;
	}
	#nosur{
	position:absolute;
	margin-top:162px;
	margin-left:585px;
	z-index:11;
	}
	#jumlah{
	position:absolute;
	margin-top:237px;
	margin-left:55px;
	}
	#desc{
	position:absolute;
	margin-top:237px;
	margin-left:218px;
	z-index:11;
	}
	#unitp{
	position:absolute;
	margin-top:237px;
	margin-left:567px;
	z-index:11;
	}
	#extp{
	position:absolute;
	margin-top:237px;
	margin-left:725px;
	z-index:11;
	}
	#tgl{
	position:absolute;
	margin-top:182px;
	margin-left:585px;
	z-index:11;
	}
	#jum1{
	position:absolute;
	margin-top:585px;
	margin-left:725px;
	z-index:11;
	}
	#jum2{
	position:absolute;
	margin-top:610px;
	margin-left:725px;
	z-index:11;
	}
	#jum3{
	position:absolute;
	margin-top:634px;
	margin-left:725px;
	z-index:11;
	}
	#jum4{
	position:absolute;
	margin-top:660px;
	margin-left:725px;
	z-index:11;
	}
	#jum5{
	position:absolute;
	margin-top:685px;
	margin-left:725px;
	z-index:11;
	}
	#jum6{
	position:absolute;
	margin-top:709px;
	margin-left:725px;
	z-index:11;
	}
	#terbilang{
	position:absolute;
	margin-top:760px;
	margin-left:110px;
	z-index:11;
	}
	#jatem{
	position:absolute;
	margin-top:802px;
	margin-left:210px;
	z-index:11;
	}
	#transferke{
	position:absolute;
	margin-top:827px;
	margin-left:290px;
	z-index:11;
	}
</style>
</head>
<body>
%for o in objects :
<div class="main" style="clear:both;">
<div id="kepada">${o.partner_id.name}<br>${o.partner_id.street}</div>
<div id="nosur">${o.number}</div>
<div id="jumlah">
%for x in o.invoice_line :
	${x.quantity} ${x.uos_id.name}<br>
%endfor
</div>
<div id="tgl">${o.date_invoice}</div>
<div id="jum1">${o.currency_id.name} jum1</div>
<div id="jum2">${o.currency_id.name} jum2</div>
<div id="jum3">${o.currency_id.name} jum3</div>
<div id="jum4">${o.currency_id.name} ${o.amount_untaxed}</div>
<div id="jum5">${o.currency_id.name} ${o.amount_tax}</div>
<div id="jum6">${o.currency_id.name} ${o.amount_total}</div>
<%
	terbilang=convert(o.amount_total,o.currency_id.id)
%>
<div id="terbilang">${terbilang}</div>
<div id="jatem">${o.date_due}</div>
<div id="transferke">transferke</div>

<div id="desc">
%for x in o.invoice_line :
	${x.product_id.name}<br>
%endfor
</div>

<div id="unitp">
%for x in o.invoice_line :
	${x.price_unit}<br>
%endfor
</div>
<div id="extp"></div>
<TABLE width=100% border="0" style="display:;">
	<TR>
		<TD width=100%>
			<table id="header" width=100% border="0">
				<tr>
					<td width="20%">
						<img src="logo_msquare.jpg" width="128px" height="89px" />
					</td>
					<td align="center">
						<font size="6"><b>PT.SUPRABAKTI MANDIRI</b></font><br>
						<a><font size="2">Jl.Danau SUnter Utara Blok A No.9,Jakarta Utara - INDONESIA</font></a><br>
<a><font size="1">Telp. : 62 21 658 33666 (Hunting) Fax : 62 21 658 31666 www.beltcare.com</font></a>
					</td>
					<td width="25%" valign="top">
						<font size="3"> </font>
					</td>
				</tr>
			</table>
		</TD>
	</TR>
	<TR>
		<TD width="100%">
			<table width="100%" border="0">
				<tr width="100%">
					<td rowspan=3 colspan=3 width="60%" valign="top"><font size="3">Kepada Yth : </font></td>
					<td colspan=2 width="40%" align="center"><font size="5"><b><i><u>INVOICE</u></i></b></font>
					<font size="5"><br><b><i>FAKTUR</i></b></font>
					<br><font size="3">NO. </font>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
					<br><font size="3">TGL. </font>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
					</td>
				</tr>
			</table>
		</TD>
	</TR>
	<TR>
		<TD width="100%">
			<table width="100%" border="1">
				<tr width="100%" align="center">
					<td width="5%">NO.</td>
					<td width="18%">QUANTITY</td>
					<td width="41%">DESCRIPTION</td>
					<td width="18%">UNIT PRICE</td>
					<td width="18%">EXT. PRICE</td>
				</tr>
				<tr width="100%" height="350">
					<td width="5%"><font size="3"><b> </b></font></td>
					<td width="18%"><font size="3"><b> </b></font></td>
					<td width="41%"><font size="3"><b> </b></font></td>
					<td width="18%"><font size="3"><b> </b></font></td>
					<td width="18%"><font size="3"><b> </b></font></td>
				</tr>
				<tr width="100%">
					<td colspan="4"><font size="3">Jumlah Harga Jual/Dasar Pengenaan Pajak</font></td>
					<td ><font size="3"><b> </b></font></td>
				</tr>
				<tr width="100%">
					<td colspan="4"><font size="3">Dikurangi potongan harga</font></td>
					<td ><font size="3"><b> </b></font></td>
				</tr>
				<tr width="100%">
					<td colspan="4"><font size="3">Dikurangi uang muka yang telah diterima</font></td>
					<td ><font size="3"><b> </b></font></td>
				</tr>
				<tr width="100%">
					<td colspan="4"><font size="3">Total Sebelum PPN 10%</font></td>
					<td ><font size="3"><b> </b></font></td>
				</tr>
				<tr width="100%">
					<td colspan="4"><font size="3">PPN 10%</font></td>
					<td ><font size="3"><b> </b></font></td>
				</tr>
				<tr width="100%">
					<td colspan="4"><font size="3">Total Setelah PPN 10%</font></td>
					<td ><font size="3"><b> </b></font></td>
				</tr>
			</table>
		</TD>
	</TR>
	<TR>
		<TD width="100%">
			<table width="100%" border="0">
				<tr width="100%">
					<td>Terbilang : 
<br>........................................................................................................................................................
<br>........................................................................................................................................................
					</td>
				</tr>
				<tr width="100%">
					<td>Jatuh Tempo Pembayaran : 
					</td>
				</tr>
				<tr width="100%">
					<td>Pembayaran dapat ditransfer melalui : 
					</td>
				</tr>
			</table>
		</TD>
	</TR>
</TABLE>
</div>
%endfor
</body>
</html>
