##
# Copyright 2008 Google Inc. 
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0
##

from google.appengine.ext import db

MEMCACHE_VOTES = 'VOTES_'

def genKeyForContinentsInfo():
  return 'INFO_CONTINENTS'

def genKeyForCountriesInfo():
  return 'INFO_COUNTRIES'

def genKeyForStatesInfo(countryCode):
  return 'INFO_STATES' + countryCode

def genKeyForPostcodesInfo(countryCode):
  return 'INFO_POSTCODES' + countryCode

class PetitionSigner(db.Model):
  type = db.StringProperty()
  name = db.StringProperty()
  num = db.IntegerProperty()
  org_icon = db.StringProperty()
  streetinfo = db.StringProperty()
  state = db.StringProperty()
  city = db.StringProperty()
  postcode = db.StringProperty()
  country = db.StringProperty()
  latlng = db.GeoPtProperty()

class Postcode(db.Model):
  postcode = db.StringProperty()
  counter = db.IntegerProperty(default=0)
  state = db.StringProperty()
  country = db.StringProperty()
  data = db.TextProperty()
  latlng = db.GeoPtProperty()

class Country(db.Model):
  country = db.StringProperty()
  counter = db.IntegerProperty(default=0)
  data = db.TextProperty()
  latlng = db.GeoPtProperty()
