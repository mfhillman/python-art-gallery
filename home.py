import jinja2
import os
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

class HomeHandler(webapp2.RequestHandler):
    def get(self):
   
		year = '2016'
		headerPaintingUrl = 'foobar'

		template_values = {
        	'year': year,
        	'paintingUrl': headerPaintingUrl
		}		

		template = JINJA_ENVIRONMENT.get_template('home.html')
		self.response.write(template.render(template_values))
        