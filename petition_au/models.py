##
# Copyright 2008 Google Inc. 
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0
##

from google.appengine.ext import db

class RegionCluster(db.Model):
  type = db.StringProperty()
  name = db.StringProperty()
  data = db.TextProperty()
  count = db.IntegerProperty()
  latlng = db.GeoPtProperty()
  state = db.StringProperty()

class PetitionSigner(db.Model):
  type = db.StringProperty()
  name = db.StringProperty()
  num = db.IntegerProperty()
  org_icon = db.StringProperty()
  streetinfo = db.StringProperty()
  state = db.StringProperty()
  city = db.StringProperty()
  postcode = db.IntegerProperty()
  latlng = db.GeoPtProperty()
