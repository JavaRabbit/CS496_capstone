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

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.mime.application import MIMEApplication



JINJA_ENV = jinja2.Environment(
 loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MM(ndb.Model):
     name = ndb.StringProperty(required = True)
     email = ndb.StringProperty()
     manager = ndb.StringProperty()

# actually not using this class.
# employee is actually MM
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

# not using award since it wouldn't query
class Award(ndb.Model):
    recipient = ndb.StringProperty(required=True)
    manager = ndb.StringProperty()
    type = ndb.StringProperty(required=True)
    date = ndb.DateProperty()



class Award2(ndb.Model):
    recipient = ndb.StringProperty(required=True)
    manager = ndb.StringProperty()
    type = ndb.StringProperty(required=True)
    date = ndb.DateProperty()


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

        # for now, route to sign in page
        self.redirect("/signIn")

# for debugging purposes only
class UserHandler(webapp2.RequestHandler):
    def get(self, id=None):
        # get all users
        get_user_query_results = [get_user_query.to_dict()
                                      for get_user_query in User.query()]
        self.response.write(json.dumps(get_user_query_results))  # display results to user


class UserHandler2(webapp2.RequestHandler):

    def delete(self, id=None):
        if id:
            try:
                query = User.query(User.username == id).get()

                query.key.delete()
                self.response.write("User deleted sucessfully.")

            except Exception, e:
                self.response.write("Invalid User username")
        else:
            self.response.write("You cannot delete a User with no id")

    # user has signed in, and is a confirmed user
    # this will route to home.html view
    def get(self, username=None):
        if username:
            # set the user to username
            #user = users.User(username)

            # set the memcache user to username
            query = User.query(User.username == username).get()
            q_d = query.to_dict()
            #self.response.write(json.dumps(q_d))

            # create a dictionary we will use in our templates
            template_vars = {
            "name" : q_d['name'],# or username?? which to pick
            "user" :  memcache.get(key='user')
            }


            # Query the database for all 'employees' whose manager is current loggedin user
            get_user_query_results = [get_user_query.to_dict()
                                          for get_user_query in MM.query(MM.manager == memcache.get(key='user'))]

            template_vars['allMM'] = get_user_query_results


            # Query the database for all 'awards' whose manager is current logged in user
            award_results = [get_user_query.to_dict()
                                          for get_user_query in Award2.query(Award2.manager == memcache.get(key='user'))]

            template_vars['allAwards'] = award_results


            template = JINJA_ENV.get_template('home.html')
            self.response.out.write(template.render(template_vars))

class MyAccount(webapp2.RequestHandler):
    def get(self, id=None):
        template_vars = {

        "user" :  memcache.get(key='user')
        }

        query = User.query(User.username == memcache.get(key='user')).get()
        q_d = query.to_dict()
        template_vars['stuff'] = q_d

        template = JINJA_ENV.get_template('myaccount.html')
        self.response.out.write(template.render(template_vars))

    # method for updating user account settings
    # try catch? if exists
    def post(self, id=None):
        try:
            query = User.query(User.username == memcache.get(key='user')).get()
            query.name = self.request.get("name")
            query.email = self.request.get("email")
            query.put()

            # go back to users home page
            self.redirect("/user/" + memcache.get(key='user') )
        except Exception, e:
            self.redirect("/")

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

        self.redirect("/user/" + memcache.get(key='user') )
        # fix above. if 'user is empty', redirect to '/'


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

class DeleteHandler(webapp2.RequestHandler):
    def post(self, id=None):
        query = MM.query(MM.email == self.request.get("email")).fetch()
        for person in query:
            person.key.delete()

        # go back to users home page
        self.redirect("/user/" + memcache.get(key='user') )

# Award is now Award2
class Awards(webapp2.RequestHandler):
    def get(self, id=None):
        get_user_query_results = [get_user_query.to_dict()
                                      for get_user_query in Award2.query()]
        self.response.write(json.dumps(get_user_query_results))  # display results to user



class Award(webapp2.RequestHandler):
    def get(self, id=None):

        # get value from the paramters
        recip= self.request.get("recip")
        email = self.request.get("email")


        # get the users email address
        query = User.query(User.username == memcache.get(key='user')).get()
        q_d = query.to_dict()

        # put values into a dictionary so view can use them
        template_vars = { "recip" : recip, "email" : email , "current_user" : memcache.get(key='user'), "sender_email" : q_d['email']}

        template = JINJA_ENV.get_template('createAward.html')
        self.response.out.write(template.render(template_vars))


    #  post method to create award
    def post(self, id=None):

        # create a new Award2
        e = Award2()
        e.recipient = self.request.get("recipname")
        e.type = self.request.get("type")
        e.date = None
        e.manager = memcache.get(key='user')  # set manager to current logged
        #in user
        e.put()

        emailResult = ""
        try:

            # test sending out email
            FROM = self.request.get("manageremail")
            TO = self.request.get("recipemail") # must be list
            # SUBJECT = "Congratulations on Your Award"
            #TEXT = "This is the capstone application. This award PDF for Employee of the Month"

            # This works, but ends up as gibberish
            msg = MIMEMultipart()

            # Add the email subject line
            msg['Subject'] = "Congratulations on Your Award"
            msg['Text'] = "This award PDF for Employee of the Month"

            cover_letter = MIMEApplication(open("EmployeeOfTheMonth.pdf", "rb").read())
            cover_letter.add_header('Content-Disposition', 'attachment', filename="EmployeeOfTheMonth.pdf")
            msg.attach(cover_letter)

            #msg.attach(MIMEText(file("EmployeeOfTheMonth.pdf").read()))

            username = self.request.get("manageremail")
            password = self.request.get("managerpassword")   ### always remove the password ############################
            server = smtplib.SMTP('smtp.gmail.com:587')


            server.starttls()
            server.ehlo()
            server.login(username,password)
            server.sendmail(FROM, TO, msg.as_string()) #TEXT
            server.quit()
            emailResult = "success"


        except Exception, e:
            emailResult = "failed to email"
            self.redirect("/" )
        # go back to users home page
        self.redirect("/user/" + memcache.get(key='user') )




class Admin(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENV.get_template('adminLogin.html')
        self.response.out.write(template.render())

    def post(self):
        if self.request.get("username") == "cat" and self.request.get("password")=="fish":
            # set memcache to admin Logged in = true
            self.redirect("/adminPage")

        else:
            # notify user that password was wrong
            self.redirect("/admin")

class AdminPage(webapp2.RequestHandler):
    def get(self):
        # check if admin is logged in, otherwise notify user and
        # redirect to admin login

        template = JINJA_ENV.get_template('adminPage.html')
        self.response.out.write(template.render())


app = webapp2.WSGIApplication([

    ('/', MainPage),
    ('/createUser', CreateUser),
    ('/signIn', SignIn),
    ('/users', UserHandler),
    ('/user/(.*)', UserHandler2),
    ('/workers', Workers),
    ('/worker', Worker),
    ('/logout', Logout),
    ('/delete/(.*)', DeleteHandler),
    ('/awards', Awards),
    ('/award', Award),
    ('/myaccount', MyAccount),
    ('/admin', Admin),
    ('/adminPage', AdminPage)

], debug=True)
