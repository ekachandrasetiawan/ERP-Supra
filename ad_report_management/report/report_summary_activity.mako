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
			<th style='min-width:80%; font-size:12pt' colspan="9" align="center">Summary Activity Report</th>
		</tr>
		<tr>
			<th style='min-width:80%; font-size:10pt' colspan="9" align="left">Bulan : ${get_bulan(data)}</th>
		</tr>
	</table>
	
	<table width="100%" cellspacing="0" cellpadding="3px">
		<tr>
			<td colspan="12" style="border-bottom:5px double #000;">&nbsp;</td>
		</tr>
		<tr>
			<th style='font-weight:bold; font-size:10pt'>Salesman</th>
		</tr>
		<tr id="header2">
        	<th style='font-weight:bold; font-size:10pt'>Activity</th>
			<th style='font-weight:bold; font-size:10pt'>Customer</th>
            <th style='font-weight:bold; font-size:10pt'>Location</th>
		</tr>
		%for v, o in get_summary_activity(data).items() :
		<tr>
			<td colspan="12" style="1px solid #000;">&nbsp;</td>
		</tr>
		<tr>
			<td style='font-weight:bold; font-size:10pt'>${o['name']}</td>
		</tr>
			%for i in o['line']:
				%for a in get_summary_location(i['actid']):
				<tr class='total1'>
					<td>${a['activity']}</td>
					<td>${a['loc']}</td>
					<td>${a['cus']}</td>
				</tr>
				%endfor
			%endfor
		%endfor	
	</table>

</body>
</html>
