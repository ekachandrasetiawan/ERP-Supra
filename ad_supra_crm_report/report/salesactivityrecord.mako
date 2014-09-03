<html>
<body>
<table border="0" width="100%">
	<%
	form=data['form']
	#interval=get_interval(form)
	%>
	%for sp in get_sales_person(form):
	<tr>
		<td>
			<table border="0" width="100%">
				<%
				sa=get_sales_activity(form,sp.id)
				%>
				<tr><td>Sales person : ${sp.name}
				%if not sa:
					<br/>No Data Found</td></tr>
				%else:
				</td></tr>
				%for x in sa:
				<%
					weekbefplanrow = [len(x.beforeplansenin),len(x.beforeplanselasa),len(x.beforeplanrabu),len(x.beforeplankamis),len(x.beforeplanjumat),len(x.beforeplansabtu),len(x.beforeplanahad)]
					weekbefactrow = [len(x.beforeactualsenin),len(x.beforeactualselasa),len(x.beforeactualrabu),len(x.beforeactualkamis),len(x.beforeactualjumat),len(x.beforeactualsabtu),len(x.beforeactualahad)]
					weekaftplanrow = [len(x.afterplansenin),len(x.afterplanselasa),len(x.afterplanrabu),len(x.afterplankamis),len(x.afterplanjumat),len(x.afterplansabtu),len(x.afterplanahad)]
					weekaftactrow = [len(x.afteractualsenin),len(x.afteractualselasa),len(x.afteractualrabu),len(x.afteractualkamis),len(x.afteractualjumat),len(x.afteractualsabtu),len(x.afteractualahad)]
				%>
				<tr><td><b>Before Launch</b></td></tr>
				<tr width="100%">
					<td>
						<table border="1" width="100%">
							<tr width="100%"><th width="9%"> </th><th width="13%">Senin</th><th width="13%">Selasa</th><th width="13%">Rabu</th><th width="13%">Kamis</th><th width="13%">Jumat</th><th width="13%">Sabtu</th><th width="13%">Minggu</th></tr>
							%if max(weekbefplanrow)==0:
								<tr><td>Plan</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
							%else:
							%for bp in range(0,max(weekbefplanrow)):
							<tr>
								<td>Plan</td>
								<td>
									%if x.beforeplansenin:
										%if len(x.beforeplansenin)>bp:
											<i>Customer</i> : <br/>${x.beforeplansenin[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeplansenin[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeplansenin[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.beforeplansenin[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeplanselasa:
										%if len(x.beforeplanselasa)>bp:
											<i>Customer</i> : <br/>${x.beforeplanselasa[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeplanselasa[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeplanselasa[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.beforeplanselasa[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeplanrabu:
										%if len(x.beforeplanrabu)>bp:
											<i>Customer</i> : <br/>${x.beforeplanrabu[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeplanrabu[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeplanrabu[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.beforeplanrabu[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeplankamis:
										%if len(x.beforeplankamis)>bp:
											<i>Customer</i> : <br/>${x.beforeplankamis[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeplankamis[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeplankamis[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.beforeplankamis[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeplanjumat:
										%if len(x.beforeplanjumat)>bp:
											<i>Customer</i> : <br/>${x.beforeplanjumat[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeplanjumat[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeplanjumat[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.beforeplanjumat[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeplansabtu:
										%if len(x.beforeplansabtu)>bp:
											<i>Customer</i> : <br/>${x.beforeplansabtu[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeplansabtu[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeplansabtu[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.beforeplansabtu[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeplanahad:
										%if len(x.beforeplanahad)>bp:
											<i>Customer</i> : <br/>${x.beforeplanahad[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeplanahad[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeplanahad[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.beforeplanahad[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
							</tr>
							%endfor
							%endif
							%if max(weekbefactrow)==0:
								<tr><td>Actual</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
							%else:
							%for ba in range(0,max(weekbefactrow)):
							<tr>
								<td>Actual</td>
								<td>
									%if x.beforeactualsenin:
										%if len(x.beforeactualsenin)>bp:
											<i>Customer</i> : <br/>${x.beforeactualsenin[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeactualsenin[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeactualsenin[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.beforeactualsenin[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeactualselasa:
										%if len(x.beforeactualselasa)>bp:
											<i>Customer</i> : <br/>${x.beforeactualselasa[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeactualselasa[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeactualselasa[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.beforeactualselasa[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeactualrabu:
										%if len(x.beforeactualrabu)>bp:
											<i>Customer</i> : <br/>${x.beforeactualrabu[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeactualrabu[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeactualrabu[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.beforeactualrabu[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeactualkamis:
										%if len(x.beforeactualkamis)>bp:
											<i>Customer</i> : <br/>${x.beforeactualkamis[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeactualkamis[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeactualkamis[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.beforeactualkamis[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeactualjumat:
										%if len(x.beforeactualjumat)>bp:
											<i>Customer</i> : <br/>${x.beforeactualjumat[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeactualjumat[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeactualjumat[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.beforeactualjumat[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeactualsabtu:
										%if len(x.beforeactualsabtu)>bp:
											<i>Customer</i> : <br/>${x.beforeactualsabtu[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeactualsabtu[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeactualsabtu[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.beforeactualsabtu[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.beforeactualahad:
										%if len(x.beforeactualahad)>bp:
											<i>Customer</i> : <br/>${x.beforeactualahad[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.beforeactualahad[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.beforeactualahad[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.beforeactualahad[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
							</tr>
							%endfor
							%endif
						</table>
					</td>
				</tr>
				<tr><td><b>After Launch</b></td></tr>
				<tr width="100%">
					<td>
						<table border="1" width="100%">
							<tr width="100%"><th width="9%"> </th><th width="13%">Senin</th><th width="13%">Selasa</th><th width="13%">Rabu</th><th width="13%">Kamis</th><th width="13%">Jumat</th><th width="13%">Sabtu</th><th width="13%">Minggu</th></tr>
							%if max(weekaftplanrow)==0:
								<tr><td>Plan</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
							%else:
							%for ap in range(0,max(weekaftplanrow)):
							<tr>
								<td>Plan</td>
								<td>
									%if x.afterplansenin:
										%if len(x.afterplansenin)>bp:
											<i>Customer</i> : <br/>${x.afterplansenin[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afterplansenin[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afterplansenin[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.afterplansenin[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afterplanselasa:
										%if len(x.afterplanselasa)>bp:
											<i>Customer</i> : <br/>${x.afterplanselasa[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afterplanselasa[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afterplanselasa[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.afterplanselasa[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afterplanrabu:
										%if len(x.afterplanrabu)>bp:
											<i>Customer</i> : <br/>${x.afterplanrabu[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afterplanrabu[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afterplanrabu[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.afterplanrabu[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afterplankamis:
										%if len(x.afterplankamis)>bp:
											<i>Customer</i> : <br/>${x.afterplankamis[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afterplankamis[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afterplankamis[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.afterplankamis[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afterplanjumat:
										%if len(x.afterplanjumat)>bp:
											<i>Customer</i> : <br/>${x.afterplanjumat[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afterplanjumat[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afterplanjumat[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.afterplanjumat[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afterplansabtu:
										%if len(x.afterplansabtu)>bp:
											<i>Customer</i> : <br/>${x.afterplansabtu[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afterplansabtu[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afterplansabtu[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.afterplansabtu[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afterplanahad:
										%if len(x.afterplanahad)>bp:
											<i>Customer</i> : <br/>${x.afterplanahad[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afterplanahad[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afterplanahad[bp].location or '-'}
											<br/><i>Objective</i> : <br/>${x.afterplanahad[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
							</tr>
							%endfor
							%endif
							%if max(weekaftactrow)==0:
								<tr><td>Actual</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
							%else:
							%for aa in range(0,max(weekaftactrow)):
							<tr>
								<td>Actual</td>
								<td>
									%if x.afteractualsenin:
										%if len(x.afteractualsenin)>bp:
											<i>Customer</i> : <br/>${x.afteractualsenin[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afteractualsenin[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afteractualsenin[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.afteractualsenin[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afteractualselasa:
										%if len(x.afteractualselasa)>bp:
											<i>Customer</i> : <br/>${x.afteractualselasa[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afteractualselasa[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afteractualselasa[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.afteractualselasa[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afteractualrabu:
										%if len(x.afteractualrabu)>bp:
											<i>Customer</i> : <br/>${x.afteractualrabu[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afteractualrabu[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afteractualrabu[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.afteractualrabu[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afteractualkamis:
										%if len(x.afteractualkamis)>bp:
											<i>Customer</i> : <br/>${x.afteractualkamis[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afteractualkamis[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afteractualkamis[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.afteractualkamis[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afteractualjumat:
										%if len(x.afteractualjumat)>bp:
											<i>Customer</i> : <br/>${x.afteractualjumat[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afteractualjumat[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afteractualjumat[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.afteractualjumat[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afteractualsabtu:
										%if len(x.afteractualsabtu)>bp:
											<i>Customer</i> : <br/>${x.afteractualsabtu[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afteractualsabtu[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afteractualsabtu[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.afteractualsabtu[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
								<td>
									%if x.afteractualahad:
										%if len(x.afteractualahad)>bp:
											<i>Customer</i> : <br/>${x.afteractualahad[bp].partner_id.name or '-'}
											<br/><i>Quotation</i> : <br/>${x.afteractualahad[bp].order_id.name or '-'}
											<br/><i>Location</i> : <br/>${x.afteractualahad[bp].location or '-'}
											<br/><i>Result</i> : <br/>${x.afteractualahad[bp].name.replace("/n","<br/>")}
										%endif
									%else:
										${''}
									%endif
								</td>
							</tr>
							%endfor
							%endif
						</table>
					</td>
				</tr>
				%endfor
				%endif
			</table>
		</td>
	</tr>
	%endfor
</table>
</body>
</html>
