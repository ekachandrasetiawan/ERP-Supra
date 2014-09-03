<html>
	<head>
	<style>
		body {
		font-family:helvetica;
		font-size:12;
		}
		
		.footer td{
		font-size:12;
		}
		
		.header {
		margin-left:0;
		text-align:left;
		}
		
		.header td {
		font-size:12;
		}
		
		.listitem td{
		font-size:12;
		}
		
		.listitem th{
		font-size:12;
		}
		
		a{
			font-size:12;
			opacity:0;
		}
	</style>
	</head>
	<body>
	<%
		form=data['form']
		print "++++++++++",get_object(data)[0].name
	%>
	
	%for o in get_object(data):
		<table class='listitem' width='100%'>
			<tr width='100%' height='35px'>
				<td width="12%"><a><b>Item No.</b></a></td>
				<td width="10%"><a><b>Q'tity</b></a></td>
				<td width="50%"><a><b>Description</b></a></td>
				<td width="10%"><a><b>Weight</b></a></td>
				<td width="18%"><a><b>Measurement</b></a></td>
			</tr>
			%for line in o.product_lines:
			<tr width='100%'>
				<td width='12%' valign='top' align='center'>
				</td>
				<td width='10%' valign='top' align='left'>
					${line.product_qty} ${line.product_uom.name}
				</td>
				<td width='50%' valign='top' align='left'>
					${line.product_id.name}<br/>
					%if line.name==False:
					
					%else:
					    ${line.name.replace('\n','<br/>')}
					%endif
				</td>
				<td width='10%'>
				</td>
				<td width='18%'>
				</td>
			</tr>
			%endfor
		</table>
	%endfor
	</body>
</html>