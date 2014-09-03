<html>
<body>
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
%for o in objects :
		<table class='listitem' width='100%'>
			<tr width='100%'>
				<th width='5%'>
					<a>No.<a/>
				</th>
				<th width='23%'>
					<a>Jumlah<a/>
				</th>
				<th width='72%'>
					<a>Uraian Pekerjaan<a/>
				</th>
			</tr>
			<%
				i=1;
			%>
			%for line in o.perintah_lines:
			<tr width='100%'>
				<td width='5%' valign='top' align='center'>
					${i}
				</td>
				<td width='23%' valign='top' align='left'>
					${line.product_qty} ${line.product_uom.name}
				</td>
				<td width='72%'>
					${line.product_id.name}<br/>
					%if line.name==False:
					
					%else:
					    ${line.name.replace('\n','<br/>')}
					%endif
				</td>
				<%
					i+=1;
				%>
			</tr>
			%endfor
			<tr width='100%'>
				<td colspan='3'> 
				</td>
			</tr>
			<tr width='100%'>
				<td width='5%'>
				</td>
				<td width='23%'>
				</td>
				<td width='72%'>
					%if o.note==False:
					
					%else:
					    Note : <br/>
					    ${o.note.replace('\n','<br/>')}
					%endif
				</td>
			</tr>
		</table>
%endfor
</body>
</html>
