<html>
<head>
<style>
div{
	min-height:1290px;
	height:1290px;
	margin-top:20px;
	margin-bottom:20px;
	position:relative;
	}
table
	{
	font-size:14px;
	float:left;
	border-collapse:collapse;
	}
table.main tr td { padding: 5px;}
.main
	{
	width:23.7cm;
	margin:0 auto;
	}
.main th
	{
	border:1px solid #000;
	}
.main td
	{
	border:1px solid #000;
	}
	
.headpage
	{
		width:100%;
	}
.logo
	{
		float:right;
		width:20%;
	}
.fontcompany{
	font-size:16px;
	
}
.address1
	{
		float:left;
		width:80%;
		text-align:left;
	}
.alignCenter{
	text-align: center;
}
.alignLeft{
	text-align: left;
}
.alignRight{
	text-align: right;
}

.alignTop{
	vertical-align: top;
}
</style>
</head>
<body>
<%
	from datetime import datetime
%>
%for o in objects:
<div style="clear:both;">
<table width="100%">
	<tr width="100%" align="center">
		<td colspan="2">
			<table width="100%">
				<tr width="100%">
					<td width="80%">
						<font size="4"><b>${o.company_id.name or ''}</b><br/></font>
						${o.company_id.street or ''}<br/>
						${o.company_id.street2 or ''} ${o.company_id.zip or ''}, ${o.company_id.country_id.name or ''}<br/>
						Phone ${o.company_id.phone or ''} Fax ${o.company_id.fax or ''}<br/>
						<u>${o.company_id.website or ''}</u> email :<u>${o.company_id.email or ''}</u>
					</td>
					<td width="20%">
						<img style="width:100px;height=170px" src="data:image/jpg;image/png;base64,${o.company_id.logo}">
					</td>
				</tr>
			</table>
		</td>
	</tr>
	<tr width="100%" align="center"><td colspan="2"><font size="5"><b>SALES ORDER </b></font><br/><br/></td></tr>
	<tr width="100%" valign="top">
		<td width="50%">
			<table width="100%" >
				<tr width="100%" class="alignTop">
					<td width="20%">
						<b>To<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
					${o.partner_id.name or ""} <br/>
						
						%if o.attention:
							${o.attention.street or ""} <br/>
							${o.attention.street2 or ""}<br/>
							${o.attention.city or ""} ${o.attention.state_id.name or ""}  ${o.attention.zip or ""}
						%else:
							${o.partner_id.street or ""} <br/>
							${o.partner_id.street2 or ""}<br/>
							${o.partner_id.city or ""} ${o.partner_id.state_id.name or ""}  ${o.partner_id.zip or ""}
						%endif
					</td>
				</tr>
				<tr width="100%" valign="top">
					<td width="20%">
						<b>Phone<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
						${o.partner_id.phone or ""}
					</td>
				</tr>
				<tr width="100%" class="alignTop">
					<td width="20%">
						<b>Fax<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
						${o.attention.fax or o.partner_id.fax or ""}
					</td>
				</tr>
				<tr width="100%" class="alignTop">
					<td width="20%">
						<b>Attn<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
						${o.attention.name or ""}
					</td>
				</tr>
				<tr width="100%" valign="top">
					<td width="20%">
						<b>Email<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
						${o.attention.email or o.partner_id.email or "-"}
					</td>
				</tr>
				%if o.partner_id==o.partner_shipping_id:

				%else:
					<tr width="100%" valign="top">
						<td width="20%">
							<b>Delivery Address<b/>
						</td>
						<td width="2%">
							<b>:</b>
						</td>
						<td width="80%">
						${o.partner_shipping_id.street or ""} <br/>
						${o.partner_shipping_id.street2 or ""}
						</td>
					</tr>
				%endif
			</table>
		</td>
		<td width="50%">
			<table width="100%">
				<tr width="100%" class="alignTop">
					<td width="20%" class="alignTop">
						<b>SO.No.<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
						${o.name or ""}
					</td>
				</tr>
				<tr width="100%" class="alignTop">
					<td width="20%" class="alignTop">
						<b>PO No.<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
						${o.client_order_ref or ""}
					</td>
				</tr>
				<tr width="100%" class="alignTop">
					<td width="20%" class="alignTop">
						<b>Date<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%" class="alignTop">
						${o.date_order or ""}
					</td>
				</tr>
				<tr width="100%" class="alignTop">
					<td width="25%" class="alignTop">
						<b>Contact Person<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%" class="alignTop">
						${o.user_id.name or "-"}
					</td>
				</tr>
				<tr width="100%" valign="top">
					<td width="20%">
						<b>Phone<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
						${o.user_id.phone or "-"}
					</td>
				</tr>
				<tr width="100%" valign="top">
					<td width="20%">
						<b>Fax<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
						${o.user_id.fax or "-"}
					</td>
				</tr>
				<tr width="100%" valign="top">
					<td width="20%">
						<b>Email<b/>
					</td>
					<td width="2%">
						<b>:</b>
					</td>
					<td width="80%">
						${o.user_id.email or "-"}
					</td>
				</tr>
			</table>
		</td>
	</tr><br/>
	<tr width="100%">
		<td colspan="2" width="100%">
			We would like to offer our product as your requirement as following : <br/><br/><br/>
			<table class="main" width="100%" cellspacing="0">
				<tr width="100%">
					<th width="5%">No</th>
					<th width="10%">Quantity</th>
					<th width="7%">Unit</th>
					<th width="47%">Description</th>
					<th width="15%">Unit Price<br>(${o.pricelist_id.currency_id.name})</th>
					<th width="15%">Price<br>(${o.pricelist_id.currency_id.name})</th>
				</tr>
				<%
					i=1;
				%>
				%for line in o.order_line:
				<tr width="100%">
					<td width="5%" class="alignTop">${i}</td>
					<td width="10%" class="alignCenter alignTop">${line.product_uom_qty}</td>
					<td width="7%" class="alignCenter alignTop">${line.product_uom.name}</td>
					<td width="47%" class="alignTop">${line.name}</td>
					<td width="15%" class="alignRight alignTop">${formatLang(float(line.price_unit),digits=2)}</td>
					<td width="15%" class="alignRight alignTop">${formatLang(float(line.price_unit*line.product_uom_qty),digits=2)}</td>
				</tr>
				
				<% i+=1 %>
				%endfor
				<%
					discount_amount=0.0
					untax_amount=0.0
				%>
				%for line in o.order_line:
					<% untax_amount+=(line.price_unit*line.product_uom_qty) %>
					%if line.discount_nominal:
						<% discount_amount=discount_amount+line.discount_nominal %>
					%elif line.discount:
						<% discount_amount+=(line.discount/100)*(line.price_unit*line.product_uom_qty) %>
					%endif
				%endfor
				<tr width="100%">
					<td colspan="4" rowspan="4" width="70%" style="border:0px solid #000;"></td>
					<td width="15%">Gross Value</td>
					<td width="15%" class="alignRight">${formatLang(float(untax_amount),digits=2)}</td>
				</tr>
				<tr width="100%">
					<td width="15%">Disc</td>
					<td width="15%" class="alignRight">${formatLang(float(discount_amount),digits=2)}</td>
				</tr>
				<tr width="100%">
					<td width="15%">VAT 10%</td>
					<td width="15%" class="alignRight">${o.amount_tax}</td>
				</tr>
				<tr width="100%">
					<td width="15%">Net.</td>
					<td width="15%" class="alignRight">${o.amount_total}</td>
				</tr>
			</table>
		</td>
	</tr>
	
