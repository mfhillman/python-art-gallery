import datetime
import os

import jinja2
import webapp2

from models import Painting, Gallery

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
  extensions=['jinja2.ext.autoescape'], autoescape=True)

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
  def get(self, pool_name):
   
    year = datetime.datetime.now().year
    galleries = [
        Gallery(id='foo', name='Gallery One', front_painting = Painting(file_name = 'legendofsleepyhollow')),
        Gallery(id='foo', name='Gallery Two', front_painting = Painting(file_name = 'legendofsleepyhollow'))
    ]

    template_values = {
        'year': year,
        'galleries': galleries,
        'pool_name': pool_name,
        'pool_title': 'Galleries'
    }

    template = JINJA_ENVIRONMENT.get_template('galleries.html')
    self.response.write(template.render(template_values))

class GalleryHandler(webapp2.RequestHandler):
  def get(self, pool_name, gallery_id):

    year = datetime.datetime.now().year

    painting_one = Painting(file_name='legendofsleepyhollow', title='Legend of Sleepy Hollow')
    painting_two = Painting(file_name='legendofsleepyhollow', title='Legendary Sleepy Hollow')
    gallery = Gallery(
        id=gallery_id,
        name='Sleepy Hollows',
        front_painting=painting_one,
        paintings=[painting_one,painting_two])

    template_values = {
        'year': year,
        'gallery': gallery,
        'pool_name': pool_name
    }

    template = JINJA_ENVIRONMENT.get_template('gallery.html')
    self.response.write(template.render(template_values))

class PaintingHandler(webapp2.RequestHandler):
  def get(self, pool_name, gallery_id, painting_id):

    year = datetime.datetime.now().year

    painting = Painting(file_name='legendofsleepyhollow', title='Legend of Sleepy Hollow', width=50, height=100)

    template_values = {
        'year': year,
        'painting': painting,
        'gallery_id': gallery_id,
        'pool_name': pool_name
    }

    template = JINJA_ENVIRONMENT.get_template('painting.html')
    self.response.write(template.render(template_values))
		
class MissionHandler(webapp2.RequestHandler):
  def get(self):

    year = datetime.datetime.now().year

    template_values = {
        'year': year
    }		

    template = JINJA_ENVIRONMENT.get_template('mission.html')
    self.response.write(template.render(template_values))
    
app = webapp2.WSGIApplication([
    ('/', HomeHandler),
    ('/(galleries|archives)', GalleriesHandler),
    ('/(galleries|archives)/([^/]+)', GalleryHandler),
    ('/(galleries|archives)/([^/]+)/([^/]+)', PaintingHandler),
    ('/mission', MissionHandler),
    ], debug=True)
  