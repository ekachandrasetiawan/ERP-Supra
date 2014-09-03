<html>
<body>
<style>
	body{
	font-family:Arial,Helvetica,sans-serif;	
	}
	
	#no{
	position:absolute;
	margin-top:67px;
	margin-left:700px;
	z-index:11;
	}
	#diterima{
	position:absolute;
	margin-top:110px;
	margin-left:155px;
	z-index:11;
	}
	#sebanyak{
	position:absolute;
	margin-top:150px;
	margin-left:155px;
	}
	#pembayaran{
	position:absolute;
	margin-top:195px;
	margin-left:155px;
	z-index:11;
	}
	#jumlah{
	position:absolute;
	margin-top:265px;
	margin-left:145px;
	z-index:11;
	}
	#tanggal{
	position:absolute;
	margin-top:300px;
	margin-left:700px;
	z-index:11;
	}
	#ttd{
	position:absolute;
	margin-top:187px;
	margin-left:475px;
	z-index:11;
	}
</style>
%for o in objects :
	
<div id="no"><font size="3">No</font></div>
<div id="diterima"><font size="3">diterima</font></div>
<div id="sebanyak"><font size="3">sebanyak</font></div>
<div id="pembayaran"><font size="3">pembayaran</font></div>
<div id="jumlah"><font size="3">jumlah</font></div>
<div id="tanggal"><font size="3">tanggal</font></div>
<div id="ttd"><font size="3">ttd</font></div>

<TABLE width=100% border="0" style="display:;">
	<TR>
		<TD width=100%>
			<table id="header" width=100% border="0">
				<tr>
					<td width="20%">
						<img src="logo_msquare.jpg" width="128px" height="89px" />
					</td>
					<td align="left">
						<font size="6"><b>PT.SUPRABAKTI MANDIRI</b></font><br>
						<a><font size="2">Jl.Danau SUnter Utara Blok A No.9,Jakarta Utara - INDONESIA</font></a><br>
<a><font size="1">Telp. : 62 21 658 33666 (Hunting) Fax : 62 21 658 31666 www.beltcare.com</font></a>
					</td>
					<td width="25%" valign="bottom">
						<font size="3">No. .............................................</font>
					</td>
				</tr>
			</table>
		</TD>
	</TR>
	<TR>
		<TD width="100%">
			<TABLE width=100% border="0">
				<TR>
					<TD width=100%>
						<table id="isi" width=100% border="1">
							<tr>
								<td width="18%">
									<font size="3"><u>Sudah Terima dari</u><br><i>Received from</i></font>
								</td>
								<td width="1%" valign="top">
									<font size="3">:</font>
								</td>
								<td width="81%">
									<a></a>
								</td>
							</tr>
							<tr>
								<td width="18%">
									<font size="3"><u>Banyaknya Uang</u><br><i>The Sum of</i></font>
								</td>
								<td width="1%" valign="top">
									<font size="3">:</font>
								</td>
								<td width="81%">
									<a></a>
								</td>
							</tr>
							<tr height="60">
								<td width="18%" valign="top">
									<font size="3"><u>Untuk Pembayaran</u><br><i>Being Payment Of</i></font>
								</td>
								<td width="1%" valign="top">
									<font size="3">:</font>
								</td>
								<td width="81%">
									<a></a>
								</td>
							</tr>
							<tr>
								<td width="18%" colspan="3" bgcolor="grey" height="35">
									<font size="3"><b></b></font><br>
								</td>
							</tr>
							<tr>
								<td colspan="3">
									<table width="100%" border="1">
										<tr height="150" valign="top">
											<td width="60%"><font size="2"><b>Catatan : </b></font></td>
											<td width="40%" align="center"><font size="2">...................... , ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,<br><br><br><br><br><br><br>(&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
			&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
			&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;)</font></td>
										</tr>
									</table>
								</td>
							</tr>
						</table>
					</TD>
				</TR>
			</TABLE>
		</TD>
	</TR>
</TABLE>
%endfor
</body>
</html>
