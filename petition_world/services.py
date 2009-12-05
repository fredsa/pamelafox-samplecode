import cgi
import os
import logging
import copy

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import images

from django.utils import simplejson

import models
import util
import geodata

class CryptographicNonceService(webapp.RequestHandler):
  def get(self):
    # Don't cache this value
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
    self.response.headers.add_header('Expires', 'Thu, 01 Jan 1970 08:00:00 GMT')
    # Produces 160 bits of randomness to send back to the user
    randomVal = ''.join(["%02x" % ord(x) for x in os.urandom(20)])
    # Check the cookie, if they've already got an identifier, use it,
    # otherwise, generate a new one
    identifierVal = self.request.cookies.get(
      'identifier',
      ''.join(["%02x" % ord(x) for x in os.urandom(20)])
    )
    # No value is required, we only need to be able to verify that we've
    # issued this nonce in the recent past.
    memcache.set(randomVal, '', 3600)
    # Spam bots generally don't maintain cookie stores
    self.response.headers.add_header(
      'Set-Cookie', 'nonce=%s; path=/' % randomVal
    )
    # This keeps people from voting twice
    self.response.headers.add_header(
      'Set-Cookie', ('identifier=%s; path=/; ' +
      'expires=Sat, 01 Jan 2011 08:00:00 GMT') % identifierVal
    )
    # Simple format string is faster than a JSON dump
    self.response.out.write("{\"nonce\": \"%s\"}" % randomVal)

class VotesInLocationService(webapp.RequestHandler):
  def get(self):
    self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
    self.response.headers.add_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
    country = self.request.get('country')
    state = self.request.get('state')
    city = self.request.get('city')
    postcode = self.request.get('postcode')
    query = db.Query(models.PetitionSigner)
    if country is not None and country != '':
      query.filter('country =', country)
    if state is not None and state != '':
      query.filter('state =', state)
    if city is not None and city != '':
      query.filter('city =', city)
    if postcode is not None and postcode != '':
      query.filter('postcode =', postcode)
    results = query.fetch(16) # 4 x 4 pictures
    data = []
    for result in results:
      if result.gfc_id is not None and result.gfc_id != '':
        signer = {}
        signer['gfcId'] = result.gfc_id
        data.append(signer)
    self.response.out.write(simplejson.dumps(data))

class ContinentsInfoService(webapp.RequestHandler):
  def get(self):
    self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
    self.response.headers.add_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
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
    self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
    self.response.headers.add_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
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
    self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
    self.response.headers.add_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
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
    self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
    self.response.headers.add_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
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

class OrgsInfoService(webapp.RequestHandler):
  def get(self):
    self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
    self.response.headers.add_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
    countryCode = self.request.get('countryCode')
    cachedVal = memcache.get(models.genKeyForOrgsInfo(countryCode))
    if cachedVal is not None:
      self.response.out.write(cachedVal)
    else:
      data  = {}
      results = util.getOrgsInCountry(countryCode)
      data['orgs'] = []
      for result in results:
        data['orgs'].append({"name": result.name, "center": [result.latlng.lat, result.latlng.lon], "freetext": result.freetext, "media": result.media, "icon": result.org_icon});

      newVal = simplejson.dumps(data)
      memcache.set(models.genKeyForOrgsInfo(countryCode), newVal, 10)
      self.response.out.write(newVal)

class TotalsInfoService(webapp.RequestHandler):
  def get(self):
    self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
    self.response.headers.add_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
    cachedVal = memcache.get(models.genKeyForTotalsInfo())
    if cachedVal is not None:
      logging.info("Memcache hit: %s" % (cachedVal))
      self.response.out.write(cachedVal)
    else:
      data  = {}
      totalVotes, totalCountries, totalOrgs = util.getTotals()
      data['total'] = {'totalVotes': totalVotes, 'totalCountries': totalCountries, 'totalOrgs': totalOrgs}
      newVal = simplejson.dumps(data)
      memcache.set(models.genKeyForTotalsInfo(), newVal, 30)
      self.response.out.write(newVal)


