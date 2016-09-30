from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import ndb

_PAINTING_BUCKET = 'mfh-art-gallery.appspot.com'
_PAINTING_FORMAT = '/gs/' + _PAINTING_BUCKET + '/artwork-images/{0}.jpg'

class Painting(ndb.Model):
	file_name = ndb.StringProperty(indexed = False)
	title = ndb.StringProperty(indexed = False)
	width = ndb.IntegerProperty()
	height = ndb.IntegerProperty()
	
	def _image_path(self) :
		return _PAINTING_FORMAT.format(self.file_name)

	def _blob_key(self) :
		return blobstore.create_gs_key(self._image_path());
		
	def _base_image(self) :
		return images.get_serving_url(self._blob_key())
	
	def full_size_image(self) :
		return self._base_image() + '=s0'
		
	def thumbnail_image(self) :
		return self._base_image() + '=s165'
