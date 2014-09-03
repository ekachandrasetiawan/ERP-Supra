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
			<th style='min-width:80%; font-size:12pt' colspan="9" align="center">Summary Product</th>
		</tr>
		<tr>
			<th style='min-width:80%; font-size:10pt' colspan="9" align="left">Customer : ${get_supplier(data)}</th>
		</tr>
	</table>
	
	<table width="100%" cellspacing="0" cellpadding="3px">
		<tr>
			<td colspan="12" style="border-bottom:5px double #000;">&nbsp;</td>
		</tr>
		<tr id="header2">
			<th>Sale Order</th>
            <th>Customer Reference</th>
			<th>Product Name</th>
			<th>Quantity</th>
			<th>UoM</th>
			<th>Unit Price</th>
		</tr>
		%for o in get_summary_product(data) :
		<tr class='total1'>
			<td style='font-weight:bold; font-size:10pt'>${o.order_id.name}</td>
            <td style='font-weight:bold; font-size:10pt'>${o.order_id.client_order_ref}</td>
            <td style='font-weight:bold; font-size:10pt'>${o.name}</td>
            <td style='font-weight:bold; font-size:10pt'>${o.product_uom_qty}</td>
            <td style='font-weight:bold; font-size:10pt'>${o.product_uom.name}</td>
            <td style='font-weight:bold; font-size:10pt'>${o.price_unit} ${o.order_id.pricelist_id.currency_id.symbol}</td>
		</tr>
		%endfor	
	</table>

</body>
</html>
