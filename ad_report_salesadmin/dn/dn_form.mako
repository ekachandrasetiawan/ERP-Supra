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
<script>
</script>
</head>
<body>
%for o in objects:
<table class='listitem' width='100%'>
	<tr width='100%' height='30px'>
		<th width='14%'>
			<a>ITEM NO<a/>
		</th>
		<th width='17%'>
			<a>JUMLAH<a/>
		</th>
		<th width='51%'>
			<a>JENIS BARANG<a/>
		</th>
		<th width='18%'>
			<a>PART NO<a/>
		</th>
	</tr>
	%for line in o.note_lines:
	<tr width='100%'>
		<td width='14%' valign='top' align='center'>
			${line.itemno or ''}
		</td>
		<td width='17%' valign='top' align='left'>
			${line.product_qty or '-'} ${line.product_uom.name or '-'}
		</td>
		<td width='51%'>
			${line.product_id.name or '-'}<br/>
			%if line.name==False:
			
			%else:
			    ${line.name.replace('\n','<br/>')}
			%endif
		</td>
		<td width='18%' valign='top' align='center'>
			${line.product_id.default_code or '-'}
		</td>
	</tr>
	%endfor
	<tr width='100%'>
		<td colspan='4'> 
		</td>
	</tr>
	<tr width='100%'>
                <td width='14%'>
                </td>
                <td width='17%'>
                </td>
                <td width='51%'>
                        %if o.packing_lines:
				<table width='70%'>
					<tr width='70%'>
						<td width='33%'>Pack</td>
						<td width='33%'>Measurement</td>
						<td width='33%'>Weight</td>
					</tr>
				%for pack in o.packing_lines:
					<tr width='50%'>
                                                <td width='33%'>${pack.name}</td>
                                                <td width='33%'>${pack.measurement}</td>
                                                <td width='33%'>${pack.weight}</td>
                                        </tr>
				%endfor
			%endif
                </td>
                <td width='18%'>
                </td>
        </tr>
	<tr width='100%'>
		<td width='14%'>
		</td>
		<td width='17%'>
		</td>
		<td width='51%'>
			%if o.note==False:
			
			%else:
			    Note : <br/>
			    ${o.note.replace('\n','<br/>')}
			%endif
		</td>
		<td width='18%'>
		</td>
	</tr>
</table>
%endfor
</body>
</html>
