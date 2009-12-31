#!/usr/bin/python2.5
#
# Copyright 2009 Google Inc.
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0

"""The module that handles requests for user-facing pages.

This model sets up a base class for requests, and then each
page extends that class to define its own title and other
customizations.
"""

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


class BasePage(webapp.RequestHandler):
  """The base class for actual pages to subclass."""

  def get(self):
    self.Render(self.GetTemplateFilename(), self.GetTemplateValues())

  def GetTemplateValues(self, page_title='Welcome'):
    template_values = {'page_title': page_title}
    return template_values

  def GetTemplateFilename(self):
    return 'base.html'

  def Render(self, filename, template_values):
    path = os.path.join(os.path.dirname(__file__), 'templates', filename)
    self.response.out.write(template.render(path, template_values))


class Home(BasePage):
  """The main page, displays just a message and links to the user."""

  def GetTemplateValues(self):
    template_values = BasePage.GetTemplateValues(self, 'PETITION')
    return template_values

  def GetTemplateFilename(self):
    return 'main.html'


class Signup(BasePage):
  """The signup page, displays a form."""

  def GetTemplateValues(self):
    template_values = BasePage.GetTemplateValues(self, 'SIGN THE PETITION')
    return template_values

  def GetTemplateFilename(self):
    return 'form.html'


class Map(BasePage):
  """The map page, displays a dynamic map."""

  def GetTemplateValues(self):
    template_values = BasePage.GetTemplateValues(self, 'VIEW THE MAP')
    return template_values

  def GetTemplateFilename(self):
    return 'map.html'
