import cgi
import os
import urllib
import logging
import pickle

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

# Set the debug level
_DEBUG = True

class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)

class BaseRequestHandler(webapp.RequestHandler):
  """Base request handler extends webapp.Request handler

     It defines the generate method, which renders a Django template
     in response to a web request
  """

  def generate(self, template_name, template_values={}):
    """Generate takes renders and HTML template along with values
       passed to that template

       Args:
         template_name: A string that represents the name of the HTML template
         template_values: A dictionary that associates objects with a string
           assigned to that object to call in the HTML template.  The defualt
           is an empty dictionary.
    """
    # We check if there is a current user and generate a login or logout URL
    user = users.get_current_user()

    if user:
      log_in_out_url = users.create_logout_url('/')
    else:
      log_in_out_url = users.create_login_url(self.request.path)

    # We'll display the user name if available and the URL on all pages
    values = {'user': user, 'log_in_out_url': log_in_out_url}
    values.update(template_values)

    # Construct the path to the template
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'templates', template_name)

    # Respond to the request by rendering the template
    return template.render(path, values, debug=_DEBUG)
    
class MainRequestHandler(BaseRequestHandler):
  def get(self):
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      }

    self.response.out.write(self.generate('index.html', template_values));

class ChatsRequestHandler(BaseRequestHandler):
  MEMCACHE_KEY = 'greetings'
  MEMCACHE_TEMPLATE = 'greetings_template'
  
  def get(self):
    template = memcache.get(self.MEMCACHE_TEMPLATE)
    self.response.out.write(template)
    
  def post(self):
    greeting = Greeting()

    if users.get_current_user():
      greeting.author = users.get_current_user()
    
    greeting.content = self.request.get('content')
    greeting.put()
    
    greetingsString = memcache.get(self.MEMCACHE_KEY)
    if greetingsString is None:
      greetingsList = []
    else:
      greetingsList = pickle.loads(greetingsString)
      if len(greetingsList) >= 40:
        greetingsList.pop()
    greetingsList.insert(0, greeting)

    if not memcache.set(self.MEMCACHE_KEY, pickle.dumps(greetingsList)):
        logging.debug("Memcache set failed:")

    template_values = {
      'greetings': greetingsList,
    }
    template = self.generate('chats.html', template_values)
    if not memcache.set(self.MEMCACHE_TEMPLATE, template):
        logging.debug("Memcache set failed:")

    self.response.out.write(template)



                                                
application = webapp.WSGIApplication(
                                     [('/chat', MainRequestHandler),
                                      ('/getchats', ChatsRequestHandler)
                                      ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
