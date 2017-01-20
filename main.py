import datetime
import os

import jinja2
import webapp2

from models import Painting, Gallery

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

class GalleriesHandler(webapp2.RequestHandler):
    def get(self):
   
		year = datetime.datetime.now().year
		
		galleries = [
		  Gallery(gallery_id='foo', name='Gallery One', front_painting = Painting(file_name = 'legendofsleepyhollow')),
		  Gallery(gallery_id='foo', name='Gallery Two', front_painting = Painting(file_name = 'legendofsleepyhollow'))
		]


		template_values = {
        	'year': year,
        	'galleries': galleries
		}		

		template = JINJA_ENVIRONMENT.get_template('galleries.html')
		self.response.write(template.render(template_values))
		
app = webapp2.WSGIApplication([
    ('/', HomeHandler),
    ('/galleries', GalleriesHandler),
], debug=True)