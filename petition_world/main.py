import cgi
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import pages
import services

def main():
  application = webapp.WSGIApplication([
                                      ('/', pages.MainPage),
                                      ('/signup', pages.FormPage),
                                      ('/debug', pages.DebugPage),
                                      ('/map', pages.MapPage),
                                      ('/add/random', pages.RandomAddService),
                                      ('/add/signer', pages.SignerAddService),
                                      ('/nonce', services.CryptographicNonceService),
                                      ('/info/continents', services.ContinentsInfoService),
                                      ('/info/countries', services.CountriesInfoService),
                                      ('/info/states', services.StatesInfoService),
                                      ('/info/postcodes', services.PostcodesInfoService),
                                      ('/clearcache', pages.MemcacheClearer)
                                      ],
                                     debug=True)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
