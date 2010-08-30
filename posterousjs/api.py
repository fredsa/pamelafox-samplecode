#!/usr/bin/python2.5
#
# Copyright 2009 Google Inc.
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0

import logging
from xml.dom import minidom

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.api import memcache

from django.utils import simplejson

class ApiHandler(webapp.RequestHandler):
  """ Handles all calls to api/, and responds with JSONinified version of
  equivalent Posterous API call."""

  def get(self):
    dict = None

    # Form URL to Posterous API according to request URL
    url = 'http://posterous.com' + self.request.path + '?' + self.request.query_string

    # Check if the result is cached
    cached_result = memcache.get(url)
    if cached_result:
      dict = simplejson.loads(cached_result)
    else:
      dict = self.convert_results(url)

    # Output JSON result, and wrap in callback if provided
    if dict:
      json = simplejson.dumps(dict)
      # Stick it in cache for 5 minutes
      memcache.set(url, json, 300)
      callback = self.request.get('callback')
      self.response.headers['Content-Type'] = 'application/json'
      if callback:
        self.response.out.write(callback + '(' + json + ')')
      else:
        self.response.out.write(json)

  def convert_results(self, url):
    """ Returns a Python dict containing the API results for given URL."""

    dict = None

    # Fetch the URL (with 10 seconds window, in case API is slow to respond)
    result = urlfetch.fetch(url, deadline=10)
    if result.status_code == 200:
      dom = minidom.parseString(result.content)
      # Check for Posterous API errors first
      errors = dom.getElementsByTagName('err')
      if errors:
        dict = {'error': errors[0].getAttribute('msg')}
      # Top-level will either be posts, tags, or sites
      elif url.find('readposts') > -1:
        dict = self.convert_dom(dom, 'post')
      elif url.find('gettags') > -1:
        dict = self.convert_dom(dom, 'tag')
      elif url.find('getsites') > -1:
        dict = self.convert_dom(dom, 'site')
    else:
      dict = {'error': result.status_code}
    return dict

  def convert_dom(self, dom, tag_name):
    """ Returns a Python dict for the top-level tags in a given API result."""

    dict = {}
    top_nodes = dom.getElementsByTagName(tag_name)
    nodes_list = []
    for top_node in top_nodes:
      child_dict = {}
      for child_node in top_node.childNodes:
        if child_node.nodeType != child_node.TEXT_NODE:
          child_dict[child_node.tagName] = child_node.firstChild.wholeText
      nodes_list.append(child_dict)
    dict[tag_name] = nodes_list
    return dict

def main():
  application = webapp.WSGIApplication([(r'/api/.*', ApiHandler)],
                                     debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
