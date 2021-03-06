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
class SlipHandlerBoat(webapp2.RequestHandler):
    def put(self, id=None):
        try:
            s = ndb.Key(urlsafe=id).get()
            slip_data = json.loads(self.request.body)

            if s.current_boat == None:

                s.current_boat = slip_data['name']
                s.arrival_date = slip_data['arrival_date']
                s.put()

                # also the boat you put in the slip should not be at sea
                b = ndb.Key(urlsafe=s.current_boat).get() # this should get the boat
                b.at_sea = False  # change to at_sea is False
                b.put()
                self.response.write("you changed the boat in the slip")
            else:
                self.error(403)  # send reponse 403
                self.response.write("Sorry, slip is already occupied")
        except Exception, e:
            self.response.write("Not a valid slip id. Try again.")

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
            try:
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
                    # there is no boat, but delete the slip anyways
                    s.key.delete()
            except Exception, e:
                self.response.write("Invalid SLIP id")
        else:
            self.response.write("You cannot delete a slip with no id")


    def get(self, id=None):
        if id:
            try:
                s = ndb.Key(urlsafe=id).get()
                s_d = s.to_dict()
                s_d['self'] = "/slip/" + id
                self.response.write(json.dumps(s_d))
            except Exception, e:
                self.response.write("Not a valid Slip id")
        else:

            #results = Slip.query().fetch()
            get_slip_query_results = [get_slip_query.to_dict()
                                      for get_slip_query in Slip.query()]

            self.response.write(json.dumps(get_slip_query_results))

    #  This PUT method will allow user to update slip number
    def put(self, id=None):
        slip_data = json.loads(self.request.body)
        s = ndb.Key(urlsafe=id).get()
        s_d = s.to_dict()
        s_d['number'] = slip_data['number'] # reassign the number
        s.number = slip_data['number']
        s.put()
        self.response.write(json.dumps(s_d))

class BoatHandler2(webapp2.RequestHandler):
    #  PUT /boat/{boat_id}/boat  allows users to modify a boat
    def put(self, id=None):
        boat_data = json.loads(self.request.body)
        b = ndb.Key(urlsafe=id).get()
        b_d = b.to_dict()

        if 'name' in boat_data:
            b_d['name'] = boat_data['name']
            b.name = boat_data['name']
        if 'type' in boat_data:
            b_d['type'] = boat_data['type']
            b.type = boat_data['type']
        if 'length' in boat_data:
            b_d['length'] = boat_data['length']
            b.length = boat_data['length']
        b.put()
        self.response.write(json.dumps(b_d))


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

            try:
                b = ndb.Key(urlsafe=id).get()
                b_d = b.to_dict()
                b_d['self'] = "/boat/" + id
                self.response.write(json.dumps(b_d))
            except Exception, e:
                self.response.write("Not a valid Boat id")

        else:
            get_boat_query_results = [get_boat_query.to_dict()
                                      for get_boat_query in Boat.query()]

            self.response.write(json.dumps(get_boat_query_results))

    def patch(self):
        self.response.write("this is patch")

    def delete(self, id=None):
        if id:
            try:
                b = ndb.Key(urlsafe=id).get()
                b_d = b.to_dict()
                b.key.delete()

                # we deleted the boat, now empty the slip
                # get all the slips into a variable
                get_slip_query_results = [get_slip_query.to_dict()
                                          for get_slip_query in Slip.query()]

                urlstr = b.key.urlsafe()
                if  any(d['current_boat'] == urlstr for d in get_slip_query_results):
                    qu = Slip.query(Slip.current_boat == urlstr).fetch()
                    res = qu[0]
                    theSlip = Slip.get_by_id(res.key.id())
                    theSlip.current_boat = None
                    theSlip.arrival_date = None
                    theSlip.put()
                    self.response.write(b_d['name'])
                else:
                    self.response.write("The deleted boat is not in a slip")
            except Exception, e:
                self.response.write("Invalid Boat ID")
        else:
            self.response.write("You cannot delete a Boat with no id")

    # method to move a boat to "at_sea"
    #
    # updates so that putting boat at_sea empties out the slip
    def put(self, id=None):
        # this changes the boat to the sea
        try:
            if id:
                b = ndb.Key(urlsafe=id).get()
                if b.at_sea == False:
                    b.at_sea = True # set to true, moved boat to the sea
                    b.put()

                    # get all the slips into a variable
                    get_slip_query_results = [get_slip_query.to_dict()
                                              for get_slip_query in Slip.query()]
                    urlstr = b.key.urlsafe()
                    if  any(d['current_boat'] == urlstr for d in get_slip_query_results):
                        qu = Slip.query(Slip.current_boat == urlstr).fetch()
                        res = qu[0]
                        theSlip = Slip.get_by_id(res.key.id())
                        theSlip.current_boat = None
                        theSlip.arrival_date = None
                        theSlip.put()
                        self.response.write(json.dumps(b.to_dict()))
                        #self.response.write("Slip foudn and changed")
                    else:
                        self.response.write("No slip found for that ship")
                else:
                    self.response.write("boat already at sea")
        except Exception, e:
            self.response.write("Not a valid boat id.")


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
    ('/boat/(.*)/boat', BoatHandler2),
    ('/boat/(.*)', BoatHandler),
    ('/boat', BoatHandler),
    ('/slip/(.*)/date', SlipHandler2),
    ('/slip/(.*)/boat', SlipHandlerBoat),
    ('/slip', SlipHandler),
    ('/slip/(.*)', SlipHandler),
    ('/', MainPage),

], debug=True)
