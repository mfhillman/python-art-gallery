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
  
def UnicodeDictReader(utf8_data, **kwargs):
  csv_reader = csv.DictReader(utf8_data, **kwargs)
  for row in csv_reader:
    yield {unicode(key, 'utf-8'):unicode(value, 'utf-8') for key, value in row.iteritems()}

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

class EditGalleriesHandler(webapp2.RequestHandler):
  def get(self):
   
    gallery_keys = GalleryList.get_by_id('galleries').gallery_keys
    galleries = ndb.get_multi(gallery_keys)
    archive_keys = GalleryList.get_by_id('archives').gallery_keys
    archives = ndb.get_multi(archive_keys)
    
    gallery_strs = []
    for gallery in galleries:
      gallery_strs.append(','.join([gallery.url_fragment(), gallery.name]))
    main_galleries_text = '\n'.join(gallery_strs)

    archive_strs = []
    for gallery in archives:
      archive_strs.append(','.join([gallery.url_fragment(), gallery.name]))
    archive_galleries_text = '\n'.join(archive_strs)
    
    orphan_strs = []
    orphans = self.get_orphan_galleries(gallery_keys + archive_keys)
    for gallery in orphans:
      orphan_strs.append(','.join([gallery.url_fragment(), gallery.name]))
    orphan_galleries_text = '\n'.join(orphan_strs)
    
    template_values = {
        'main_galleries_text': main_galleries_text,
        'archive_galleries_text': archive_galleries_text,
        'orphans_galleries_text': orphan_galleries_text
    }

    template = JINJA_ENVIRONMENT.get_template('admin_edit_galleries.html')
    self.response.write(template.render(template_values))
    
  def get_orphan_galleries(self, listed_keys):
    orphans = []
    all_galleries = Gallery.query().fetch()
    
    for gallery in all_galleries:
      if gallery.key not in listed_keys:
        orphans.append(gallery)
        
    return orphans
    
class UpdateGalleriesHandler(webapp2.RequestHandler):
  def post(self, pool_name):
    # Content is one gallery per line: id, name.
    # When saving gallery lists, name is ignored
    new_galleries_content = self.request.get('content')
    new_galleries_list = string.split(new_galleries_content, '\n')
    
    gallery_list = GalleryList(id=pool_name)
    gallery_list.gallery_keys = []
    for gal in new_galleries_list:
      gal_id = string.split(gal, ',')[0]
      gallery_list.gallery_keys.append(ndb.Key(Gallery, gal_id))

    gallery_list.save()
    
    self.redirect('/admin/confirm')

class NavToGalleryHandler(webapp2.RequestHandler):
  def post(self):
    gallery_id_content = self.request.get('content')
    self.redirect('/admin/edit_gallery/' + gallery_id_content)

class EditGalleryHandler(webapp2.RequestHandler):
  def get(self, gallery_id): 
    if gallery_id.isdigit():
      gallery = Gallery.get_by_id(gallery_id)
      paintings = ndb.get_multi(gallery.painting_keys)
    else:
      gallery_id = self.get_fresh_id()
      gallery = Gallery(id=gallery_id)      
      paintings = []
      
    painting_strs = []
    for painting in paintings:
      painting_strs.append(','.join([painting.title,str(painting.height),
                                     str(painting.width),painting.key.id()]))
    painting_text = '\n'.join(painting_strs)

    template_values = {
        'gallery': gallery,
        'paintings_text': painting_text
    }

    template = JINJA_ENVIRONMENT.get_template('admin_edit_gallery.html')
    self.response.write(template.render(template_values))

  def get_fresh_id(self):
    all_galleries = Gallery.query().fetch()
    sorted_galleries = sorted(all_galleries, key=lambda gal: int(gal.key.id()))
        
    return int(sorted_galleries[len(sorted_galleries)-1].key.id()) + 1;

class UpdateGalleryHandler(webapp2.RequestHandler):
  def post(self):
    gallery = Gallery(id=self.request.get('gallery_id'),
        name=self.request.get('gallery_name'),
        front_painting_id=self.request.get('front_painting_id'))
        
    # Note that columns are expected to be title, height, width, id
    painting_strs = string.split(self.request.get('paintings_text'), '\n')
 
    paintings = []
    for painting_str in painting_strs:
      row = string.split(painting_str, ',')
      painting = Painting(
          id=string.strip(row[3]),
          title=string.strip(row[0]), 
          height=int(row[1]) if row[1] else 0,
          width=int(row[2]) if row[2] else 0)  
      paintings.append(painting)
      gallery.painting_keys.append(painting.key)
      
    self.response.write('painting count ' + str(len(paintings)) + '<BR>')
    
    # Write back only changed paintings
    changed_paintings = []
    old_paintings = ndb.get_multi(gallery.painting_keys)
    
    for i in range(0, len(old_paintings)):
      old = old_paintings[i]
      new = paintings[i]
      if old == None or len(old.base_image_url) == 0 or (old.title != new.title or old.height != new.height or old.width != new.width):
        if old != None and len(old.base_image_url) > 0:
          new.base_image_url = old.base_image_url
        else:
          new.set_base_image_url()
        changed_paintings.append(new)
          
    if len(changed_paintings) > 0:
      self.response.write(changed_paintings)
      ndb.put_multi(changed_paintings)
    else:
      self.response.write('<BR> no changed paintings!<BR>')
      
    self.response.write('<BR>' + str(gallery) + '<BR>')
    gallery.save()

