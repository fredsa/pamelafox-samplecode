import cgi
import os
import random
import logging
import hashlib
import csv
import re

import urllib2


from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import images

from django.utils import simplejson

import models
import geocoder
import util
import geodata
import geodata2

class RootRedirect(webapp.RequestHandler):
  def get(self):
    skin = self.request.get('skin') or 'main'
    if skin == 'main':
      self.redirect('/vote?skin=mini')
    else:
      self.redirect('/vote?skin=' + skin)

class BasePage(webapp.RequestHandler):
  def get(self):
    self.render(self.getTemplateFilename(), self.getTemplateValues())

  def getTemplateValues(self, page_title, page_num):
    skin = self.request.get('skin') or 'main'
    if not skin in ['main', 'mini','large']:
      skin = 'main' 

    bg_color = self.request.get('bg_color')
    website = self.request.get('website')
    tabSet = self.request.get('tabSet')

    if len(tabSet) == 0:
      tabSet = '<map name="Map" id="Map"> \
          <area shape="rect" coords="1,1,189,39" href="vote?skin=mini&amp;bg_color=%s" /> \
          <area shape="rect" coords="204,10,250,39" href="vote?skin=mini&amp;bg_color=%s" /> \
          <area shape="rect" coords="251,10,323,39" href="explore?skin=mini&amp;bg_color=%s" /> \
          <area shape="rect" coords="324,10,381,39" href="learn?skin=mini&amp;bg_color=%s" /> </map>' % (bg_color,bg_color,bg_color,bg_color)
      imageColor = 'Green'
    else:
       tabSet = '<map name="Map" id="Map" > \
          <area shape="rect" coords="12,10,60,39" href="vote?skin=mini&amp;bg_color=%s&amp;tabSet=Blue" /> \
          <area shape="rect" coords="60,10,132,39" href="explore?skin=mini&amp;bg_color=%s&amp;tabSet=Blue" /> \
          <area shape="rect" coords="133,10,190,39" href="learn?skin=mini&amp;bg_color=%s&amp;tabSet=Blue" /> \
            <area shape="rect" coords="219,10,400,39" href="vote?skin=mini&amp;bg_color=%s&amp;tabSet=Blue" /> </map>' % (bg_color,bg_color,bg_color,bg_color)
       imageColor = 'Blue'
        
    template_values = {
      'page_title': page_title,
      'page_num': page_num,
      'skin': skin,
      'bg_color': bg_color,
      'website': website,
      'imageMap': tabSet,
      'imageColor': imageColor,
      #TODO: start using these in the templates
      'vote_href': "/vote?skin=%s&amp;bg_color=%s&amp;website=%s" % (skin, bg_color, website),
      'explore_href': "/explore?skin=%s&amp;bg_color=%s&amp;website=%s" % (skin, bg_color, website),
      'learn_href': "/learn?skin=%s&amp;bg_color=%s&amp;website=%s" % (skin, bg_color, website)
    }
    return template_values

  def getTemplateFilename(self):
    return "base.html"

  def render(self, filename, template_values):
    path = os.path.join(os.path.dirname(__file__), 'templates', template_values['skin'], filename)
    logging.info(path)
    self.response.out.write(template.render(path, template_values))

class LearnPage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Learn', 0)
    return template_values

  def getTemplateFilename(self):
    return "learn.html"
    
    
    
class VisulisationPage(BasePage):
    def getTemplateValues(self):
        template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Learn', 0)
        return template_values

    def getTemplateFilename(self):
        return "visual.html"

class VotePage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Vote', 1)
    return template_values

  def getTemplateFilename(self):
    return "vote.html"


class ExplorePage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Explore', 2)
    return template_values

  def getTemplateFilename(self):
    explore = self.request.get('version')
    if len(explore) == 0:
        return "explore.html"
    else:
        return "exploreVisual.html"

class TermsPage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Terms', 3)
    return template_values

  def getTemplateFilename(self):
    return "terms.html"

class RegisterPage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Register', 4)
    return template_values

  def getTemplateFilename(self):
    return "register.html"

class EmbedPage(BasePage):
  def getTemplateValues(self):
    template_values = BasePage.getTemplateValues(self, 'Show Your Vote: Embed', 5)
    return template_values

  def getTemplateFilename(self):
    return "embed.html"

class HostAddService(webapp.RequestHandler):
  def post(self):
    host = models.PetitionHost()
    host.host_name = self.request.get('host_name')
    host.host_email = self.request.get('host_email')
    host.host_website = self.request.get('host_website')
    host.host_bgcolor = self.request.get('host_bgcolor')
#    if os.environ['SERVER_SOFTWARE'].startswith('Development'):
    util.sendEmbedMail(host.host_email, host.host_bgcolor, host.host_website)
