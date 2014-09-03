<html>
<head>
<style>
table
	{
	font-size:10px;
	}
#header2 th
	{
	border-bottom:1px solid #000;
	}
.total1 td
	{
	border-bottom:1px dashed #000;
	}
.total2 td
	{
	border-top:2px solid #000;
	}
.subhead td
	{
	border-bottom:1px solid #D1D1D1;
	}
</style>
</head>
<body>
	<table width="100%">
		<tr>
			<th style='min-width:80%; font-size:12pt' colspan="9" align="center">Outstanding Report</th>
		</tr>
		<tr>
			<th style='min-width:80%; font-size:10pt' colspan="9" align="left">Supplier : ${get_supplier(data)}</th>
		</tr>
	</table>
	
	<table width="100%" cellspacing="0" cellpadding="3px">
		<tr>
			<td colspan="12" style="border-bottom:5px double #000;">&nbsp;</td>
		</tr>
		<tr>
			<th>Sale Order</th>
            <th>Customer Reference</th>
            <th>Due Date</th>
            <th>Attention</th>
		</tr>
		<tr>
			<th>&nbsp;</th>
			<th>Product Name</th>
			<th>Quantity</th>
			<th>UoM</th>
			<th>Delivered</th>
			<th>Outstanding</th>
		</tr>
		<tr id="header2">
			<th>&nbsp;</th>
			<th>Delivery Note</th>
            <th>Delivery Date</th>
			<th>Product Name</th>
			<th>Quantity</th>
			<th>State</th>
		</tr>
		%for o in get_basedon(data) :
		<tr>
			<td colspan="12" style="1px solid #000;">&nbsp;</td>
		</tr>
		<tr>
			<td style='font-weight:bold; font-size:10pt'>${o.name}</td>
            <td style='font-weight:bold; font-size:10pt'>${o.client_order_ref}</td>
            <td style='font-weight:bold; font-size:10pt'>${o.due_date}</td>
            <td style='font-weight:bold; font-size:10pt'>${o.attention.name}</td>
		</tr>
			%for i in o.order_line:
				<tr>
					<td style='font-weight:bold; font-size:10pt'>&nbsp;</td>
		            <td style='font-weight:bold; font-size:10pt'>${i.name}</td>
		            <td style='font-weight:bold; font-size:10pt'>${i.product_uom_qty}</td>
		            <td style='font-weight:bold; font-size:10pt'>${i.product_uom.name}</td>
		            <td style='font-weight:bold; font-size:10pt'>${get_delivered(i)}</td>
		            <td style='font-weight:bold; font-size:10pt'>${i.product_uom_qty-get_delivered(i)}</td>
				</tr>
				%for a in get_outstanding(i):
					<tr class='total1'>
						<td>&nbsp;</td>
						<td>${a.note_id.name}</td>
						<td>${a.note_id.tanggal}</td>
						<td>${a.name}</td>
						<td align="right">${a.product_qty} - ${a.product_uom.name}</td>
						<td>${a.note_id.state}</td>
					</tr>
				%endfor
			%endfor
		%endfor	
	</table>

</body>
</html>
