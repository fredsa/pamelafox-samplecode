#!/usr/bin/python2.5
#
# Copyright 2009 Google Inc.
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0

"""The main module that sets up URL handlers and runs the app.

This module uses the App Engine webapp library to assign
URL patterns to various classes. The classes are divided into
two modules, services and pages. Services are used behind-the-scenes,
pages are what the user sees.
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import pages
import services


def main():
  application = webapp.WSGIApplication([
      ('/', pages.Home),
      ('/map', pages.Map),
      ('/signup', pages.Signup),
      ('/services/signup', services.Signup),
      ('/services/setup', services.Setup),
      ('/services/clusters', services.Clusters),
      ], debug=True)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
