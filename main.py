import datetime
import os

import jinja2
import webapp2

from google.appengine.ext import ndb

from models import Painting, Gallery, GalleryList, SchoolInfo, ResumeInfo

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
  extensions=['jinja2.ext.autoescape'], autoescape=True)

HOME_PAINTING = 'legendofsleepyhollow'

class HomeHandler(webapp2.RequestHandler):
  def get(self):
  
    year = datetime.datetime.now().year
    header_painting = Painting.get_by_id(HOME_PAINTING)

    template_values = {
        'year': year,
        'painting': header_painting
    }		

    template = JINJA_ENVIRONMENT.get_template('home.html')
    self.response.write(template.render(template_values))

class GalleriesHandler(webapp2.RequestHandler):
  def get(self, pool_name):
   
    year = datetime.datetime.now().year
    gallery_keys = GalleryList.get_by_id(pool_name).gallery_keys
    galleries = ndb.get_multi(gallery_keys)
    front_painting_keys = map(lambda g: ndb.Key(Painting, g.front_painting_id), galleries)
    front_paintings = ndb.get_multi(front_painting_keys)
    pairs = zip(galleries, front_paintings)
    
    template_values = {
        'year': year,
        'gallery_front_pairs': pairs,
        'pool_name': pool_name,
        'pool_title': 'Galleries'
    }

    template = JINJA_ENVIRONMENT.get_template('galleries.html')
    self.response.write(template.render(template_values))

class GalleryHandler(webapp2.RequestHandler):
  def get(self, pool_name, gallery_id):

    year = datetime.datetime.now().year
    gallery = Gallery.get_by_id(gallery_id)
    paintings = ndb.get_multi(gallery.painting_keys)

    template_values = {
        'year': year,
        'gallery': gallery,
        'paintings': paintings,
        'pool_name': pool_name
    }

    template = JINJA_ENVIRONMENT.get_template('gallery.html')
    self.response.write(template.render(template_values))

class PaintingHandler(webapp2.RequestHandler):
  def get(self, pool_name, gallery_id, painting_id):

    year = datetime.datetime.now().year
    painting = Painting.get_by_id(painting_id)

    template_values = {
        'year': year,
        'painting': painting,
        'gallery_url_fragment': gallery_id,
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

class ResumeHandler(webapp2.RequestHandler):
  def get(self):

    resume = ResumeInfo.retrieve()
    year = datetime.datetime.now().year

    template_values = {
        'year': year,
        'exhibitions': resume.exhibitions,
        'honors': resume.honors,
        'schools': resume.schools
    }		

    template = JINJA_ENVIRONMENT.get_template('resume.html')
    self.response.write(template.render(template_values))
    
app = webapp2.WSGIApplication([
    ('/', HomeHandler),
    ('/(galleries|archives)', GalleriesHandler),
    ('/(galleries|archives)/([^/]+)', GalleryHandler),
    ('/(galleries|archives)/([^/]+)/([^/]+)', PaintingHandler),
    ('/mission', MissionHandler),
    ('/resume', ResumeHandler),
    ], debug=True)
  