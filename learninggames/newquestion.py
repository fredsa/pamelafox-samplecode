##
# Copyright 2008 Google Inc. 
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0
##
import random
import pickle
from datetime import datetime

from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.db import GeoPt
from google.appengine.api import memcache
from google.appengine.api import users

from django.utils import simplejson

from datamodel import *

MEMCACHE_CURRENTQUESTION = 'currentquestion'

class NewQuestionHandler(webapp.RequestHandler):
  def get(self):
    url = "http://spreadsheets.google.com/feeds/list/p9pdwsai2hDO9TzAf5XGncQ/od6/public/values?alt=json"
    result = urlfetch.fetch(url)
    if result.status_code == 200:
      feedOBJ = simplejson.loads(result.content)
      if feedOBJ["feed"]:
        feedEntries = feedOBJ["feed"]["entry"]
        randInt = random.randint(0, (len(feedEntries)-1))
        location = feedEntries[randInt]

        geoGame = GeoGame()
        geoGame.latlng = GeoPt(location["gsx$latitude"]["$t"],
                               location["gsx$longitude"]["$t"])
        geoGame.placename = location["gsx$place"]["$t"]
        geoGame.put()

        self.response.out.write("New Question: %s" % geoGame.placename)
        memcache.delete(MEMCACHE_CURRENTQUESTION)
    else:
      self.response.out.write("Error getting feed")

class CurrentQuestionHandler(webapp.RequestHandler):
  def get(self):
    questionString = memcache.get(MEMCACHE_CURRENTQUESTION)
    if questionString is not None:
      questionJSON = pickle.loads(questionString)
    else:
      query = db.Query(GeoGame)
      query.order('-date')
      currentQuestion = query.get()
      timediff = datetime.now() - currentQuestion.date
      questionOBJ = {
             "id": currentQuestion.key().id_or_name(),
             "placename":currentQuestion.placename,
             "lat":currentQuestion.latlng.lat,
             "lng":currentQuestion.latlng.lon,
             "secondsleft": (60 - timediff.seconds)}
      questionJSON = simplejson.dumps(questionOBJ)
      memcache.set(MEMCACHE_CURRENTQUESTION, pickle.dumps(questionJSON), 1)
    self.response.out.write("%s" % questionJSON)

class UserAnswerHandler(webapp.RequestHandler):
  def get(self):
    latlng_string = self.request.get("latlng")
    latlng = GeoPt(latlng_string.split(",")[0], latlng_string.split(",")[1])
    user_score = GeoGameUserScore()
    user_score.user = users.get_current_user()
    user_score.latlng = latlng
    user_score.game_id = self.request.get("game_id")
    user_score.put()
    self.response.out.write("posted")

class AllAnswersHandler(webapp.RequestHandler):
  def get(self):
    game_id = self.request.get("id")
    query = db.Query(GeoGameUserScore)
    query.filter('game_id =', game_id)
    results = []
    for result in query:
      if result.user is None:
        nickname = 'anon'
      else:
        nickname = result.user.nickname()
      results.append({"user_name": nickname,
                      "lat": result.latlng.lat,
                      "lng": result.latlng.lon});
    results_json = simplejson.dumps(results)
    self.response.out.write("%s" % results_json)

application = webapp.WSGIApplication(
                                       [('/geogame/newquestion',
                                         NewQuestionHandler),
                                        ('/geogame/useranswer',
                                         UserAnswerHandler),
                                        ('/geogame/allanswers',
                                         AllAnswersHandler),
                                        ('/geogame/currentquestion',
                                         CurrentQuestionHandler)],
                                       debug=True)
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
