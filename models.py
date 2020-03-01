import string

from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import ndb

_PAINTING_BUCKET = 'mfh-art-gallery.appspot.com'
_PAINTING_FORMAT = '/gs/' + _PAINTING_BUCKET + '/artwork-images/{0}.jpg'

_RESUME_KEY_LOCATION = 'resume'

class Painting(ndb.Model):
  # file name is stored in id
  title = ndb.StringProperty(indexed=False)
  base_image_url = ndb.StringProperty(indexed=False)
  width = ndb.IntegerProperty(indexed=False)
  height = ndb.IntegerProperty(indexed=False)
  old_id = ndb.IntegerProperty(indexed=True)
  
  def set_base_image_url(self) :
    try:
      self.base_image_url = self._base_image()
    except images.ObjectNotFoundError:
      self.base_image_url = ''

  def clear_base_image_url(self) :
      try:
        images.delete_serving_url(self._blob_key())
      except images.ObjectNotFoundError:
      
      self.base_image_url = ''

  def _image_path(self) :
    return _PAINTING_FORMAT.format(self.key.id())

  def _blob_key(self) :
    return blobstore.create_gs_key(self._image_path());
		
  def _base_image(self) :
    return images.get_serving_url(self._blob_key())
	
  def full_size_image(self) :
    return self.base_image_url + '=s0'
	
  def thumbnail_image(self) :
    return self.base_image_url + '=s165'
    
  def url_fragment(self) :
    return self.key.id()
    
  @classmethod
  def get_from_old_id(cls, old_id):
    query = cls.query(cls.old_id == old_id)
    results = query.fetch(1)
    if len(results) > 0:
      return results[0]
    else:
      return None
		
class Gallery(ndb.Model):
  name = ndb.StringProperty(indexed=False)
  front_painting_id = ndb.StringProperty(indexed=False)
  painting_keys = ndb.KeyProperty(repeated=True)
  
  def url_fragment(self) :
    return self.key.id()
    
  def save(self) :
    history_entry = GalleryHistory(gallery=self)
    self.put()
    history_entry.put()
    
class GalleryHistory(ndb.Model):
  gallery = ndb.StructuredProperty(Gallery)
  date = ndb.DateTimeProperty(auto_now_add=True)
    
class GalleryList(ndb.Model):
  gallery_keys = ndb.KeyProperty(repeated=True)
  
  def save(self) :
    history_entry = GalleryListHistory(gallery_list=self, pool_name=self.key.id())
    self.put()
    history_entry.put()

class GalleryListHistory(ndb.Model):
  pool_name = ndb.StringProperty(indexed = False)
  gallery_list = ndb.StructuredProperty(GalleryList)
  date = ndb.DateTimeProperty(auto_now_add=True)
  
class SchoolInfo(ndb.Model):
  school = ndb.StringProperty(indexed=False)
  school_detail = ndb.StringProperty(indexed=False)
  
  def to_admin_str(self):
    if self.school_detail:
      return self.school + '|' + self.school_detail
    else:
      return self.school
      
  def from_admin_str(self, str):
    strs = string.split(str, '|')
    self.school = strs[0]
    if len(strs) > 1:
      self.school_detail = strs[1]
    else:
      self.school_detail = ''

class ResumeInfo(ndb.Model):
  exhibitions = ndb.StringProperty(repeated=True)
  honors = ndb.StringProperty(repeated=True)
  schools = ndb.StructuredProperty(SchoolInfo, repeated=True)
  
  @classmethod
  def retrieve(cls) :
    return cls.get_or_insert(_RESUME_KEY_LOCATION)
    
  def save(self) :
    history_entry = ResumeHistory(resume=self)
    self.put()
    history_entry.put()
  
class ResumeHistory(ndb.Model):
  resume = ndb.StructuredProperty(ResumeInfo)
  date = ndb.DateTimeProperty(auto_now_add=True)
