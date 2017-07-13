from google.appengine.ext import ndb
import webapp2
import json


class Boat(ndb.Model):
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty()
    length = ndb.IntegerProperty()
    at_sea = ndb.BooleanProperty(default=True)


class Fish(ndb.Model):
    name = ndb.StringProperty(required=True)
    numFriends = ndb.IntegerProperty()

class BoatHandler(webapp2.RequestHandler):
    def post(self):
        boat_data = json.loads(self.request.body)
        new_boat = Boat(name=boat_data['name'])
        new_boat.put()
        boat_dict = new_boat.to_dict()
        boat_dict['self'] = '/boat/' + new_boat.key.urlsafe()
        self.response.write(json.dumps(boat_dict))


    def get(self, id=None):
        if id:
            b = ndb.Key(urlsafe=id).get()
            b_d = b.to_dict()
            b_d['self'] = "/boat/" + id
            self.response.write(json.dumps(b_d))
        else:
            self.response.write("There are no boats")
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.write('There are some fish')





class FishHandler(webapp2.RequestHandler):
    def post(self):
        fish_data = json.loads(self.request.body)
        new_fish = Fish(name=fish_data['name'])
        new_fish.put()
        fish_dict = new_fish.to_dict()
        fish_dict['self'] = '/fish/' + new_fish.key.urlsafe()
        self.response.write(json.dumps(fish_dict))


    def get(self, id=None):
        if id:
            f = ndb.Key(urlsafe=id).get()
            f_d = f.to_dict()
            f_d['self'] = "/fish/" + id
            self.response.write(json.dumps(f_d))
        else:
            self.response.write("There are no fish")
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.write('There are some fish')

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/fish', FishHandler),
    ('/fish/(.*)', FishHandler),
    ('/boat', BoatHandler),
    ('/boat/(.*)', BoatHandler),
], debug=True)
