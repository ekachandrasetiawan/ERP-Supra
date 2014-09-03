<html>
<head>
<style>
${css}

.listitem td{
font-size:13;
}

.listitem th{
font-size:13;
}

a{
	font-size:13;
	opacity:0;
}

</style>
</head>
<body>
	%for o in objects:
		<table class='listitem' width='100%'>
			<tr width='100%' height='35px'>
				<th width='8%'>
					<a>No.<a/>
				</th>
				<th width='28%'>
					<a>Jumlah<a/>
				</th>
				<th width='64%'>
					<a>Nama Barang<a/>
				</th>
			</tr>
			%for line in o.prepare_lines:
			<tr width='100%'>
				<td width='8%' valign='top' align='center'>
					
				</td>
				<td width='28%' valign='top' align='left'>
					${line.product_qty or '-'} ${line.product_uom.name or '-'}
				</td>
				<td width='64%'>
					${line.product_id.name or '-'}<br/>
					%if line.name==False:
					
					%else:
					    ${line.name.replace('\n','<br/>')}
					%endif
				</td>
			</tr>
			%endfor
			<tr width='100%'>
				<td colspan='3'> 
				</td>
			</tr>
			<tr width='100%'>
				<td width='8%'>
				</td>
				<td width='28%'>
				</td>
				<td width='64%'>
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

