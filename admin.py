import csv
import jinja2
import os
import string
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users

from models import Painting, Gallery, GalleryList, SchoolInfo, ResumeInfo, ResumeHistory

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
  extensions=['jinja2.ext.autoescape'], autoescape=True)
  
class AdminHandler(webapp2.RequestHandler):
  def get(self):
  
    resume = ResumeInfo.retrieve()
    exhibitions_text = '\n'.join(resume.exhibitions)
    honors_text = '\n'.join(resume.honors)
    school_strs = []
    for school in resume.schools:
      school_strs.append(school.to_admin_str())
    schools_text = '\n'.join(school_strs)
    
    template = JINJA_ENVIRONMENT.get_template('admin.html')
    self.response.out.write(template.render(
        exhibitions_text=exhibitions_text,
        honors_text=honors_text,
        schools_text=schools_text))
      
class ConfirmHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write('Confirmed!<br>')
    
class UpdateExhibitionsHandler(webapp2.RequestHandler):
  def post(self):
    new_exhibitions = self.request.get('content')
    exhibition_list = string.split(new_exhibitions, '\n')
    
    resume = ResumeInfo.retrieve()
    resume.exhibitions = exhibition_list
    resume.save()
    
    self.redirect('/admin/confirm')

class UpdateHonorsHandler(webapp2.RequestHandler):
  def post(self):
    new_honors = self.request.get('content')
    honors_list = string.split(new_honors, '\n')
    
    resume = ResumeInfo.retrieve()
    resume.honors = honors_list
    resume.save()
    
    self.redirect('/admin/confirm')
    
class UpdateSchoolsHandler(webapp2.RequestHandler):
  def post(self):
    new_schools = self.request.get('content')
    schools_list = string.split(new_schools, '\n')
    schools = []
    
    for school_text in schools_list:
      info = SchoolInfo()
      info.from_admin_str(school_text)
      schools.append(info)
      
    resume = ResumeInfo.retrieve()
    resume.schools = schools
    resume.save()
    
    self.redirect('/admin/confirm')
    
class PaintingCsvHandler(webapp2.RequestHandler):
  def get(self):
    with open('csvs/paintings.csv') as csvfile:
      reader = csv.DictReader(csvfile)
      paintings = []
      for row in reader:
        self.response.write(row['Title'] + ' ' + row['ImageBaseName'] + '<BR>')
        painting = Painting(
            id=row['ImageBaseName'],
            title=row['Title'], 
            width=int(row['WidthInches']) if row['WidthInches'] else 0,
            height=int(row['HeightInches']) if row['HeightInches'] else 0,
            old_id=int(row['PaintingID']))
        paintings.append(painting)

      ndb.put_multi(paintings)
      
class GalleryStructureHandler(webapp2.RequestHandler):
  def get(self):
    # Read paintings to map ids to filenames
    painting_map = {}
    with open('csvs/paintings.csv') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        painting_map[row['PaintingID']] = row['ImageBaseName']
        
    with open('csvs/galleries.csv') as csvfile:
      reader = csv.DictReader(csvfile)
      sorted_galleries = sorted(reader, key=lambda row: int(row['GalleryOrder']))
      galleries = GalleryList(id="galleries")
      archives = GalleryList(id="archives")
      for gallery in sorted_galleries:
        if gallery['Archived'] == '1':
          archives.gallery_keys.append(ndb.Key(Gallery, gallery['GalleryID']))
        else:
          galleries.gallery_keys.append(ndb.Key(Gallery, gallery['GalleryID']))
      
      ndb.put_multi([galleries, archives])

      for gallery in galleries.gallery_keys:
        self.response.write(gallery.id() + '<BR>')        
    
app = webapp2.WSGIApplication([
    ('/admin', AdminHandler),
    ('/admin/confirm', ConfirmHandler),
    ('/admin/update_exhibitions', UpdateExhibitionsHandler),
    ('/admin/update_honors', UpdateHonorsHandler),
    ('/admin/update_schools', UpdateSchoolsHandler),
    ('/admin/painting_csv', PaintingCsvHandler),
    ('/admin/gallery_structure', GalleryStructureHandler)
], debug=True)