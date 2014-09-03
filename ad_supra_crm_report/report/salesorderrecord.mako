<html>
<body>
<table border="1">
	<%
	form=data['form']
	interval=get_interval(form)
	total=0
	%>
	
	<tr>
	<th>Regional</th><th>Salesman</th>
	%for x in range(len(interval)):
		<th>
		${min(interval[str(x+int(min(interval.keys())))])} - ${max(interval[str(x+int(min(interval.keys())))])} 
		</th>
	%endfor
	</tr>
	
	%for reg in get_regional():
		%for sales in get_sales_person(form,reg.id):
			<tr><td>${reg.name}</td><td>${sales.user_id.name}</td>
			%for week in range(len(interval)):
				%for so in get_sales_order(form,sales.user_id.id,interval[str(week+int(min(interval.keys())))]):
					<% 
					total+=so.amount_total
					%>
				%endfor
				<td>${total}</td>
				<% 
				total=0
				%>
			%endfor
			</tr>
		%endfor
	%endfor
</table>
</body>
</html>