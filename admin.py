import datetime
import os

import webapp2

from google.appengine.api import users

from models import Painting, Gallery
		
class AdminHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.response.write('You are an administrator.')
            else:
                self.response.write('You are not an administrator.')
        else:
            self.response.write('You are not logged in.')
            
class AdminResumeHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('You are at the resume handler.<br>')
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.response.write('You are an administrator.')
            else:
                self.response.write('You are not an administrator.')
        else:
            self.response.write('You are not logged in.')
		
app = webapp2.WSGIApplication([
    ('/admin', AdminHandler),
    ('/admin/resume', AdminResumeHandler),
], debug=True)