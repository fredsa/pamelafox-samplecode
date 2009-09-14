import cgi
import os
import random

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache

from django.utils import simplejson

import models
import geocoder
import util 
import geodata

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
    return "worldmap.html"

class DebugPage(webapp.RequestHandler):
  def get(self):
    countryCode = self.request.get('countryCode')
    if not countryCode:
      countryCode = 'AU'
    self.response.out.write("<table>")
    self.write("countryCode", countryCode)
    self.write("getCountryVotesInStore", util.getCountryVotesInStore(countryCode))
    self.write("getCountryVotesPerPostcodeInStore", util.getCountryVotesPerPostcodeInStore(countryCode))
    self.write("getCountryVotes", util.getCountryVotes(countryCode))
    self.write("getTotalVotes", util.getTotalVotes())
    self.response.out.write("</table>")
    self.response.out.write("<form action=/addrandom?countryCode=AU method=get><input type=submit value=RandomAU></form>")
    self.response.out.write("<form action=/clearcache?countryCode=AU method=get><input type=submit value=ClearMemcacheAU></form>")

  def write(self, header, info):
    self.response.out.write("<tr><td>" + header + "</td><td>" + str(info) + "</td></tr>")

class MemcacheClearer(webapp.RequestHandler):
  def get(self):
    memcache.delete(models.MEMCACHE_VOTES + 'TOTAL')
    memcache.delete(models.genKeyForCountriesInfo())
    memcache.delete(models.genKeyForContinentsInfo())

    countryCode = self.request.get("countryCode")
    memcache.delete(models.genKeyForStatesInfo(countryCode))
    memcache.delete(models.MEMCACHE_VOTES + 'TOTAL')
    for stateCode in geodata.countries[countryCode]['states']:
      memcache.delete(models.MEMCACHE_VOTES + countryCode + stateCode)


class RandomAddService(webapp.RequestHandler):
  def get(self):
    signer = models.PetitionSigner()
    signer.name = "Random"
    signer.num = 2
    signer.email = "random@google.com"
    signer.streetinfo = "1 Main St"
    signer.city = "Random"
    countryCode = self.request.get("countryCode")
    if not countryCode:
      possibleCountries = geodata.countries
      countryCode = random.choice(possibleCountries.keys())
    if util.countryHasStates(countryCode):
      possibleStates = geodata.countries[countryCode]["states"]
      signer.state = random.choice(possibleStates.keys())
      signer.postcode = signer.state + str(random.randrange(1,100))
    else:
      signer.state = countryCode + "Random"
      signer.postcode = countryCode + str(random.randrange(1,100))
    signer.country = countryCode
    signer.latlng = db.GeoPt(0,0)
    signer.put()
    self.response.out.write(signer.country + "<br>")
    self.response.out.write(signer.state)
    util.addSignerToClusters(signer)

class SignerAddService(webapp.RequestHandler):
  def post(self):
    signer = models.PetitionSigner()
    type = self.request.get('type')
    if type is "family":
      signer.name = self.request.get('family_name')
      signer.num = int(self.request.get('family_num'))
    elif type is "org":
      signer.name = self.request.get('org_name')
      signer.num = int(self.request.get('org_num'))
      signer.org_icon = self.request.get('org_icon')
    signer.email = self.request.get('email')
    #signer.streetinfo = self.request.get('streetinfo')
    signer.city = self.request.get('city')
    signer.state = self.request.get('state')
    signer.country = self.request.get('country')
    signer.postcode = self.request.get('postcode')
    latlng = geocoder.geocodeAddress(signer.city + " " + signer.state + " " + signer.postcode + " " + signer.country)
    if latlng is not None:
       signer.latlng = latlng
    signer.put()
    util.addSignerToClusters(signer)
    #self.redirect('/signup')
    self.redirect('/map?countryCode=' + signer.country + '&latlng=' + str(latlng.lat) + ',' + str(latlng.lon))
