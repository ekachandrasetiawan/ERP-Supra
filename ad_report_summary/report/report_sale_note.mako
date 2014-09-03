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
			<th style='min-width:80%; font-size:12pt' colspan="9" align="center">Summary Report</th>
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
			<th>Order Packaging</th>
            <th>Date Preparation</th>
			<th>Product Name</th>
			<th>Quantity</th>
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
			%for i in o.preparation_line:
				%for z in i.prepare_lines:
				<tr>
					<td style='font-weight:bold; font-size:10pt'>&nbsp;</td>
		            <td style='font-weight:bold; font-size:10pt'>${i.name}</td>
		            <td style='font-weight:bold; font-size:10pt'>${i.tanggal}</td>
		            <td style='font-weight:bold; font-size:10pt'>${z.name}</td>
		            <td style='font-weight:bold; font-size:10pt'>${z.product_qty} - ${z.product_uom.name}</td>
				</tr>
				%endfor
				%for a in i.delivery_lines:
					%for x in a.note_lines: 
					<tr class='total1'>
						<td>&nbsp;</td>
						<td>${a.name}</td>
						<td>${a.tanggal}</td>
						<td>${x.name}</td>
						<td align="right">${x.product_qty} - ${x.product_uom.name}</td>
						<td>${a.state}</td>
					</tr>
					%endfor
				%endfor
			%endfor
		%endfor	
	</table>

</body>
</html>
