import datetime
import os

import jinja2
import webapp2

from models import Painting

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

HOME_PAINTING = 'legendofsleepyhollow'

class HomeHandler(webapp2.RequestHandler):
    def get(self):
   
		year = datetime.datetime.now().year
		header_painting = Painting(file_name=HOME_PAINTING)

		template_values = {
        	'year': year,
        	'painting': header_painting
		}		

		template = JINJA_ENVIRONMENT.get_template('home.html')
		self.response.write(template.render(template_values))
        
app = webapp2.WSGIApplication([
    ('/', HomeHandler)
], debug=True)