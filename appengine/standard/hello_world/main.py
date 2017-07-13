from google.appengine.ext import ndb
import webapp2
import json




class Boat(ndb.Model):
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty()
    length = ndb.IntegerProperty()
    at_sea = ndb.BooleanProperty(default=True)

class Slip(ndb.Model):
    number = ndb.IntegerProperty()
    current_boat = ndb.StructuredProperty(Boat)
    arrival_date = ndb.StringProperty()


class Fish(ndb.Model):
    name = ndb.StringProperty(required=True)
    numFriends = ndb.IntegerProperty()


class SlipHandler2(webapp2.RequestHandler):
    def put(self, id=None):
        s = ndb.Key(urlsafe=id).get()
        slip_data = json.loads(self.request.body)
        s.arrival_date = slip_data['arrival_date']
        s.put()
        self.response.write("wonky")

class SlipHandler(webapp2.RequestHandler):
    def post(self, id=None):
        slip_data = json.loads(self.request.body)
        new_slip = Slip(number=slip_data['number'], arrival_date=slip_data['arrival_date'])
        new_slip.put()
        slip_dict = new_slip.to_dict()
        slip_dict['self'] = '/slip/' + new_slip.key.urlsafe()
        self.response.write(json.dumps(slip_dict))


    def delete(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            s_d = s.to_dict()
            #s_d['self'] = "/slip/" + id
            #self.response.write(s_d)
            s.key.delete()

        else:
            self.response.write("You cannot delete a slip with no id")


    def get(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            s_d = s.to_dict()
            s_d['self'] = "/slip/" + id
            #self.response.write(s.key())
            self.response.write(json.dumps(s_d))
        else:

            #results = Slip.query().fetch()
            get_slip_query_results = [get_slip_query.to_dict()
                                      for get_slip_query in Slip.query()]

            self.response.write(json.dumps(get_slip_query_results))




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
            get_boat_query_results = [get_boat_query.to_dict()
                                      for get_boat_query in Boat.query()]

            self.response.write(json.dumps(get_boat_query_results))

    def delete(self, id=None):
        if id:
            b = ndb.Key(urlsafe=id).get()
            b_d = b.to_dict()
            b.key.delete()

        else:
            self.response.write("You cannot delete a Boat with no id")


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
    ('/slip/(.*)/date', SlipHandler2),
    ('/slip', SlipHandler),
    ('/slip/(.*)', SlipHandler),

], debug=True)
