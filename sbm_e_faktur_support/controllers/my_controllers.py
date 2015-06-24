import base64
import openerp.addons.web.http as oeweb
from openerp.addons.web.controllers.main import content_disposition

#----------------------------------------------------------
# Controller
#----------------------------------------------------------
class my_controllers(oeweb.Controller):
	_cp_path = '/my'

	@oeweb.httprequest
	def index(self, req):
		
		return req