class GetBoundedOrgs(webapp.RequestHandler):
  def get(self):
    self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
    self.response.headers.add_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
    cachedVal = memcache.get(models.genKeyForBoundedOrgs())
    if cachedVal is not None:
       self.response.out.write(cachedVal)
    else:
    #countryCodes = self.request.get('countryCode').split('|')
        name = self.request.get('name')
        #bounds = self.request.get('bounds')
        results = []
        for code in geodata.countries.keys():
          results.extend(util.getOrgsInCountryForName(code,name))
    
        logging.info(results)
        ret = lambda x : ((x.latlng.lat,x.latlng.lon),x.name , x.org_icon)
        display = {}
        # this could be O(n) but this allows for easier changes to the retun object while i 
        # develop and test the search feature 
        #dict with unique locations
        totalResults = util.getUniqueWithCount(results,lambda y: str(y.latlng.lat) + str(y.latlng.lon),ret)
        #dict with unique countrys
        countryResults = util.getUniqueWithCount(results,lambda y: y.country ,lambda x : (geodata.countries[x.country]['center'],x.name,x.org_icon))
        display['zoomed'] = totalResults
        display['countryLevel'] = countryResults
        response = simplejson.dumps(display)
        #5 mins seems to be the defacto
        memcache.set(models.genKeyForBoundedOrgs(), response, 300)
        self.response.out.write(response)
      
      
class TwitterService(webapp.RequestHandler):
    def get(self):
        self.response.headers.add_header('Cache-Control', 'no-cache, must-revalidate')
        self.response.headers.add_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
        self.response.out.write('{"results":[{"profile_image_url":"http://a3.twimg.com/profile_images/292680765/Photo_14_normal.jpg","created_at":"Fri, 04 Dec 2009 23:06:09 +0000","from_user":"enfox","to_user_id":452837,"text":"@earthhour Im Voting Earth for Earth Hour Copenhagen! Show your vote for Earth too at http://www.earthhour.org","id":6352307121,"from_user_id":127933,"to_user":"earthhour","geo":null,"iso_language_code":"en","source":"<a href="http://twitter.com/">web</a>"},{"profile_image_url":"http://a3.twimg.com/profile_images/536284163/12966_178182684102_722859102_3018367_27518_n_normal.jpg","created_at":"Fri, 04 Dec 2009 23:04:59 +0000","from_user":"miskolino","to_user_id":null,"text":"Im Voting Earth for Earth Hour Copenhagen! Show your vote for Earth too at http://www.earthhour.org (via @earthhour)","id":6352275687,"from_user_id":3359267,"geo":null,"iso_language_code":"en","source":"<a href="http://twitter.com/">web</a>"},{"profile_image_url":"http://a3.twimg.com/profile_images/406964235/P7182730_normal.JPG","created_at":"Fri, 04 Dec 2009 22:55:45 +0000","from_user":"ViolenaJ","to_user_id":452837,"text":"@earthhour Im Voting Earth for Earth Hour Copenhagen! Show your vote for Earth too at http://www.earthhour.org","id":6352037109,"from_user_id":41668672,"to_user":"earthhour","geo":null,"iso_language_code":"en","source":"<a href="http://twitter.com/">web</a>"},{"profile_image_url":"http://a1.twimg.com/profile_images/500883552/jp140185_normal.png","created_at":"Fri, 04 Dec 2009 22:24:51 +0000","from_user":"Jeep_Down_Under","to_user_id":null,"text":"Great! RT @earthhour: Obama to come to Copenhagen at decision time @ COP15. Will this turn out to be #Hopenhagen: http://tinyurl.com/yb6tj3t","id":6351256065,"from_user_id":29644019,"geo":null,"iso_language_code":"en","source":"<a href="http://www.tweetdeck.com/" rel="nofollow">TweetDeck</a>"}],"max_id":6352307121,"since_id":0,"refresh_url":"?since_id=6352307121&q=earthHour","next_page":"?page=2&max_id=6352307121&q=earthHour","results_per_page":15,"page":1,"completed_in":0.092802,"query":"earthHour"}')
    
class GetUniqueOrgs(webapp.RequestHandler):
  def get(self):
    cachedVal = memcache.get(models.genKeyForAllOrgsInfo())
    if cachedVal is not None:
      self.response.out.write(cachedVal)
    else:
      allOrgNames = []
      #with out an org table this really is not optimal
      for countryCode in geodata.countries.keys():
         allOrgNames.extend(map(lambda x: x.name.upper().strip(),util.getOrgsInCountry(countryCode)))
      jsonDump = simplejson.dumps(util.getUnique(allOrgNames))
      memcache.set(models.genKeyForAllOrgsInfo(), jsonDump, 300)
      self.response.out.write(jsonDump)
      
      
#get logos
#TODO: memcache, browser cache should save most of this
#especially since its being round tripped
class LogoForOrg(webapp.RequestHandler):
  def get(self):
     orgName = self.request.get('orgName')
     logging.info(orgName)
     query = db.Query(models.PetitionSigner)
     result = query.filter('name =',orgName).get()
     if result is not None:
       if result.org_icon_hosted is not None:
          self.response.headers['Content-Type'] = "image/png"
          image = result.org_icon_hosted
          self.response.out.write(image)
          
        
     
    