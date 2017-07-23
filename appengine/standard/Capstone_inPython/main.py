from google.appengine.ext import ndb
import webapp2
import json
import os
import jinja2

JINJA_ENV = jinja2.Environment(
 loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

'''
class Boat(ndb.Model):
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty()
    length = ndb.IntegerProperty()
    at_sea = ndb.BooleanProperty(default=True)

class Slip(ndb.Model):
    number = ndb.IntegerProperty(required=True)
    #current_boat = ndb.StructuredProperty(Boat)
    current_boat = ndb.StringProperty()
    arrival_date = ndb.StringProperty()


class Fish(ndb.Model):
    name = ndb.StringProperty(required=True)
    numFriends = ndb.IntegerProperty()



'''

class MainPage(webapp2.RequestHandler):
    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'

        # set the view to be index.html found in folder templates
        template = JINJA_ENV.get_template('index.html')
        # controller tells to render the index.html template
        self.response.out.write(template.render())



app = webapp2.WSGIApplication([

    #('/fish', FishHandler),
    #('/fish/(.*)', FishHandler),

    ('/', MainPage)

], debug=True)
