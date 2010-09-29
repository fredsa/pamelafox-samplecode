import logging

import gdata.auth
import gdata.spreadsheets.client
import gdata.spreadsheets.data
from django.shortcuts import render_to_response
from django.http import HttpResponse

from models.event import Event
import credentials

def main_page(request):
  return render_to_response('index.html', {})


# Example use: addevent?spreadsheet_key=tuUZenEu2BFpLXBMZ4iaL7Q
def add_event(request):
  event = Event()
  event.spreadsheet_key = request.GET.get('spreadsheet_key')
  event.worksheet_id = request.GET.get('worksheet_id', 'od6')
  event.save()
  return HttpResponse('Added')


# Example use: cancel?event=tuUZenEu2BFpLXBMZ4iaL7Q&attendee=stephaniel@google.com
def request_cancel(request):
  event_id = request.GET.get('event')
  attendee_id = request.GET.get('attendee')
  cancel_url = 'reallycancel?event=%s&attendee=%s' % (event_id, attendee_id)
  return render_to_response('request.html', {'cancel_url': cancel_url})


# Example use: reallycancel?event=tuUZenEu2BFpLXBMZ4iaL7Q&attendee=stephaniel@google.com
def cancel(request):
  event_id = request.GET.get('event')
  attendee_id = request.GET.get('attendee')
  try:
    event = Event.objects.get(spreadsheet_key=event_id)
    status = cancel_in_spreadsheet(event.spreadsheet_key, event.worksheet_id, attendee_id)
  except Event.DoesNotExist:
    status = cancel_in_spreadsheet(event_id, 'od6', attendee_id)
  return render_to_response('status.html', {'status': status})


def cancel_in_spreadsheet(spreadsheet_key, worksheet_id, attendee_id):
  client = gdata.spreadsheets.client.SpreadsheetsClient()
  client.auth_token = gdata.gauth.OAuthHmacToken(
      credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET,
      credentials.TOKEN_KEY, credentials.TOKEN_SECRET,
      gdata.gauth.ACCESS_TOKEN,
      next=None, verifier=None)

  list_feed = 'https://spreadsheets.google.com/feeds/list/%s/%s/private/full' % (spreadsheet_key, worksheet_id)

  # TODO: Maybe only search for a particular column name using sq=,
  # if we standardize that column name
  list_feed = list_feed + '?q=' + attendee_id
  feed = client.get_feed(list_feed,
                         desired_class=gdata.spreadsheets.data.ListsFeed)

  if len(feed.entry) > 1:
    return 'Error: Found multiple matching rows for id %s.' % attendee_id

  row = feed.entry[0]
  # TODO: Use standard column header?
  row.set_value('cancelled', 'Yes')
  client.Update(row)

  return 'We\'ve now marked you as cancelled for this event. Thanks for letting us know, we hope to see you at future events!'