class PaintingCsvHandler(webapp2.RequestHandler):
  def get(self):
    with open('csvs/paintings.csv') as csvfile:
      reader = UnicodeDictReader(csvfile)
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
    with open('csvs/galleries.csv') as csvfile:
      reader = UnicodeDictReader(csvfile)
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
        
class GalleriesAndEntriesHandler(webapp2.RequestHandler):
  def get(self):
    painting_map = {}
    gallery_map = {}
    galleries = []
    sorted_gallery_entries = []

    # Map Painting IDs to ImageBaseName, which is the new id
    with open('csvs/paintings.csv') as csvfile:
      reader = UnicodeDictReader(csvfile)
      for row in reader:
        painting_map[row['PaintingID']] = row['ImageBaseName']

    # Read galleries, build basic entities, map to id.
    with open('csvs/galleries.csv') as csvfile:
      reader = UnicodeDictReader(csvfile)
      for row in reader:
        front_painting = painting_map[row['FrontPaintingID']]
        gallery = Gallery(
            id=row['GalleryID'],
            name=row['GalleryName'],
            front_painting_id=painting_map[row['FrontPaintingID']])
        galleries.append(gallery)
        gallery_map[row['GalleryID']] = gallery
        
    # Sort Gallery Entries by Ordering
    with open('csvs/gallery_entries.csv') as csvfile:
      reader = UnicodeDictReader(csvfile)
      sorted_gallery_entries = sorted(reader, key=lambda row: int(row['Ordering']))

    # Loop through gallery entries, adding keys to galleries
    for entry in sorted_gallery_entries:
      gallery = gallery_map[entry['GalleryID']]
      painting_id = painting_map[entry['PaintingID']]
      key = ndb.Key(Painting, painting_id)
      gallery.painting_keys.append(key)

    # Write galleries!
    ndb.put_multi(galleries)
    
    self.response.write('Done yo.')

class FixGalleryHandler(webapp2.RequestHandler):
  def get(self, gallery_id):

    year = datetime.datetime.now().year
    if gallery_id.isdigit():
      gallery = Gallery.get_by_id(gallery_id)
    else:
      gallery = None
    if gallery:
      self.response.write('Got a gallery.')
      self.response.write('<BR>' + str(gallery) + '<BR>')
    else:
      self.response.write('No gallery bub.')

class FixPaintingUrlsHandler(webapp2.RequestHandler):
  def get(self, start_str):
    interval = 25
    start = int(start_str)
    paintings = []
    
    with open('csvs/paintings.csv') as csvfile:
      reader = UnicodeDictReader(csvfile)
      i = 0
      for row in reader:
        if i >= start and i < (start + interval):
          painting = Painting(
              id=row['ImageBaseName'],
              title=row['Title'], 
              width=int(row['WidthInches']) if row['WidthInches'] else 0,
              height=int(row['HeightInches']) if row['HeightInches'] else 0,
              old_id=int(row['PaintingID']))
          painting.set_base_image_url()
          paintings.append(painting)
        i = i + 1

    ndb.put_multi(paintings)

    template = JINJA_ENVIRONMENT.get_template('fix_painting_urls.html')
    if len(paintings) == 25:
      redirect = str(start + interval)
    else:
      redirect = ''
    self.response.out.write(template.render(
        start = str(start), redirect = redirect, paintings = paintings))
        
class FixSpecificPaintingUrlHandler(webapp2.RequestHandler):
  def get(self, name):
    paintings = []
    
    with open('csvs/paintings.csv') as csvfile:
      reader = UnicodeDictReader(csvfile)
      for row in reader:
        if row['ImageBaseName'] == name:
          painting = Painting(
              id=row['ImageBaseName'],
              title=row['Title'], 
              width=int(row['WidthInches']) if row['WidthInches'] else 0,
              height=int(row['HeightInches']) if row['HeightInches'] else 0,
              old_id=int(row['PaintingID']))
          painting.set_base_image_url()
          paintings.append(painting)

    ndb.put_multi(paintings)

    template = JINJA_ENVIRONMENT.get_template('fix_painting_urls.html')
    if len(paintings) == 25:
      redirect = str(start + interval)
    else:
      redirect = ''
    self.response.out.write(template.render(
        start = 0, redirect = '', paintings = paintings))
        
app = webapp2.WSGIApplication([
    ('/admin', AdminHandler),
    ('/admin/confirm', ConfirmHandler),
    ('/admin/update_exhibitions', UpdateExhibitionsHandler),
    ('/admin/update_honors', UpdateHonorsHandler),
    ('/admin/update_schools', UpdateSchoolsHandler),
    ('/admin/edit_galleries', EditGalleriesHandler),
    ('/admin/update_galleries/(galleries|archives)', UpdateGalleriesHandler),
    ('/admin/nav_to_gallery', NavToGalleryHandler),
    ('/admin/edit_gallery/([^/]+)', EditGalleryHandler),
    ('/admin/update_gallery', UpdateGalleryHandler),
    ('/admin/painting_csv', PaintingCsvHandler),
    ('/admin/gallery_structure', GalleryStructureHandler),
    ('/admin/galleries_and_entries', GalleriesAndEntriesHandler),
    ('/admin/fix_gallery/([^/]+)', FixGalleryHandler),
    ('/admin/fix_painting_urls/([^/]+)', FixPaintingUrlsHandler),
    ('/admin/fix_specific_painting_url/([^/]+)', FixSpecificPaintingUrlHandler)
], debug=True)