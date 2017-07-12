from google.appengine.ext import ndb
import webapp2
import json

class Fish(ndb.Model):
    name = ndb.StringProperty(required=True)
    numFriends = ndb.IntegerProperty()


class FishHandler(webapp2.RequestHandler):
    def post(self):
        fish_data = json.loads(self.request.body)
        new_fish = Fish(name=fish_data['name'])
        new_fish.put()
        self.response.write(json.dumps(new_fish.to_dict()))


    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('There are some fish')

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/fish', FishHandler),
], debug=True)
