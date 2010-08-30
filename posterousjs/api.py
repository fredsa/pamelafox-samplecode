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
from django.utils import simplejson

class ApiHandler(webapp.RequestHandler):

  def get(self):
    path = self.request.path
    query_string = self.request.query_string
    url = 'http://posterous.com' + path + '?' + query_string
    result = urlfetch.fetch(url, deadline=10)
    logging.info(result.status_code)
    dict = None
    if result.status_code == 200:
      dom = minidom.parseString(result.content)
      errors = dom.getElementsByTagName('err')
      logging.info(errors)
      if errors:
        dict = {'error': errors[0].getAttribute('msg')}
      # Top-level will either be posts, tags, or sites
      elif path.find('readposts') > -1:
        dict = self.flat_dict(dom, 'post')
      elif path.find('gettags') > -1:
        dict = self.flat_dict(dom, 'tag')
      elif path.find('getsites') > -1:
        dict = self.flat_dict(dom, 'site')
    else:
      dict = {'error': '404'}

    if dict:
      logging.info(dict)
      json = simplejson.dumps(dict)
      callback = self.request.get('callback')
      self.response.headers['Content-Type'] = 'application/json'
      if callback:
        self.response.out.write(callback + '(' + json + ')')
      else:
        self.response.out.write(json)

  def flat_dict(self, dom, tag_name):
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
