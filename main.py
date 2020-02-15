import datetime
import os

import jinja2
import webapp2

from google.appengine.ext import ndb

from models import Painting, Gallery, GalleryList, SchoolInfo, ResumeInfo

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
  extensions=['jinja2.ext.autoescape'], autoescape=True)

HOME_PAINTING = 'fatgoldenchickenfinalforwebFB'

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
    if gallery_id.isdigit():
      gallery = Gallery.get_by_id(gallery_id)
    else:
      gallery = None
    if gallery:
      paintings = ndb.get_multi(gallery.painting_keys)
  
      template_values = {
          'year': year,
          'gallery': gallery,
          'paintings': paintings,
          'pool_name': pool_name
      }
  
      template = JINJA_ENVIRONMENT.get_template('gallery.html')
      self.response.write(template.render(template_values))
    else:
      self.error(404)

class PaintingHandler(webapp2.RequestHandler):
  def get(self, pool_name, gallery_id, painting_id):

    year = datetime.datetime.now().year
    if len(painting_id) > 0:
      painting = Painting.get_by_id(painting_id)
    else:
      painting = None
    if gallery_id.isdigit():
      gallery = Gallery.get_by_id(gallery_id)
    else:
      gallery = None
      
    if painting and gallery:
      template_values = {
          'year': year,
          'painting': painting,
          'gallery_url_fragment': gallery_id,
          'pool_name': pool_name
      }
  
      template = JINJA_ENVIRONMENT.get_template('painting.html')
      self.response.write(template.render(template_values))
    else:
      self.error(404)
		
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
    
class LegacyImageHandler(webapp2.RequestHandler):
  def get(self):
    gallery_id = self.request.get('GID')
    if gallery_id.isdigit():
      gallery = Gallery.get_by_id(gallery_id)
    else:
      gallery = None
    painting_param = self.request.get('PID')
    if painting_param.isdigit():
      old_painting_id = int(self.request.get('PID'))
      painting = Painting.get_from_old_id(old_painting_id)
    else:
      painting = None
    if painting and gallery:
      self.redirect('/galleries/' + gallery_id + '/' + painting.key.id())
    else:
      self.error(404)
    
app = webapp2.WSGIApplication([
    ('/', HomeHandler),
    ('/(galleries|archives)', GalleriesHandler),
    ('/(galleries|archives)/([^/]+)', GalleryHandler),
    ('/(galleries|archives)/([^/]+)/([^/]+)', PaintingHandler),
    ('/mission', MissionHandler),
    ('/resume', ResumeHandler),
    ('/image.aspx', LegacyImageHandler)
    ], debug=True)
  