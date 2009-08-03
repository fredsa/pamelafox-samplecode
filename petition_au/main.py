import cgi
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache

from django.utils import simplejson

import models
import geocoder
import geodata

MEMCACHE_MAXPOSTCODES = 'maxpostcode'
MEMCACHE_STATECLUSTER = 'statecluster_'

class BasePage(webapp.RequestHandler):
  def get(self):
    self.render(self.getTemplateFilename(), self.getTemplateValues())

  def getTemplateValues(self, page_title):
    template_values = {'page_title': page_title}
    return template_values

  def getTemplateFilename(self):
    return "base.html"

  def render(self, filename, template_values):
    path = os.path.join(os.path.dirname(__file__), 'templates', filename)
    self.response.out.write(template.render(path, template_values))

class MainPage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'PETITION')
    return template_values

  def getTemplateFilename(self):
    return "main.html"

class FormPage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'SIGN THE PETITION')
    return template_values

  def getTemplateFilename(self):
    return "form.html"

class MapPage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'VIEW THE MAP')
    return template_values

  def getTemplateFilename(self):
    return "map.html"

class Guestbook(webapp.RequestHandler):
  def post(self):
    signer = models.PetitionSigner()
    type = self.request.get('type')
    self.response.out.write(type + "TYPE")
    if type is "family":
      signer.name = self.request.get('family_name')
      signer.num = int(self.request.get('family_num'))
    elif type is "org":
      signer.name = self.request.get('org_name')
      signer.num = int(self.request.get('org_num'))
      signer.org_icon = self.request.get('org_icon')
    signer.email = self.request.get('email')
    signer.streetinfo = self.request.get('streetinfo')
    signer.city = self.request.get('city')
    signer.state = self.request.get('state')
    signer.postcode = int(self.request.get('postcode'))
    latlng = geocoder.geocodeAddress(signer.streetinfo + " " + signer.city + " " + signer.state + " " + str(signer.postcode))
    if latlng is not None:
       signer.latlng = latlng
    signer.put()
    clusterdata = {'lastname': signer.name,
                   'streetinfo': signer.streetinfo,
                   'city': signer.city,
                   'state': signer.state,
                   'postcode': signer.postcode,
                   'lat': latlng.lat,
                   'lng': latlng.lon}

    query = db.Query(models.RegionCluster)
    query.filter('type =', 'postcode')
    query.filter('name =', str(signer.postcode))
    result = query.get()
    if result is None:
      postcodecluster = models.RegionCluster()
      postcodecluster.type = 'postcode'
      postcodecluster.name = str(signer.postcode)
      postcodecluster.state = signer.state
      postcodecluster.data = simplejson.dumps([clusterdata])
      postcodecluster.count = 1
      latlng = geocoder.geocodeAddress(str(signer.postcode) + ",AU")
      if latlng is not None:
        postcodecluster.latlng = latlng
      postcodecluster.put()
    else:
      postcodecluster = result
      postcodecluster.count = postcodecluster.count + 1
      data = simplejson.loads(postcodecluster.data)
      data.append(clusterdata)
      postcodecluster.data = simplejson.dumps(data)
      postcodecluster.put()

    # Remember the max number of addresses in a postcode, useful for clustering
    maxpostcodes = memcache.get(MEMCACHE_MAXPOSTCODES)
    if maxpostcodes is not None:
      if int(maxpostcodes) < postcodecluster.count:
        memcache.set(MEMCACHE_MAXPOSTCODES, str(postcodecluster.count))
      else:
        findMaxInPostcodes()
    memcache.delete(MEMCACHE_STATECLUSTER + signer.state)
    self.redirect('/map?postcode=' + str(signer.postcode) + '&state=' + signer.state)

def findMaxInPostcodes():
  query = db.Query(models.RegionCluster)
  query.filter('type =', 'postcode')
  query.order('-count')
  result = query.get()
  memcache.set(MEMCACHE_MAXPOSTCODES, str(result.count))
  return result.count

class Setup(webapp.RequestHandler):
  def post(self):
    for state in geodata.states:
      statecluster = RegionCluster()
      statecluster.type = 'state'
      statecluster.name = state.name
      statecluster.data = '[]'
      statecluster.count = 0
      statecluster.latlng = GeoPt(state.lat, state.lng)
      statecluster.put()
    self.response.out.write('Added all the states')

class ClusterGenerator(webapp.RequestHandler):
  def get(self):
    data = {}
    data['states'] = {}
    maxpostcodes = memcache.get(MEMCACHE_MAXPOSTCODES)
    if maxpostcodes is None:
      maxpostcodes = findMaxInPostcodes()
    data['maxpostcodes'] = int(maxpostcodes)

    for state in geodata.states:
      statedataString = memcache.get(MEMCACHE_STATECLUSTER + state['name'])
      if statedataString is None:
        query = db.Query(models.RegionCluster)
        query.filter('type =', 'postcode')
        query.filter('state =', state['name'])
        results = query.fetch(1000)
        statedata = {}
        statedata['lat'] = state['lat']
        statedata['lng'] = state['lng']
        statedata['count'] = len(results)
        statedata['postcodes'] = []
        for result in results:
          statedata['postcodes'].append(simplejson.loads(result.data))
        memcache.set(MEMCACHE_STATECLUSTER + state['name'], simplejson.dumps(statedata))
      else:
        statedata = simplejson.loads(statedataString)
      data['states'][state['name']] = statedata
    self.response.out.write(simplejson.dumps(data))


application = webapp.WSGIApplication(
                                     [
                                      ('/', MainPage),
                                      ('/signup', FormPage),
                                      ('/map', MapPage),
                                      ('/setup', Setup),
                                      ('/getclusters', ClusterGenerator),
                                      ('/sendform', Guestbook)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
