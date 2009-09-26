import cgi
import os
import logging
import copy

from google.appengine.ext import webapp
from google.appengine.api import memcache

from django.utils import simplejson

import models
import util
import geodata

class CryptographicNonceService(webapp.RequestHandler):
  def get(self):
    # Produces 160 bits of randomness to send back to the user
    randomVal = ''.join(["%02x" % ord(x) for x in os.urandom(20)])
    # No value is required, we only need to be able to verify that we've
    # issued this nonce in the recent past.
    memcache.set(randomVal, '', 900, 0, 'nonce')
    self.response.headers.add_header(
      'Set-Cookie', 'nonce=%s; path=/' % randomVal
    )
    self.response.out.write(simplejson.dumps({'nonce': randomVal}))

class ContinentsInfoService(webapp.RequestHandler):
  def get(self):
    cachedVal = memcache.get(models.genKeyForContinentsInfo())
    if cachedVal is not None:
      self.response.out.write(cachedVal)
    else:
      data = {}
      data['continents'] = copy.deepcopy(geodata.continents)
      for continentCode in geodata.continents:
        data['continents'][continentCode]['count'] = util.getContinentVotes(continentCode)
      newVal = simplejson.dumps(data)
      memcache.set(models.genKeyForContinentsInfo(), newVal, 300)
      self.response.out.write(newVal)

class CountriesInfoService(webapp.RequestHandler):
  def get(self):
    cachedVal = memcache.get(models.genKeyForCountriesInfo())
    if cachedVal is not None:
      self.response.out.write(cachedVal)
    else:
      data = {}
      data['countries'] = copy.deepcopy(geodata.countries)
      for countryCode in geodata.countries:
        count = util.getCountryVotes(countryCode)
        if count is 0:
          del data['countries'][countryCode]
        else:
          data['countries'][countryCode]['count'] = count
          del data['countries'][countryCode]['points']
          del data['countries'][countryCode]['levels']
          if util.countryHasStates(countryCode):
            del data['countries'][countryCode]['states']

      newVal = simplejson.dumps(data)
      memcache.set(models.genKeyForCountriesInfo(), newVal, 300)
      self.response.out.write(newVal)

class StatesInfoService(webapp.RequestHandler):
  def get(self):
    countryCode = self.request.get('countryCode')
    cachedVal = memcache.get(models.genKeyForStatesInfo(countryCode))
    if cachedVal is not None:
      self.response.out.write(cachedVal)
    else:
      data = {}
      data['states'] = copy.deepcopy(geodata.countries[countryCode]['states'])
      for stateCode in geodata.countries[countryCode]['states']:
        count = util.getStateVotes(countryCode, stateCode)
        if count is 0:
          del data['states'][stateCode]
        else:
          data['states'][stateCode]['count'] = count

      newVal = simplejson.dumps(data)
      memcache.set(models.genKeyForStatesInfo(countryCode), newVal, 300)
      self.response.out.write(newVal)

class PostcodesInfoService(webapp.RequestHandler):
  def get(self):
    countryCode = self.request.get('countryCode')
    cachedVal = memcache.get(models.genKeyForPostcodesInfo(countryCode))
    if cachedVal is not None:
      self.response.out.write(cachedVal)
    else:
      data  = {}
      results = util.getPostcodesInCountry(countryCode)
      data['postcodes'] = {}
      for result in results:
        data['postcodes'][result.postcode] = {"count": result.counter, "center": [result.latlng.lat, result.latlng.lon]}

      newVal = simplejson.dumps(data)
      memcache.set(models.genKeyForPostcodesInfo(countryCode), newVal, 10)
      self.response.out.write(newVal)