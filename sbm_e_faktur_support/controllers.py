import web.http as http
from web.http import request

class MyController(http.Controller):
	@http.route('/my_url/some_html',type="http")
	def some_html(self):
		return "<h1>AAAAAAAA</h1>"