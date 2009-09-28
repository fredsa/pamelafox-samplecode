import cgi
import os
import random
import logging
import hashlib

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

class RootRedirect(webapp.RequestHandler):
  def get(self):
    self.redirect('/learn')

class BasePage(webapp.RequestHandler):
  def get(self):
    self.render(self.getTemplateFilename(), self.getTemplateValues())

  def getTemplateValues(self, page_title, page_num):
    template_values = {'page_title': page_title, 'page_num': page_num}
    return template_values

  def getTemplateFilename(self):
    return "base.html"

  def render(self, filename, template_values):
    path = os.path.join(os.path.dirname(__file__), 'templates', filename)
    self.response.out.write(template.render(path, template_values))

class LearnPage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Learn', 0)
    return template_values

  def getTemplateFilename(self):
    return "learn.html"

class VotePage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Vote', 1)
    return template_values

  def getTemplateFilename(self):
    return "vote.html"

class ExplorePage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Explore', 2)
    return template_values

  def getTemplateFilename(self):
    return "explore.html"

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
    originalNonce = self.request.cookies.get('nonce', None)
    hashedNonce = self.request.get('nonce')
    cachedVal = memcache.get(originalNonce)
    if hashedNonce and originalNonce and cachedVal is not None and hashlib.sha1(originalNonce).hexdigest() == hashedNonce:
      memcache.delete(originalNonce, 0)
      signer = models.PetitionSigner()
      if not self.request.get('org_name') or self.request.get('org_name') == '':
        signer.type = 'person'
        signer.name = self.request.get('person_name')
        signer.gfc_id = self.request.get('person_gfc_id')
      else:
        signer.type = 'org'
        signer.name = self.request.get('org_name')
        signer.org_icon = self.request.get('org_icon')
        signer.email = self.request.get('email')
        signer.streetinfo = self.request.get('streetinfo')
      signer.city = self.request.get('city')
      signer.state = self.request.get('state')
      signer.country = self.request.get('country')
      signer.postcode = self.request.get('postcode')
      signer.latlng = db.GeoPt(float(self.request.get('lat')), float(self.request.get('lng')))
      signer.put()
      util.addSignerToClusters(signer, signer.latlng)
      self.response.headers.add_header('Set-Cookie', 'latlng=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT; path=/' % (str(signer.latlng.lat) + ',' + str(signer.latlng.lon)))
      self.redirect('/explore')
    else:
      # Spam
      # TODO: log this!
      self.redirect('/')
