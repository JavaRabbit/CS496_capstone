from google.appengine.ext import ndb
import webapp2
import json
import os
import jinja2

JINJA_ENV = jinja2.Environment(
 loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    signature = ndb.IntegerProperty()


'''

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

class CreateUser(webapp2.RequestHandler):
    def get(self):
        # set the view to be index.html found in folder templates
        template = JINJA_ENV.get_template('createUser.html')
        # controller tells to render the index.html template
        self.response.out.write(template.render())

    def post(self):
        #new_user = User(name="alpha", username = "alpha_username", password = "password")
        username = self.request.get("username")
        realname = self.request.get("realname")
        password = self.request.get("password")
        email = self.request.get("email")
        new_user = User(name=realname, username = username, password = password, email = email)
        new_user.put() # put it into the ndb store

        # for now, route to all users
        self.redirect("/users")

# for debugging purposes only
class UserHandler(webapp2.RequestHandler):
    def get(self, id=None):
        #r get all users
        get_user_query_results = [get_user_query.to_dict()
                                      for get_user_query in User.query()]
        self.response.write(json.dumps(get_user_query_results))  # display results to user

class SignIn(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENV.get_template('signIn.html')
        # controller tells to render the index.html template
        self.response.out.write(template.render())

    #def post(self):
        # verify that username and password are correct

app = webapp2.WSGIApplication([

    #('/fish', FishHandler),
    #('/fish/(.*)', FishHandler),

    ('/', MainPage),
    ('/createUser', CreateUser),
    ('/signIn', SignIn),
    ('/users', UserHandler)

], debug=True)
