#!/usr/bin/python2.5
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Tests for geocoder."""

import unittest

from google.appengine.api import urlfetch
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub

import geocoder


class GeocoderTest(unittest.TestCase):

  def setUp(self):
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())

  def testGeocodeKnownAddress(self):
    latlng = geocoder.GeocodeAddress('2016,AU')
    self.assertEqual(latlng.lat, -33.8929561)
    self.assertEqual(latlng.lon, 151.2058735)
  
  def testGeocodeBadAddress(self):
    latlng = geocoder.GeocodeAddress('sdfsdfsfsdf')
    self.assertEqual(latlng, None)


if __name__ == '__main__':
  unittest.main()