#    else:
#      deferred.defer(util.sendEmbedMail,
#        host.host_email, host.host_bgcolor, host.host_website
#      )
    host.put()
    self.redirect(
      "/embed?skin=%s&bg_color=%s&website=%s" % (
        self.request.get('skin'), self.request.get('bg_color'),
        host.host_website
      )
    )
    
class UploadPage(webapp.RequestHandler):
  def get(self):
      self.response.out.write('<form enctype="multipart/form-data" method="post" action="/upload">')
      self.response.out.write('<input type="file" name="csv" />')
      self.response.out.write('<input type="submit" />')
      self.response.out.write('</form>')
  def post(self):
      csvFile = self.request.get("csv")
      logging.info(csvFile)
      #for some reason app engine has no os.linesep?
      #i am assuming something some where is taking care of line endings
      reader = csv.reader(csvFile.split('\n'))
      
      for line in reader:
         if len(line) > 1: 
           logging.info(line)
           countryCode = line[0]
           countryVote = filter(lambda x: x.isdigit(), line[1])
           if countryCode in geodata.countries:
              util.addMassVotes(countryCode,countryVote)
              self.response.out.write('uploaded %s votes for %s<br />' % ( countryVote,countryCode))
           else:
              self.response.out.write('invalid country code %s' % (countryCode))
              #add some where
              

class DebugPage(webapp.RequestHandler):
  def get(self):
    countryCode = self.request.get('countryCode')
    if not countryCode:
      countryCode = 'AU'
    self.response.out.write("<table>")
    self.write("countryCode", countryCode)
    self.write("getCountryVotesInStore", util.getCountryVotesInStore(countryCode))
    self.write("getCountryVotesPerPostcodeInStore", util.getCountryVotesPerPostcodeInStore(countryCode))
    self.write("getCountryVotes", util.getCountryVotes(countryCode))
    self.write("getTotalVotes", util.getTotals())
    self.response.out.write("</table>")
    self.response.out.write("<form action=/addrandom?countryCode=AU method=get><input type=submit value=RandomAU></form>")
    self.response.out.write("<form action=/clearcache?countryCode=AU method=get><input type=submit value=ClearMemcacheAU></form>")

  def write(self, header, info):
    self.response.out.write("<tr><td>" + header + "</td><td>" + str(info) + "</td></tr>")

class MemcacheClearer(webapp.RequestHandler):
  def get(self):
    memcache.flush_all()

class JSONImport(webapp.RequestHandler):
  def get(self):
    file = self.request.get('file')
    url = "http://vote-earth-locations.hollersydney.com.au/" + file
    result = urlfetch.fetch(url)
    if result.status_code == 200:
      feed = simplejson.loads(result.content)
      locations = feed["locations"]
      for location in locations:
        fields = location["fields"]
        countryName = (fields["country"]).upper()
        if geodata2.country_id_mappings.has_key(countryName):
          country = geodata2.country_id_mappings[(fields["country"]).upper()]
          if country is not "US" and country is not "AU":
            query = db.Query(models.PetitionSigner)
            created_at = fields["created_at"]
            query.filter('name =', created_at)
            signer = query.get()
            if signer is None:
              signer = models.PetitionSigner()
              signer.country = country
              signer.latlng = db.GeoPt(float(fields["longitude"]), float(fields["latitude"]))
              signer.name = created_at # using this since we need to store this somewhere, it's basically the unique ID
              signer.state = ''
              signer.postcode = fields["postcode"]
              deferred.defer(util.addSignerToClusters, signer, signer.latlng)
              self.response.out.write("Adding from: " + country + "<br>")
            else:
              self.response.out.write("Already saw: " + created_at + "<br>")
          else:
            self.response.out.write("<b>Ignoring from: </b>" + country + "<br>")
        else:
          self.response.out.write("<b>Could not map: </b>" + fields["country"] + "<br>")

class RandomAddService(webapp.RequestHandler):
  def get(self):
    signer = models.PetitionSigner()
    signer.name = "Random"
    signer.num = 2
    signer.email = "random@google.com"
    signer.streetinfo = "1 Main St"
    signer.city = "Random"
    countryCode = self.request.get("countryCode")
    if not countryCode:
      possibleCountries = geodata.countries
      countryCode = random.choice(possibleCountries.keys())
    if util.countryHasStates(countryCode):
      possibleStates = geodata.countries[countryCode]["states"]
      signer.state = random.choice(possibleStates.keys())
      signer.postcode = signer.state + str(random.randrange(1,100))
    else:
      signer.state = countryCode + "Random"
      signer.postcode = countryCode + str(random.randrange(1,100))
    signer.country = countryCode
    signer.latlng = db.GeoPt(0,0)
    signer.put()
    self.response.out.write(signer.country + "<br>")
    self.response.out.write(signer.state)
    util.addSignerToClusters(signer)



    url = "http://www.google.com/"
    try:
      result = urllib2.urlopen(url)
      doSomethingWithResult(result)
    except urllib2.URLError, e:
      handleError(e)

