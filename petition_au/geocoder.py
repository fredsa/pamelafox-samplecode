#!/usr/bin/python2.5
#
# Copyright 2009 Google Inc.
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0

"""A helper module for geocoding addresses over HTTP.

This module contains a function that sends a call to
the Google Maps API HTTP Geocoder to geocode an address.
"""

import urllib

from google.appengine.api import urlfetch
from google.appengine.ext import db


def GeocodeAddress(address):
  """Retrieves a lat/lng from the geocoder.

  Args:
    address: The address. Punctuation/case don't matter.
  Returns:
    A db.GeoPt() object if successful, None otherwise.
  """

  base_path = ('http://maps.google.com/maps/geo?output=csv&sensor=false'
               '&key=ABQIAAAAndLQTfJ9k_JvMh7lbOFC1RS4My7l3P1CJ6Hnc875WZ'
               'oO7BnwWBT9WQb3OhuPByEjaQs33G5wM5s5Ng&q=')
  enc_address = urllib.quote_plus(address)
  response = urlfetch.fetch(base_path + enc_address)
  if response.status_code == 200 and response.content.startswith('200'):
    [lat, lng] = [float(x) for x in response.content.split(',')[2:4]]
    return db.GeoPt(lat, lng)
  return None
