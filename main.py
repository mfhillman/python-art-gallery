import webapp2

from home import HomeHandler

app = webapp2.WSGIApplication([
    ('/', HomeHandler)
], debug=True)