class TwitterPage(BasePage):
        def getTemplateValues(self):
          template_values = BasePage.getTemplateValues(self, 'Show Your Vote: twitter feed', 5)
          return template_values

        def getTemplateFilename(self):
          return "twitter.html"
          
class UpdateTwitter(webapp.RequestHandler):
    def get(self):
         try:
             request = 'http://search.twitter.com/search.json?q=earthhour' 
             twitterReponse = urllib2.urlopen(request).read()
             if len(twitterResponse) > 0:
                memcache.delete('twitter',0)
                query = db.Query(models.TwitterFeed)
                result = query.get()
                logging.info(twitterResponse)
                if result is None:
                     mass = models.TwitterFeed()
                     mass.twitterJson = twitterReponse
                     result = mass;
                else:
                    result.twitterJson = twitterReponse;
              
                result.put()   
                memcache.add('twitter',result,600)
         except urllib2.URLError, e:
            logging.error('twitter update failed')
            
class SignerAddService(webapp.RequestHandler):
  def post(self):    
    skin = 'mini'
    if self.request.get('skin') != '':
      skin = self.request.get('skin') 
        
    originalNonce = self.request.cookies.get('nonce', None)
    hashedNonce = self.request.get('nonce')
    cachedVal = originalNonce and memcache.get(originalNonce)
    personName = self.request.get('person_name')
    if (hashedNonce and originalNonce and cachedVal is not None and hashlib.sha1(originalNonce).hexdigest() == hashedNonce):
      logging.info("Signature accepted: " + personName)
      signer = self.createSignerFromParams(self.request)
      memcache.delete(originalNonce, 0)
      self.response.headers.add_header('Set-Cookie', 'latlng=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT; path=/' % (str(signer.latlng.lat) + ',' + str(signer.latlng.lon)))
      # Remove the nonce cookie
      self.response.headers.add_header('Set-Cookie', 'nonce=; expires=Fri, 31-Dec-1980 23:59:59 GMT; path=/')
      #not set so chanes are it was not set  
      self.redirect('/explore?location=%s&skin=%s' % (self.request.get('postcode'),skin))
    else:
      # Spam
      if not hashedNonce:
        logging.info("Marked as spam (no hashed nonce): " + personName)
      elif not originalNonce:
        logging.info("Marked as spam (no original nonce): " + personName)
      elif cachedVal is None:
        logging.info("Marked as spam (no cached value): " + personName)
      elif not (hashlib.sha1(originalNonce).hexdigest() == hashedNonce):
        logging.info("Marked as spam (nonce did not match): " + personName)
      else:
        logging.info("Marked as spam (unknown reason): " + personName)
     
        self.redirect('/')

  # test with: /add/signer?person_name=Pamela&country=AU&state=NSW&postcode=2009&lat=-33.869709&lng=151.19393
  def get(self):
    #TODO: Check for whitelisted referrers
    self.createSignerFromParams(self.request)
    self.response.out.write('Queued')

  def createSignerFromParams(self, request):
    signer = models.PetitionSigner()
    # defaults to a person
    if not self.request.get('org_name') or self.request.get('org_name') == '':
      signer.type = 'person'
      signer.name = self.request.get('person_name')
      signer.gfc_id = self.request.get('person_gfc_id')
    else:
      signer.type = 'org'
      signer.name = self.request.get('org_name')
      signer.email = self.request.get('email')
      signer.streetinfo = self.request.get('streetinfo')
      #keeps the javascript failing
      logo = self.request.get("org_icon")
      #something some what sane for an image
      if len(logo) > 10:
        signer.org_icon_hosted = db.Blob(images.resize(logo,32,32))
        signer.org_icon = 'info/logo?orgName=%s' % signer.name
      else:
        logging.info("no image added")
        #put an empty string in to stop it falling over
        signer.org_icon = str('')
  
    signer.city = self.request.get('city')
    signer.state = self.request.get('state')
    signer.country = self.request.get('country')
    signer.postcode = self.request.get('postcode')
    signer.host_website = self.request.get('website')
    if self.request.get('lat') and self.request.get('lng'):
      #TODO: We used to get two lat/lngs. What happened?
      signer.latlng = db.GeoPt(float(self.request.get('lat')), float(self.request.get('lng')))
    if os.environ['SERVER_SOFTWARE'].startswith('Development'):
      util.addSignerToClusters(signer, signer.latlng)
    else:
      deferred.defer(util.addSignerToClusters, signer, signer.latlng)
    return signer

