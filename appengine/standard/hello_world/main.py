from google.appengine.ext import ndb
import webapp2
import json



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

# This updates Slip's arrival_date
class SlipHandler2(webapp2.RequestHandler):
    def put(self, id=None):
        s = ndb.Key(urlsafe=id).get()
        slip_data = json.loads(self.request.body)
        s.arrival_date = slip_data['arrival_date']
        s.put()
        self.response.write("wonky")

# updates a slip's boat name and arrival
# put /slip/slip_id/putboat
# {'name' ; "some name", 'arrival_date': "some date"}
class SlipHandler3(webapp2.RequestHandler):
    def put(self, id=None):
        s = ndb.Key(urlsafe=id).get()
        slip_data = json.loads(self.request.body)
        #s.current_boat = Boat("jasmine")
        #s.current_boat = "jasminefoo" # line that breaks
        s.current_boat = slip_data['name']
        s.arrival_date = slip_data['arrival_date']
        s.put()

        # also the boat you put in the slip should not be at sea
        b = ndb.Key(urlsafe=s.current_boat).get() # this should get the boat
        b.at_sea = False  # change to at_sea is False
        b.put()
        self.response.write("you changed the boat in the slip")

class SlipHandler(webapp2.RequestHandler):
    def post(self, id=None):
        slip_data = json.loads(self.request.body)
        new_slip = Slip(number=slip_data['number'])
        new_slip.put()
        slip_dict = new_slip.to_dict()
        slip_dict['self'] = '/slip/' + new_slip.key.urlsafe()
        self.response.write(json.dumps(slip_dict))

    # to delete a slip /slip/slip_id/
    # make it so that if a slip is occupied
    # that the boat becomes 'at_sea' = true
    def delete(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            s_d = s.to_dict()
            #s_d['self'] = "/slip/" + id
            #self.response.write(s_d)
            if s.current_boat != None:   ##### OMG its NOne not null. stupid!
                #boat_data = json.loads(self.request.body) # get the boat data
                b = ndb.Key(urlsafe=s.current_boat).get() # this should get the boat
                b.at_sea = True  # change to at_sea is true
                b.put()
                s.key.delete() # this deletes the slip
                self.response.write(id)


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

# this class for boat handles (2) move boat to the sea
# and free up the slip
class BoatHandler2(webapp2.RequestHandler):
    def put(self, id=None):
        # this changes the boat to the sea
        if id:
            b = ndb.Key(urlsafe=id).get()
            if b.at_sea == False:
                b.at_sea = True # set to true, moved boat to the sea
                b.put()
                self.response.write("moved boat to the sea")
            else:
                self.response.write("boat already at sea")


class BoatHandler(webapp2.RequestHandler):
    def post(self):
        boat_data = json.loads(self.request.body)
        #new_boat = Boat(name=boat_data['name'], length=boat_data['length'])
        if 'type' not in boat_data:
            if 'length' not in boat_data:
                # means name only in data
                new_boat = Boat(name=boat_data['name'])
            else:
                # means name + length
                new_boat = Boat(name=boat_data['name'], length=boat_data['length'])
        elif 'length' not in boat_data:
            # name + type
            new_boat = Boat(name=boat_data['name'], type=boat_data['type'])
        else:
            # name + type + length
            new_boat = Boat(name=boat_data['name'], type=boat_data['type'], length=boat_data['length'])


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

    # for boat to change at_sea
    # have to use {"at_sea": false}  Note the small f Python uses F
    #  need to update so that putting boat at_sea empties out the slip
    def put(self, id=None):
        boat_data = json.loads(self.request.body)
        if id:
            b = ndb.Key(urlsafe=id).get()
            if boat_data['at_sea'] == False:
                b.at_sea = False
                b.put()
            elif boat_data['at_sea'] == True:
                b.at_sea = True
                b.put()
            #b.at_sea = boat_data['at_sea']
            #b.put()
            self.response.write("you updated at sea to ")


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


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


app = webapp2.WSGIApplication([

    ('/fish', FishHandler),
    ('/fish/(.*)', FishHandler),
    ('/boat/(.*)/tosea', BoatHandler2),
    ('/boat/(.*)', BoatHandler),
    ('/boat', BoatHandler),
    ('/slip/(.*)/date', SlipHandler2),
    ('/slip/(.*)/putboat', SlipHandler3),
    ('/slip', SlipHandler),
    ('/slip/(.*)', SlipHandler),
    ('/', MainPage),

], debug=True)
