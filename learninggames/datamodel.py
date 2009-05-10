##
# Copyright 2008 Google Inc. 
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0
##

from google.appengine.ext import db

class NumberGame(db.Model):
   number = db.IntegerProperty()
   date = db.DateTimeProperty(auto_now_add=True)

class GeoGame(db.Model):
   latlng = db.GeoPtProperty()
   date = db.DateTimeProperty(auto_now_add=True)
   placename = db.StringProperty()

class GeoGameUserScore(db.Model):
  user = db.UserProperty()
  game_id = db.StringProperty()
  latlng = db.GeoPtProperty()
