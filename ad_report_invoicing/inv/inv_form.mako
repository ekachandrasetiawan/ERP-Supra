<html>
<head>
<style>
${css}

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
%for o in objects:
<table class='listitem' width='100%'>
	<tr width='100%' height='30px'>
		<th width="5%">
			<a>NO.</a>
		</th>
		<th width="18%">
			<a>QUANTITY</a>
		</th>
		<th width="41%">
			<a>DESCRIPTION</a></th>
		<th width="18%">
			<a>UNIT PRICE</a></th>
		<th width="18%">
			<a>EXT. PRICE</a>
		</th>
	</tr>
	%for line in o.invoice_line:
	<tr width='100%'>
		<td width='5%' valign='top' align='center'>
			
		</td>
		<td width='18%' valign='top' align='left'>
			${line.quantity or '-'} ${line.uos_id.name or '-'}
		</td>
		<td width='41%'>
			${line.product_id.name or '-'}<br/>
			%if line.name==False:
			
			%else:
			    ${line.name.replace('\n','<br/>')}
			%endif
		</td>
		<td width='18%' valign='top' align='center'>
			${line.price_unit or '-'}
		</td>
		<td width='18%' valign='top' align='center'>
			${line.price_subtotal or '-'}
		</td>
	</tr>
	%endfor
	<tr width='100%'>
		<td colspan='5'> 
		</td>
	</tr>
	<tr width='100%'>
		<td width='5%'>
		</td>
		<td width='18%'>
		</td>
		<td width='41%'>
			%if o.comment==False:
			
			%else:
			    Note : <br/>
			    ${o.comment.replace('\n','<br/>')}
			%endif
		</td>
		<td width='18%'>
		</td>
		<td width='18%'>
		</td>
	</tr>
</table>
%endfor
</body>
</html>