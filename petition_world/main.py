import cgi
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import pages
import services

def main():
  application = webapp.WSGIApplication([
                                      ('/', pages.RootRedirect),
                                      ('/learn', pages.LearnPage),
                                      ('/vote', pages.VotePage),
                                      ('/explore', pages.ExplorePage),
                                      ('/debug', pages.DebugPage),
                                      ('/add/random', pages.RandomAddService),
                                      ('/add/signer', pages.SignerAddService),
                                      ('/nonce', services.CryptographicNonceService),
                                      ('/info/votelocal', services.VotesInLocationService),
                                      ('/info/continents', services.ContinentsInfoService),
                                      ('/info/countries', services.CountriesInfoService),
                                      ('/info/states', services.StatesInfoService),
                                      ('/info/postcodes', services.PostcodesInfoService),
                                      ('/info/orgs', services.OrgsInfoService),
                                      ('/info/totals', services.TotalsInfoService),
                                      ('/clearcache', pages.MemcacheClearer)
                                      ],
                                     debug=True)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