<tr width="100%" align="left">
		<td colspan="2"><font size="3"><br/><b><i>Scope Of Work by PT.Suprabakti Mandiri</i></b><br/>
			<font style="margin-left:20px;">
			%if o.scope_work_supra_text==False:
				-
			%else:
				${o.scope_work_supra_text.replace('\n','<br/>')}
			%endif
			</font>
		</font></td>
	</tr>
	<tr width="100%" align="left">
		<td colspan="2"><font size="3"><br/><b><i>Scope Of Work by ${o.partner_id.name}</i></b><br/>
			
			<font style="margin-left:20px;">
				%if o.scope_work_customer_text==False:
					-
				%else:
					${o.scope_work_customer_text.replace('\n','<br/>')}
				%endif
			</font>
		</font></td>
	</tr>



	<tr width="100%" align="left">
       <td colspan="2"><font size="3"><br/><b><i>Notes</i></b><br/>
       	<font style="margin-left:20px;">
			%if o.note==False:
				-
			%else:
				${o.note.replace('\n','<br/>')}
			%endif
		</font>
                </font></td>
        </tr>

	<tr width="100%" align="left">
		<td colspan="2"><font size="3"><br/><b><i>Terms Of Payment </i></b><br/>
		<ul>
		%if o.term_condition:
			%for tc in o.term_condition:
				<li>${tc.name}</li>
			%endfor
		%else:
			<li>-</li>
		%endif
		</ul>
		</font></td>
	</tr>
		<tr width="100%" align="left">
       <td colspan="2"><font size="3"><br/><b><i>Terms Conditions</i></b><br/>
			<font style="margin-left:20px; display:block;">
			%if o.internal_notes==False:
				-
			%else:
				${o.internal_notes.replace('\n','<br/>')}
			%endif

			</font>
                </font></td>
     </tr>
</table>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<p></p>
<p></p>
<p></p>
<p style="margin-top:20px;"></p>
Thank You and best Regards,<br/>
<strong>PT.Suprabakti Mandiri</strong>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<strong><u>
${o.user_id.name or '-'}
</u></strong>
</div>
%endfor
</body>
</html>

