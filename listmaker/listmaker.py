"""
This script can be used to turn a Python list into a Twitter list.

This script was based off the code from this GPLv3 project:
http://code.google.com/p/friends2list/
"""

import urllib2
import urllib
import getpass
import base64
import string
import json
import sys
import simplejson

import userlist

# Make a request and return the parsed JSON
def req(url, data={'hola': 'adios'}, post=0):
  enc = urllib.urlencode(data)
  if not post:
    url += '?' + enc
  r = urllib2.Request(url)
  r.add_header('Authorization', auth_header)
  if post:
    r.add_data(enc)
  try:
    respuesta = urllib2.urlopen(r)
  except urllib2.HTTPError:
    return 0
  except urllib2.URLError:
    raise
  else:
    return simplejson.load(respuesta)

# Ask for credentials
user = raw_input('Your Twitter username: ')
pwd = getpass.getpass('Your Twitter password: ')
print 'Authenticating...'

#Note: Basic authentication for Twitter API will cease working on June 30, 2010
credentials = base64.encodestring('%s:%s' % (user, pwd))
auth_header = string.strip('Basic %s' % credentials)

#validacion
if req('http://twitter.com/account/verify_credentials.json')==0:
  sys.exit('Couldn\'t authenticate you! :(')
else:
  print 'Welcome @%s!' % (user)

#list name input
list_name = raw_input('New Twitter List name: ')

#list name input
list_descrip = raw_input('..and description: ')

# Create the new list
print 'Attempting to create list...'
api_url = 'http://api.twitter.com/1/%s/lists.json' % user
new_list = req(api_url,
               {'name': list_name,
                'description': list_descrip},
               1)
list_id = new_list['id']
print '@%s/%s has been created' % (user,list_name)

print 'Will start to add users now...'

# Add users to new list
api_url = 'http://api.twitter.com/1/%s/%s/members.json' % (user, list_id)
for u in userlist.usernames:
  a = req(api_url,
          {'list_id': list_id,
           'id': u},
          1)
  print '@%s added' % (u)

print 'Done! :) Now you can see your list at http://www.twitter.com/%s/%s' % (user, list_name)
