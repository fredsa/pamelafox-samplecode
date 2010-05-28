#!/usr/bin/python
#
# Copyright (C) 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A module to run wave robots on Django."""


import logging
import sys

from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response

import events


def CapabilitiesHandler(request, robot):
  # content-type
  return HttpResponse(robot.capabilities_xml(), content_type='text/xml')

def ProfileHandler(request, robot):
  """Handler to forward a request ot a handler of a robot."""
  # content type
  # Respond with proxied profile if name specified
  if 'name' in request.GET:
    response = robot.profile_json(request.GET['name'])
  else:
    response = robot.profile_json()
  return HttpResponse(response, content_type='text/plain')

def RobotEventHandler(request, robot):
  """Handler for the dispatching of events to various handlers to a robot.

  This handler only responds to post events with a JSON post body. Its primary
  task is to separate out the context data from the events in the post body
  and dispatch all events in order. Once all events have been dispatched
  it serializes the context data and its associated operations as a response.
  """
  if request.method == 'POST':
    json_body = request.raw_post_data
    if not json_body:
      return

    json_body = unicode(json_body, 'utf8')
    logging.info('Incoming: %s', json_body)
    json_response = robot.process_events(json_body)
    logging.info('Outgoing: %s', json_response)
    
    # Build the response.
    response = (json_response.encode('utf-8'))
    return HttpResponse(response, content_type='application/json; charset=utf-8')
  else:
    return HttpResponse('GET not implemented')


def operation_error_handler(event, wavelet):
  """Default operation error handler, logging what went wrong."""
  if isinstance(event, events.OperationError):
    logging.error('Previously operation failed: id=%s, message: %s',
                  event.operation_id, event.error_message)

def RobotVerifyTokenHandler(request, robot):
  """Handler for the token_verify request."""
  token, st = robot.get_verification_token_info()
  logging.info('token=' + token)
  if token is None:
    response = 'No token set'
    return
  if not st is None:
    if request.GET['st'] != st:
      response = 'Invalid st value passed'
      return
  response = token
  return HttpResponse(response)

def handle(request, robot):
  """Sets up the webapp handlers for this robot and starts listening.

    A robot is typically setup in the following steps:
      1. Instantiate and define robot.
      2. Register various handlers that it is interested in.
      3. Call Run, which will setup the handlers for the app.
    For example:
      robot = Robot('Terminator',
                    image_url='http://www.sky.net/models/t800.png',
                    profile_url='http://www.sky.net/models/t800.html')
      robot.register_handler(WAVELET_PARTICIPANTS_CHANGED, KillParticipant)
      run(robot)

    Args:
      robot: the robot to run. This robot is modified to use app engines
          urlfetch for posting http.
      debug: Optional variable that defaults to False and is passed through
          to the webapp application to determine if it should show debug info.
      log_errors: Optional flag that defaults to True and determines whether
          a default handlers to catch errors should be setup that uses the
          app engine logging to log errors.
      extra_handlers: Optional list of tuples that are passed to the webapp
          to install more handlers. For example, passing
            [('/about', AboutHandler),] would install an extra about handler
            for the robot.
  """
  # App Engine expects to construct a class with no arguments, so we
  # pass a lambda that constructs the appropriate handler with
  # arguments from the enclosing scope.
  robot.register_handler(events.OperationError, operation_error_handler)
  if request.path.find('_wave/capabilities.xml') > -1:
    return CapabilitiesHandler(request, robot)
  if request.path.find('_wave/robot/profile') > -1:
    return ProfileHandler(request, robot)
  if request.path.find('_wave/robot/jsonrpc') > -1:
    return RobotEventHandler(request, robot)
  if request.path.find('_wave/verify_token') > -1:
    return RobotVerifyTokenHandler(request, robot)
