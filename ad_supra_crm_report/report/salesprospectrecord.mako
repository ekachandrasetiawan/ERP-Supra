<html>
<body>
<table border="0" width="120%">
	<%
	form=data['form']
	#interval=get_interval(form)
	%>
	<tr>
		<td>
			<table border="1" width="120%">
				<tr width="120%">
					<th width="5%">PIC</th><th width="5%">Reg</th>
					<th width="10%">Customer</th><th width="10%">Product Group</th>
					<th width="10%">Project</th><th width="15%">Last Information</th>
					<th width="10%">Amount</th><th width="7%">State Prospect</th>
					<th colspan="4" width="33%">Quotation/Sales Order Information</th>
				</tr>
				%for line in get_week_line(form):
				<tr width="110%">
					<td rowspan="2" width="5%">${line.status_id.user_id.name}</td>
					<td rowspan="2" width="5%">${line.status_id.type}</td>
					<td rowspan="2" width="10%">${line.name.name}</td>
					<td rowspan="2" width="10%">${line.product_group}</td>
					<td rowspan="2" width="10%">${line.project}</td>
					<td rowspan="2" width="15%">${line.status}</td>
					<td rowspan="2" width="10%">${line.amount} ${line.currency_id.name}</td>
					<td rowspan="2" width="7%">${line.state}</td>
					<td width="8%"><b>Number</b></td>
					<td width="8%"><b>Date Created</b></td>
					<td width="7%"><b>State</b></td>
					<td width="10%"><b>Price</b></td>
				</tr>
				%if line.order_id:
				<tr>
					<td>${line.order_id.name or '-'}</td>
					<td>${line.order_id.date_order or '-'}</td>
					<td>${line.order_id.state or '-'}</td>
					<td>${line.order_id.amount_total or '-'} ${line.order_id.pricelist_id.currency_id.name or ''}</td>
				</tr>
				%else:
				<tr>
					<td>-</td>
					<td>-</td>
					<td>-</td>
					<td>-</td>
				</tr>
				%endif
				%endfor
			</table>
		</td>
	</tr>
</table>
</body>
</html>
