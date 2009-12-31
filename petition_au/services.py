#!/usr/bin/python2.5
#
# Copyright 2009 Google Inc.
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0

"""The module that handles requests for services.

This module includes a class for setting up the datastore,
a class for generating cluster JSON, and a class for adding
a petition signer to the datastore.
"""

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import memcache

from django.utils import simplejson

import models
import geocoder
import geodata


class Setup(webapp.RequestHandler):
  """Sets up the datastore with a cluster for each state. Use only once."""

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


class Clusters(webapp.RequestHandler):
  """Generates a JSON with cluster data.

  Iterates through each state, looking for the cluster data
  in memcache first. If it doesn't find it, it performs a
  datastore query and fills in the cache with the result.
  """

  def get(self):
    data = {}
    data['states'] = {}

    for state in geodata.states:
      data['states'][state['name']] = self.GetStateData(state)
    self.response.out.write(simplejson.dumps(data))

  def GetStateData(self, state):
    """Gets the data about each state and its child postcodes.

    Args:
      state: The state code, like 'NSW' or 'VIC'.

    Returns:
      A dict with the lat/lng, count, and list of postcode data.
    """
    state_data_str = memcache.get(models.MEMCACHE_STATECLUSTER + state['name'])
    if state_data_str is None:
      query = db.Query(models.RegionCluster)
      query.filter('type =', 'postcode')
      query.filter('state =', state['name'])
      results = query.fetch(1000)

      state_data = {}
      state_data['lat'] = state['lat']
      state_data['lng'] = state['lng']
      state_data['count'] = len(results)
      state_data['postcodes'] = []
      for result in results:
        state_data['postcodes'].append(simplejson.loads(result.data))
        memcache.set(models.MEMCACHE_STATECLUSTER + state['name'],
                     simplejson.dumps(state_data))
    else:
      state_data = simplejson.loads(state_data_str)
    return state_data


class Signup(webapp.RequestHandler):
  """Service called by the signup form for adding new signers."""

  def post(self):
    signer = self.CreateSignerFromRequest()
    url = '/map?postcode=%s&state=%s' % (str(signer.postcode), signer.state)
    self.redirect(url)

  def CreateSignerFromRequest(self):
    """Creates a new signer entity from the FORM parameters.

    Returns:
      The newly created signer object.
    """

    signer = models.PetitionSigner()
    signer.type = self.request.get('type')
    if signer.type == 'family':
      signer.name = self.request.get('family_name')
      signer.num = int(self.request.get('family_num'))
    elif signer.type == 'org':
      signer.name = self.request.get('org_name')
      signer.num = int(self.request.get('org_num'))
      signer.org_icon = self.request.get('org_icon')
    signer.email = self.request.get('email')
    signer.streetinfo = self.request.get('streetinfo')
    signer.city = self.request.get('city')
    signer.state = self.request.get('state')
    signer.postcode = int(self.request.get('postcode'))
    address = '%s %s %s %s' % (signer.streetinfo, signer.city,
                               signer.state, str(signer.postcode))
    latlng = geocoder.GeocodeAddress(address)
    if latlng is not None:
      signer.latlng = latlng
    signer.put()
    self.AddSignerToClusters(signer)
    return signer

  def AddSignerToClusters(self, signer):
    """Adds signer to the appropriate postcode cluster."""

    cluster_data = signer.GetClusterData()
    query = db.Query(models.RegionCluster)
    query.filter('type =', 'postcode')
    query.filter('name =', str(signer.postcode))
    result = query.get()
    if result is None:
      postcode_cluster = models.RegionCluster()
      postcode_cluster.type = 'postcode'
      postcode_cluster.name = str(signer.postcode)
      postcode_cluster.state = signer.state
      postcode_cluster.data = simplejson.dumps([cluster_data])
      postcode_cluster.count = 1
      latlng = geocoder.GeocodeAddress(str(signer.postcode) + ', AU')
      if latlng is not None:
        postcode_cluster.latlng = latlng
    else:
      postcode_cluster = result
      postcode_cluster.count += 1
      data = simplejson.loads(postcode_cluster.data)
      data.append(cluster_data)
      postcode_cluster.data = simplejson.dumps(data)
    postcode_cluster.put()
