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
	border-top:1px solid #000;
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
			<th style='min-width:80%; font-size:12pt' colspan="9" align="center">General Ledger Entity</th>
		</tr>
	</table>
	<table width="100%">
		<tr>
			<td style='font-weight:bold; font-size:8pt' colspan="9">Date : ${time.strftime('%d %B %Y', time.strptime(data['form']['date_from'],'%Y-%m-%d'))} s/d ${time.strftime('%d %B %Y', time.strptime(data['form']['date_to'],'%Y-%m-%d'))}</td>
		</tr>
		<tr>
			<td style='font-weight:bold; font-size:8pt' colspan="9">Account : ${data['form']['account_from'][1]} s/d ${data['form']['account_to'][1]}</td>
		</tr>
	</table>	
	<table width="100%" cellspacing="0" cellpadding="0px">
		<tr>
			<td colspan="12" style="border-bottom:6px double #000;"></td>
		</tr>
		<tr>
			<th colspan="2">Account</th>
			<th colspan="3">Initial Balance</th>
		</tr>
		<tr id="header2">
			<th align="left">Description</th>
			<th align="left">Date</th>
			<th align="left">Journal</th>
			<th align="center">Debit</th>
			<th align="center">Credit</th>
		</tr>
		%for o in get_account(data) : 
		<tr>
			<td colspan="12" style="1px solid #000;"></td>
		</tr>
		<tr>
			<td style='font-weight:bold; font-size:8pt' align="center" height="30" colspan="2">${o.code} ${o.name}</td>
			<td style='font-weight:bold; font-size:8pt' align="center" height="30" colspan="3">${ koma('%.2f', get_initial(o, data)) }</td>
		</tr>
		    <%
		       debit = 0
		       credit = 0
		    %>   
			%for i in get_line(o, data): 
			<tr>
				<td>${i.name}</td>
				<td>${time.strftime('%d/%m/%Y', time.strptime(i.date,'%Y-%m-%d'))}</td>
				<td align="right">${get_voucher(i.statement_id.name, i.move_id.ref, i.move_id.name)}</td>
				<td align="right" width="100">${koma('%.2f', i.debit)}</td>
				<td align="right" width="100">${koma('%.2f', i.credit)}</td>
			</tr>
			<%
		       debit += i.debit
		       credit += i.credit
		    %>
			%endfor
			<tr class='total1'>
				<td style='font-weight:bold;' colspan="3">${'TOTAL'}</td>
				<td style='font-weight:bold;' align="right">${koma('%.2f', debit)}</td>
				<td style='font-weight:bold;' align="right">${koma('%.2f', credit)}</td>
			</tr>
			<tr class='total1'>
				<td style='font-weight:bold;' colspan="4">Closing Balance</td>
				<td style='font-weight:bold;' align="center">${koma('%.2f', get_initial(o, data)+debit-credit)}</td>
			</tr>
		%endfor
	</table>
</body>
</html>
