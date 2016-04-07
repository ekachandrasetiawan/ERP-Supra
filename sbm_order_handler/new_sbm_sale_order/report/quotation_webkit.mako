
<style>
div{
	min-height:1290px;
	height:1290px;
	margin-top:20px;
	margin-bottom:20px;
	position:relative;
	}
table
	{
	font-size:14px;
	float:left;
	border-collapse:collapse;
	}
table.main tr td { padding: 5px;}

.main
	{
	width:23.7cm;
	margin:0 auto;
	}
.main th
	{
	border:1px solid #000;
	}
.main td
	{
	border:1px solid #000;
	}
	
.headpage
	{
		width:100%;
	}
.logo
	{
		float:right;
		width:20%;
	}
.fontcompany{
	font-size:16px;
	
}
.address1
	{
		float:left;
		width:80%;
		text-align:left;
	}
.alignCenter{
	text-align: center;
}
.alignLeft{
	text-align: left;
}
.alignRight{
	text-align: right;
}

.alignTop{
	vertical-align: top;
}


th {
	background-color: #AEB0B0;
	color: black;
}

</style>
 <%
	from datetime import datetime
%>
%for o in objects:

		

		
				<table class="main" width="100%" cellspacing="0" style="margin-top:7px">
					
					<%
						i=1;
					%>
					%for line in o.order_line:

					<tr width="100%">
						<td width="5%" class="alignTop">${i}</td>
						<td width="10%" class="alignCenter alignTop">${line.product_uom_qty}</td>
						<td width="7%" class="alignCenter alignTop">${line.product_uom.name}</td>
					  <!--   %for material in line.material_lines: -->
						<td width="47%" class="alignTop"> 
							  [${line.product_id.default_code}] ${line.product_id.name}<br/>
							  ${line.name or ""}<br/> 
							   %if len(line.material_lines)>1: 

									   &nbsp; &nbsp;  Consist of :
												 <ul type="circle">
														 %for material in line.material_lines: 
															  <!-- %if material.product_id.name != line.product_id.name: -->
														  <li> [${material.product_id.default_code}]${material.product_id.name}(${material.qty}&nbsp;              ${material.uom.name}) <br/>
															${material.desc or ""}

															</li>
								
													  %endfor
												 </ul>
							 %elif len(line.material_lines)==1:
							 	
								%if line.material_lines.product_id.id[0]!= line.product_id.id:
									   &nbsp; &nbsp;  Consist of :
											<ul type="circle">
												  %for material in line.material_lines: 
								<!-- %if material.product_id.name != line.product_id.name: -->
												<li> [${material.product_id.default_code}]${material.product_id.name}  &nbsp;(${material.qty}&nbsp;${material.uom.name}) <br/>
												${material.desc or ""}

													</li>
							<!-- $endif -->
							   <!-- %endfor -->
											%endfor
										   </ul>


							 %endif

						%endif
						</td>
						<!-- %endfor -->
						<td width="15%" class="alignRight alignTop">${formatLang(float(line.price_unit),digits=2)}</td>
						<td width="15%" class="alignRight alignTop">${formatLang(float(line.price_unit*line.product_uom_qty),digits=2)}<br/>
						%if line.discount_nominal:
						<p style="font-size:12px;">(Disc:&nbsp;${formatLang(float(-line.discount_nominal),digits=2)})</p>
						%endif
						</td>
					</tr>
					
					<% i+=1 %>
					%endfor
				   <tr width="100%">
						<td colspan="4" rowspan="4" width="70%" style="border:none;"></td>
						<td width="15%">Base Total</td>
						<td width="15%" class="alignRight">${formatLang(float(o.base_total),digits=2)}</td>
					</tr>
					<tr width="100%">
						<td width="15%">Discount</td>
						<td width="15%" class="alignRight">${o.total_amount_discount}</td>
					</tr>
					<tr width="100%">
						<td width="15%">Sub Total</td>
						<td width="15%" class="alignRight">${formatLang(float(o.amount_untaxed),digits=2)}</td>
					</tr>
					<tr width="100%">
						<td width="15%">Tax</td>
						<td width="15%" class="alignRight">${o.amount_tax}</td>
					</tr>
					<tr width="100%">
						<td colspan="4" rowspan="4" width="70%" style="border:none;"></td>
						<td width="15%"><b>Total</b></td>
						<td width="15%" class="alignRight"><b>${o.amount_total}</b></td>
					</tr>
				</table>


	<table width="100%" >
		<tr width="100%" class="alignTop">
			<td width="20%">
				<b>Term of Payment</b>
			</td>
			<td width="2%">
				<b>:</b>
			</td>
			<td width="80%">
				 ${o.payment_term.name or ""} <br/>
			  
			</td>
		</tr>
	   
		<tr width="100%" valign="top">
			<td width="20%">
				<b>Term Condition</b>
			</td>
			<td width="2%">
				<b>:</b>
			</td>
			<td width="80%" >
			   <ul type="circle">
			 %for term in o.term_condition:
			  <li>${term.name or ""}</li>

			%endfor
			</ul>
			</td>
		</tr>
		<tr width="100%" class="alignTop">
			<td width="20%">
				<b>Note</b>
			</td>
			<td width="2%">
				<b>:</b>
			</td>
			<td width="80%">
			   ${o.note or ""}<br/><br/>
			</td>
		</tr>
	   <tr>
	   		<td colspan="3">
	   		&nbsp;&nbsp;Thank you and best regards<br/><br/><br/><br/><br/><br/>


		   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${o.user_id.name or "-"} 
	   		</td>
	   </tr>
	   
	</table>
   <footer>
   </footer>
		  


%endfor
<!-- 
  <table width="100%" border="0" class="cell_extended">
			 <tr class ="table_parent_data">
				 <td width="5%" align="center" >
					 <small>Description</small>
				 </td>
				 <td width="5%" align="left" class="head_bottom_border">
					 <small>Taxes</small>  
				 </td>
				 <td width="40%" align="center" >
					 <small><b> Date Req.</small>  
				 </td>
				 <td width="40%" align="right" >
					 <small><b>Qty</b></small>   
				 </td>
				 <td width="5%" align="left" class="head_bottom_border">
					 <small>Unit Price</small>   
				 </td>
				 <td width="5%" align="center">
					 <small>Net Price</small>  
				 </td>
		  </tr>
				
		 </table>
	   -->