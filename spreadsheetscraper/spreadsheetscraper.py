#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.

"""One-line documentation for importer module.

A detailed description of importer.
"""

import gdata.spreadsheet.service

worksheet = {
  'key': '0Ai4sPX0Iqn_vdFV3UWVEc18wejBUNm9tb1k0cDhZdlE',
  'id': 'od6'
  }

def main():
  gd_client2 = gdata.spreadsheet.service.SpreadsheetsService()
  list_feed = gd_client2.GetListFeed(worksheet['key'], worksheet['id'],
                                     visibility='public', projection='values')
  ConvertFeed(list_feed)

def ConvertFeed(feed):
  feed_list = []
  for i, entry in enumerate(feed.entry):
    feed_list.append({})
    if isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
      # Print this row's value for each column (the custom dictionary is
      # built using the gsx: elements in the entry.)
      for key in entry.custom: 
        feed_list[i][key] = entry.custom[key].text
  print str(feed_list)

def PrintFeed(feed):
  for i, entry in enumerate(feed.entry):
    if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
      print '%s %s\n' % (entry.title.text, entry.content.text)
    elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
      print '%s %s %s' % (i, entry.title.text, entry.content.text)
      # Print this row's value for each column (the custom dictionary is
      # built using the gsx: elements in the entry.)
      print 'Contents:'
      for key in entry.custom:  
        print '  %s: %s' % (key, entry.custom[key].text) 
      print '\n',
    else:
      print '%s %s\n' % (i, entry.title.text)

if __name__ == '__main__':
  main()
