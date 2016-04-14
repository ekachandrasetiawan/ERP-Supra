
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.web.http as http
from openerp.modules.registry import Registry, RegistryManager
class SimpleController(http.Controller):
	_cp_path = '/sales_activity_plan'


	@http.jsonrequest
	def Getall(self, req,db=None):

		registry = Registry(db)
	
		with registry.cursor() as cr:

			query = cr.execute("""
				SELECT * from sales_activity_plan order by year_p DESC, week_no DESC, dow DESC, user_id, daylight, not_planned_actual limit 100
				""")
			values = cr.fetchall()
		return values

	@http.jsonrequest
	def GetUpdate(self, req,db=None,activity_id=None,user_id=None,dow=None,daylight=None,idview=None):
		
		registry = Registry(db)
		with registry.cursor() as cr:

			query = cr.execute('''
				SELECT id from sales_activity_plan where activity_id=%s and user_id=%s and dow=%s and daylight=%s order by year_p DESC, week_no DESC, dow DESC, user_id, daylight, not_planned_actual limit 1
				''',[activity_id,user_id,dow,daylight])
			
			ids_sales_act = cr.fetchall()
			ids_sales_act=ids_sales_act[0][0]
			
			
			query = cr.execute("""
				SELECT * from sales_activity_plan where id < %s order by year_p DESC, week_no DESC, dow DESC, user_id, daylight, not_planned_actual limit 600
				""",(ids_sales_act,))
			values = cr.fetchall()
			
		
		return values

	@http.jsonrequest
	def GetSearch(self, req,params=None):
		condition= params['condition']
		
		registry = Registry(params['db'])
		
		if len(condition)>1:
			cond4query= " where "
			index=0
			for idx_c,key in enumerate(condition):
				# print key,"iniiii idx_c ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????"
				if len(condition[key]) >1 :
					
					for idx,qry in enumerate(condition[key]):
					
						try:
							if condition[key][idx+1]:
								if type(qry)==int:
									cond4query=cond4query+key+"="+str(qry)+" "+params['AndOr'][index]+" "
								else:
									cond4query=cond4query+key+"="+"'"+qry+"'"+" "+params['AndOr'][index]+" "
									index+=1
						except IndexError:
							print "sini"
							cond4query=cond4query+key+"="+"'"+qry+"'"
				else:

					try:
						
						print "ok"
						if type(condition[key][0])==int:
							cond4query=cond4query+key+"="+str(condition[key][0])+" "+params['AndOr'][index]+" " 
							index+=1
						else:
							cond4query=cond4query+key+"="+"'"+condition[key][0]+"'"+" "+params['AndOr'][index]+" " 
							index+=1
					except IndexError:
						print "sana"
						if type(condition[key][0])==int:
							cond4query=cond4query+key+"="+str(condition[key][0])
								
						else:
							cond4query=cond4query+key+"="+"'"+condition[key][0]+"'" 
						
						
						
		else:
			cond4query= " where "
			for key in condition:
				
				if len(condition[key]) >1 :
					
					for idx,qry in enumerate(condition[key]):
					
						try:
							if condition[key][idx+1]:
								if type(qry)==int:
									cond4query=cond4query+key+"="+str(qry)+" "+params['AndOr'][index]+" "
								else:
									cond4query=cond4query+key+"="+"'"+qry+"'"+" "+params['AndOr'][index]+" "
									index+=1
						except IndexError:
							if type(qry)==int:
									cond4query=cond4query+key+"="+str(qry)
							else:
								cond4query=cond4query+key+"="+"'"+qry+"'"
				else:
					print condition[key][0] ,"ggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"
					if type(condition[key][0])==int:
						cond4query=cond4query+key+"="+str(condition[key][0])
					else:
						cond4query=cond4query+key+"="+"'"+condition[key][0]+"'"
			
			
							
				
		print cond4query,"ini cond4query "
	
		with registry.cursor() as cr:

			query = cr.execute("""
				SELECT """+params['fields']+""" from """+params['table']+""" """+cond4query+""" """+params['order']+""" limit %s offset %s
				""",(params['limit'],params['offset'],))
			values = cr.fetchall()
		return values