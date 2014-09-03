<html>
<body>
<style>
	body{
	font-family:Arial,Helvetica,sans-serif;	
	}
	
	#kepada{
	position:absolute;
	margin-top:130px;
	margin-left:15px;
	z-index:11;
	}
	#nosur{
	position:absolute;
	margin-top:142px;
	margin-left:525px;
	z-index:11;
	}
	#jumlah{
	position:absolute;
	margin-top:250px;
	margin-left:100px;
	}
	#jenis{
	position:absolute;
	margin-top:250px;
	margin-left:240px;
	z-index:11;
	}
	#partno{
	position:absolute;
	margin-top:250px;
	margin-left:700px;
	z-index:11;
	}
	#ekspedisi{
	position:absolute;
	margin-top:420px;
	margin-left:540px;
	z-index:11;
	}
	#nospb{
	position:absolute;
	margin-top:187px;
	margin-left:475px;
	z-index:11;
	}
	#tgl{
	position:absolute;
	margin-top:187px;
	margin-left:725px;
	z-index:11;
	}
	#tglspb{
	position:absolute;
	margin-top:162px;
	margin-left:685px;
	z-index:11;
	}
</style>
%for o in objects :
	
<div id="kepada"><font size="3">ADSOFT</font></div>
<div id="nosur"><font size="3">12/ADS/CIPUTAT/XII</font></div>
<div id="jumlah"><font size="3">15</font></div>
<div id="tgl"><font size="3">tgl</font></div>
<div id="nospb"><font size="3">nopo</font></div>
<div id="tglspb"><font size="3">tgldn</font></div>

<div id="jenis"><font size="3">
%for x in o.order_line :
	${x.product_id.name}<br>
%endfor
</font></div>

<div id="partno"><font size="3">px123</font></div>
<div id="ekspedisi"><font size="3">Kapal Selam</font></div>
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
			<table width="100%" border="1">
				<tr width="100%">
					<td rowspan=3 colspan=3 width="50%" valign="top"><font size="3">Kepada :</font></td>
					<td colspan=2 width="50%" align="center"><font size="5"><b>SURAT PENGANTAR BARANG</b></font>
					<br><font size="4">No. </font>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
					</td>
				</tr>
				<tr width="50%"><td colspan=2><font size="3">Tanggal Surat Pengantar Barang : </font></td></tr>
				<tr width="50%"><td colspan=2><font size="3">No.PB : &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;Tanggal :</font></td></tr>
				<tr width="100%">
					<td align="center" width="5%"><font size="3"><b>NO</b></font></td>
					<td align="center" width="20%"><font size="3"><b>JUMLAH</b></font></td>
					<td align="center" colspan=2 width="50%"><font size="3"><b>JENIS BARANG</b></font></td>
					<td align="center" width="20%"><font size="3"><b>PART NO.</b></font></td>
				</tr>
		
				<tr width="100%" height="150">
					<td align="center" width="5%"><font size="3"><b> </b></font></td>
					<td align="center" width="20%"><font size="3"><b> </b></font></td>
					<td align="center" colspan=2 width="50%"><font size="3"><b> </b></font></td>
					<td align="center" width="20%"><font size="3"><b> </b></font></td>
				</tr>
		
				<tr width="100%">
					<td colspan=5>
						<table border="1" width="100%">
							<tr>
								<td colspan=3 width="60%"><font size="3">CATATAN, HARAP DIBERI TANDA DIDALAM</font><br><font size="2">Barang-barang diatas telah diterima dalamkeadaan kondisi baru/baik dan jumlah yang benar<br>Komentar lainnya : </font></td>
								<td colspan=2 width="40%" valign="top"><font size="2">Ekspedisi : </font></td>
							</tr>
							<tr height="100" valign="top" align="center">
								<td width="20%"><font size="3">Yang Menerima</font></td>
								<td width="20%"><font size="3">Packing</font></td>
								<td width="20%"><font size="3">Pengirim</font></td>
								<td width="20%"><font size="3">Kepala Gudang</font></td>
								<td width="20%"><font size="3">Mengetahui</font></td>
							</tr>			
						</table>
					</td>
				</tr>
			</table>
		</TD>
	</TR>
</TABLE>
%endfor
</body>
</html>
