from google.appengine.ext import ndb
from google.appengine.api import memcache
import webapp2
import json
import os
import jinja2
import smtplib
import cgi
import textwrap
import urllib



JINJA_ENV = jinja2.Environment(
 loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MM(ndb.Model):
     name = ndb.StringProperty(required = True)
     email = ndb.StringProperty()
     manager = ndb.IntegerProperty()


class Worker(ndb.Model):
     name = ndb.StringProperty(required = True)
     email = ndb.StringProperty()
     manager = ndb.IntegerProperty()


class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    username = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    signature = ndb.IntegerProperty()


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



class UserHandler2(webapp2.RequestHandler):
    # user has signed in, and is a confirmed user
    def get(self, username=None):
        if username:
            # set the user to username
            #user = users.User(username)

            # set the memcache user to username


            query = User.query(User.username == username).get()
            q_d = query.to_dict()
            self.response.write(json.dumps(q_d))

            # create a dictionary we will use in our templates
            template_vars = {
            "name" : q_d['name'],# or username?? which to pick
            "user" :  memcache.get(key='user')
            }

            emailResult = ""
            try:
                # test sending out email
                FROM = "kbonnie@gmail.com"
                TO = ['kbonnie@gmail.com'] # must be list
                SUBJECT = "HELLO FROM APP"
                TEXT = "Need to feed the cat"
                username = "kbonnie@gmail.com"
                password = ''   ### always remove the password ############################
                server = smtplib.SMTP('smtp.gmail.com:587')
                server.ehlo()
                server.starttls()
                server.login(username,password)
                server.sendmail(FROM, TO, TEXT)
                server.quit()
                emailResult = "success"
            except Exception, e:
                emailResult = "failed to email"

            template_vars['emailResult'] = emailResult

            get_user_query_results = [get_user_query.to_dict()
                                          for get_user_query in MM.query()]

            template_vars['allMM'] = get_user_query_results


            template = JINJA_ENV.get_template('home.html')
            self.response.out.write(template.render(template_vars))

class SignIn(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENV.get_template('signIn.html')
        # controller tells to render the index.html template
        self.response.out.write(template.render())

    def post(self):
        # verify that username and password are correct

        username = self.request.get("username")
        password = self.request.get("password")
        query = User.query(User.username== username).fetch()

        # set the user into memcache
        memcache.flush_all()
        memcache.add(key='user', value = self.request.get("username"))

        if query:
            # user was found. redirect to his/her page
            self.redirect("/user/" + username)
        else:
            self.response.write("Not found")

        #self.redirect("/users")

class Worker(webapp2.RequestHandler):
    def post(self):
        e = MM()
        e.name = self.request.get("name")
        e.email = self.request.get("email")
        e.manager = memcache.get(key='user')  # set manager to current logged
        #in user
        e.put()
        #name = self.request.get("name")
        # = self.request.get("email")
        #manager = 44
        #e.manager = user.get_current_user() # from current user session
        #new_worker = Worker(name=name, email=email)
        #new_worker.put() # put it into the ndb store
        self.redirect("/user/" + memcache.get(key='user') )


#   FOR DEBUGGING ONLY
class Workers(webapp2.RequestHandler):
    def get(self,id=None):
        #get_user_query_results = [get_user_query.to_dict() for get_user_query in Worker.query()]
        get_user_query_results = [get_user_query.to_dict()
                                      for get_user_query in MM.query()]
        self.response.write(json.dumps(get_user_query_results))  # display results to user


class Logout(webapp2.RequestHandler):
    def get(self):
        # to logout, clear the memcache which stored the user
        memcache.flush_all()
        # redirect user to the home page
        self.redirect("/")



app = webapp2.WSGIApplication([

    ('/', MainPage),
    ('/createUser', CreateUser),
    ('/signIn', SignIn),
    ('/users', UserHandler),
    ('/user/(.*)', UserHandler2),
    ('/workers', Workers),
    ('/worker', Worker),
    ('/logout', Logout)

], debug=True)
