<html>
<body>
%for o in objects :
	
<TABLE width=100% border="0" style="display:;">
	<TR>
		<TD width=100%>
			<font size=5><b>PURCHASE ORDER</b></font>
		</TD>
	</TR>
	<TR>
		<TD width=100%>
			<table id="header" width=100% border="0">
				<tr>
					<td width="10%">
						<font size='3'>No.</font><br>
					</td>
					<td width="60%">
						<font size='3'>${o.name}</font><br>
					</td>
					<td width="30%" valign="top">
						<font size="3">Form No.SBM-F-adm-07a/00</font><br>
					</td>
				</tr>
				<tr>
					<td width="10%">
						<font size='3'>To :</font>
					</td>
					<td width="60%">
						<font size='3'>${o.partner_id.name}</font>
					</td>
					<td width="30%" valign="top">
						<font size="3">Date:${o.date_order}</font>
					</td>
				</tr>
				<tr>
					<td width="10%">
						<font size='3'>Attn.</font>
					</td>
					<td width="60%">
						<font size='3'>Linda</font>
					</td>
					<td width="30%" valign="top">
						<font size="3">Fax : </font>
					</td>
				</tr>
				<tr>
					<td colspan=3>
						<font size='3'>Gentlement, we are pleased to confirm thefollowing order :</font>
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
					<td width="18%">QTY</td>
					<td width="41%">DESCRIPTION</td>
					<td width="18%">UNIT PRICE</td>
					<td width="18%">EXT. PRICE</td>
				</tr>
				%for x in o.order_line:
				<tr width="100%">
					<td width="5%"><font size="3"><b></b></font></td>
					<td width="18%"><font size="3">${x.product_qty} ${x.product_uom.name}</font></td>
					<td width="41%"><font size="3">${x.product_id.name}</font></td>
					<td width="18%"><font size="3">${x.price_unit}</font></td>
					<td width="18%"><font size="3">${x.price_subtotal}</font></td>
				</tr>
				%endfor
				<tr width="100%">
					<td colspan="3"><font size="3"><b>TOTAL PRICE ${o.port.name} PORT</b></font></td>
					<td ><font size="3"><b>USD</b></font></td>
					<td ><font size="3"><b>${o.amount_total}</b></font></td>
				</tr>
			</table>
		</TD>
	</TR>
	<TR>
		<TD width="100%">
			<table width="100%" border="0">
				<tr width="100%" valign="top">
					<td width="5%"><font size="3"><b></b></font></td>
					<td width="15%"><font size="3">Your ref :</font></td>
					<td width="80%"><font size="3">${o.yourref.replace("\n", "<br />")}</font></td>
				</tr>
				<tr width="100%" valign="top">
					<td width="5%"><font size="3"><b></b></font></td>
					<td width="15%"><font size="3">Note :</font></td>
					<td width="80%"><font size="3">${o.note.replace("\n", "<br />")}</font></td>
				</tr>
				<tr width="100%" valign="top">
					<td width="5%"><font size="3"><b></b></font></td>
					<td width="15%"><font size="3">Payment term :</font></td>
					<td width="80%"><font size="3"></font></td>
				</tr>
				<tr width="100%" valign="top">
					<td width="5%"><font size="3"><b></b></font></td>
					<td width="15%"><font size="3">Shipment to :</font></td>
					<td width="80%"><font size="3">${o.port.name} port<br> ${o.location_id.partner_id.name}<br>${o.location_id.partner_id.street}<br>${o.location_id.partner_id.city} - ${o.location_id.partner_id.zip} - ${o.location_id.partner_id.country_id.name}<br>Tel : ${o.location_id.partner_id.phone}; Fax : ${o.location_id.partner_id.fax}</font></td>
				</tr>
			</table>
		</TD>
	</TR>
	<TR>
		<TD width="80%">
			<font size="3">After shipment, please fax me the copy of Invoice, Packing List, and ${o.other} and mail the original documents via DHL.<br>Kindly acknowledge the receipt of this order and send us Proforma Invoice and estimation of delivery</font>
		</TD>
	</TR>
</TABLE>
%endfor
</body>
</html>
