import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
  def get(self):
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
      nickname = users.get_current_user().nickname()
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      nickname = 'anon'

    template_values = {'url': url, 'url_linktext': url_linktext, 'nickname': nickname}

    path = os.path.join(os.path.dirname(__file__), 'templates/geogame.html')
    self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
