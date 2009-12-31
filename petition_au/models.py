#!/usr/bin/python2.5
#
# Copyright 2009 Google Inc.
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0

"""A module for the datastore model classes.

This module contains datastore model classes
for petition signers and clusters, as well
as constants for memcache key prefixes.
"""

from google.appengine.ext import db

MEMCACHE_MAXPOSTCODES = 'maxpostcode'
MEMCACHE_STATECLUSTER = 'statecluster_'


class RegionCluster(db.Model):
  """Stores information about the votes in a given region.

  Attributes:
    type: Indicates type of region, like 'postcode'.
    name: Name of the region, like '2009'.
    data: A serialized JSON of the signer data.
    count: The number of signers in this region.
    latlng: The lat/lng of the region centroid.
    state: The state that the region is part of, like 'NSW'.
  """
  type = db.StringProperty()
  name = db.StringProperty()
  data = db.TextProperty()
  count = db.IntegerProperty()
  latlng = db.GeoPtProperty()
  state = db.StringProperty()


class PetitionSigner(db.Model):
  """Stores information about a petition signer.

  Attributes:
    type: Type of signer, either 'org' or 'family'.
    name: Name of signer, given in form.
    num: Number in household or organization.
    org_icon: URL to an org icon, if specified.
    streetinfo: Street address, given in form.
    state: State, given in form. Must be AU state.
    city: City, given in form.
    postcode: Postcode, given in form.
    latlng: Calculated based on full address. May be None.
  """
  type = db.StringProperty()
  name = db.StringProperty()
  num = db.IntegerProperty()
  org_icon = db.StringProperty()
  streetinfo = db.StringProperty()
  state = db.StringProperty()
  city = db.StringProperty()
  postcode = db.IntegerProperty()
  latlng = db.GeoPtProperty()

  def GetClusterData(self):
    """Generates a dict of data about the signer, used for serialization."""

    clusterdata = {'lastname': self.name,
                   'streetinfo': self.streetinfo,
                   'city': self.city,
                   'state': self.state,
                   'postcode': self.postcode,
                   'lat': self.latlng.lat,
                   'lng': self.latlng.lon}
    return clusterdata
