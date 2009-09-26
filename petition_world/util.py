import cgi
import os
import logging

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

def addSignerToClusters(signer, extraLatLng):
  clusterdata = {'lastname': signer.name,
                 # 'streetinfo': signer.streetinfo,
                 'city': signer.city,
                 'state': signer.state,
                 'country': signer.country,
                 'postcode': signer.postcode,
                 'lat': signer.latlng.lat,
                 'lng': signer.latlng.lon}

  countryCode = signer.country
  stateCode = signer.state
  postcode = signer.postcode
  memcache.delete(models.MEMCACHE_VOTES + countryCode)
  memcache.delete(models.MEMCACHE_VOTES + countryCode + postcode)
  memcache.delete(models.MEMCACHE_VOTES + countryCode + stateCode)

  if not countryHasPostcodes(countryCode):
    query = db.Query(models.Country)
    query.filter('country =', countryCode)
    result = query.get()
    if result is None:
      countryCounter = models.Country
      countryCounter.country = countryCode
      countryCounter.counter = 1
      countryCounter.data = simplejson.dumps([clusterdata])
      countryCounter.put()
    else:
      countryCounter = result
      countryCounter.counter = countryCounter.counter + 1
      data = simplejson.loads(postcodecluster.data)
      data.append(clusterdata)
      countryCounter.data = simplejson.dumps(data)
      countryCounter.put()
  else:
    query = db.Query(models.Postcode)
    query.filter('country =', countryCode)
    query.filter('postcode =', postcode)
    result = query.get()
    if result is None:
      postcodecluster = models.Postcode()
      postcodecluster.postcode = postcode
      postcodecluster.state = stateCode
      postcodecluster.country = countryCode
      postcodecluster.data = simplejson.dumps([clusterdata])
      postcodecluster.counter = 1
      postcodecluster.latlng = extraLatLng
      postcodecluster.put()
    else:
      postcodecluster = result
      postcodecluster.counter = postcodecluster.counter + 1
      data = simplejson.loads(postcodecluster.data)
      data.append(clusterdata)
      postcodecluster.data = simplejson.dumps(data)
      postcodecluster.put()

def countryHasPostcodes(countryCode):
  #todo: log if country doesn't exit
  return geodata.countries[countryCode]['postcode'] >= 0

def countryHasStates(countryCode):
  return geodata.countries[countryCode].has_key('states')

def getCountryVotesInStore(countryCode):
  query = db.Query(models.Country)
  query.filter('country =', countryCode)
  result = query.get()
  if result:
    return result.counter
  else:
    return -1

def getCountryVotesPerStateInStore(countryCode):
  numVotesInCountry = 0
  for stateCode in geodata.countries[countryCode]['states']:
    votesMemcache = memcache.get(models.MEMCACHE_VOTES + countryCode + stateCode)
    if votesMemcache is not None:
      logging.info("Memcache hit: " + countryCode + stateCode)
      numVotesInCountry += int(votesMemcache)
    else:
      logging.info("Memcache miss: " + countryCode + stateCode)
      # get all the postcodes for that state
      # 10 states have more than 1,000 - 3 have more than 2,000
      # We will have to re-fetch max of 2 times
      query = db.Query(models.Postcode)
      query.filter('country =', countryCode)
      query.filter('state =', stateCode)
      results = query.fetch(1000)
      numVotesInState = 0
      for result in results:
        logging.info(result.state)
        numVotesInState += result.counter
      logging.info("Adding " + str(numVotesInState))
      memcache.set(models.MEMCACHE_VOTES + countryCode + stateCode, str(numVotesInState))
      numVotesInCountry += numVotesInState
  return numVotesInCountry

def getCountryVotesPerPostcodeInStore(countryCode):
  numVotesInCountry = 0
  results = getPostcodesInCountry(countryCode)
  for result in results:
    numVotesInCountry += result.counter
  return numVotesInCountry

def getStateVotesInStore(countryCode, stateCode):
  numVotesInState = 0
  # this relies on there being less than 1000 postcodes in a state
  # there are 4 states that violate this, max is 2600
  # todo: account for those 4 states
  query = db.Query(models.Postcode)
  query.filter('country =', countryCode)
  query.filter('state =', stateCode)
  results = query.fetch(1000)
  for result in results:
    numVotesInState += result.counter
  return numVotesInState

def getTotalVotes():
  # keep this memcached as much as possible
  # perhaps only re-calculate every 5 minutes?
  votesMemcache = memcache.get(models.MEMCACHE_VOTES + 'TOTAL')
  if votesMemcache is not None:
    return int(votesMemcache)
  else:
    numVotesTotal = 0
    for countryCode in geodata.countries:
      numVotesTotal += getCountryVotes(countryCode)
    memcache.set(models.MEMCACHE_VOTES + 'TOTAL', str(numVotesTotal), 300)
    return numVotesTotal

def getContinentVotes(continentCode):
  votesMemcache = memcache.get(models.MEMCACHE_VOTES + 'CONT_' + continentCode)
  if votesMemcache is not None:
    return int(votesMemcache)
  else:
    numVotesTotal = 0
    for countryCode in geodata.continents[continentCode]["countries"]:
      numVotesTotal += getCountryVotes(countryCode)
    memcache.set(models.MEMCACHE_VOTES + 'CONT_' + continentCode, str(numVotesTotal), 300)
    return numVotesTotal

def getCountryVotes(countryCode):
  votesMemcache = memcache.get(models.MEMCACHE_VOTES + countryCode)
  if votesMemcache is not None:
    return int(votesMemcache)
  elif not countryHasPostcodes(countryCode) and not countryHasStates(countryCode):
    votesInCountry = getCountryVotesInStore(countryCode)
  elif countryHasStates(countryCode):
    votesInCountry = getCountryVotesPerStateInStore(countryCode)
  elif countryHasPostcodes(countryCode):
    votesInCountry = getCountryVotesPerPostcodeInStore(countryCode)

  memcache.set(models.MEMCACHE_VOTES + countryCode, str(votesInCountry))
  return votesInCountry


def getStateVotes(countryCode, stateCode):
  votesMemcache = memcache.get(models.MEMCACHE_VOTES + countryCode + stateCode)
  if votesMemcache is not None:
    return int(votesMemcache)
  else:
    numVotesInState = getStateVotesInStore(countryCode, stateCode)
    memcache.set(models.MEMCACHE_VOTES + countryCode + stateCode, str(numVotesInState))
    return numVotesInState


def getPostcodeVotes(countryCode, postcode):
  votesMemcache = memcache.get(models.MEMCACHE_VOTES + countryCode + postcode)
  if votesMemcache is not None:
    return int(votesMemcache)
  else:
    numVotesInPostcode = getPostcodeVotesInStore()
    memcache.set(models.MEMCACHE_VOTES + countryCode + postcode, str(numVotesInPostcode))
    return numVotesInPostcode

def getPostcodesInCountry(countryCode):
  query = db.Query(models.Postcode)
  query.filter('country =', countryCode)
  # todo: account for some countries having more than 1000 postcodes
  results = query.fetch(1000)
  return results