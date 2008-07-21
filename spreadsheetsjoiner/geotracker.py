#!/usr/bin/python2.4
# -*- coding: latin-1 -*-
#
# Copyright 2008 Google Inc. All Rights Reserved.

import StringIO
import gdata.spreadsheet.service
import getpass
import csv
import gdata.docs
import gdata.docs.service
import geodata

countries = {
'AF': {},
'AX': {},
'AL': {},
'DZ': {},
'AS': {},
'AD': {},
'AO': {},
'AI': {},
'AQ': {},
'AG': {},
'AR': {},
'AM': {},
'AW': {},
'AU': {},
'AT': {},
'AZ': {},
'BS': {},
'BH': {},
'BD': {},
'BB': {},
'BY': {},
'BE': {},
'BZ': {},
'BJ': {},
'BM': {},
'BT': {},
'BO': {},
'BA': {},
'BW': {},
'BV': {},
'BR': {},
'IO': {},
'BN': {},
'BG': {},
'BF': {},
'BI': {},
'KH': {},
'CM': {},
'CA': {},
'CV': {},
'KY': {},
'CF': {},
'TD': {},
'CL': {},
'CN': {},
'CX': {},
'CC': {},
'CO': {},
'KM': {},
'CG': {},
'CD': {},
'CK': {},
'CR': {},
'CI': {},
'HR': {},
'CU': {},
'CY': {},
'CZ': {},
'DK': {},
'DJ': {},
'DM': {},
'DO': {},
'EC': {},
'EG': {},
'SV': {},
'GQ': {},
'ER': {},
'EE': {},
'ET': {},
'FK': {},
'FO': {},
'FJ': {},
'FI': {},
'FR': {},
'GF': {},
'PF': {},
'TF': {},
'GA': {},
'GM': {},
'GE': {},
'DE': {},
'GH': {},
'GI': {},
'GR': {},
'GL': {},
'GD': {},
'GP': {},
'GU': {},
'GT': {},
'GG': {},
'GN': {},
'GW': {},
'GY': {},
'HT': {},
'HM': {},
'VA': {},
'HN': {},
'HK': {},
'HU': {},
'IS': {},
'IN': {},
'ID': {},
'IR': {},
'IQ': {},
'IE': {},
'IM': {},
'IL': {},
'IT': {},
'JM': {},
'JP': {},
'JE': {},
'JO': {},
'KZ': {},
'KE': {},
'KI': {},
'KP': {},
'KR': {},
'KW': {},
'KG': {},
'LA': {},
'LV': {},
'LB': {},
'LS': {},
'LR': {},
'LY': {},
'LI': {},
'LT': {},
'LU': {},
'MO': {},
'MK': {},
'MG': {},
'MW': {},
'MY': {},
'MV': {},
'ML': {},
'MT': {},
'MH': {},
'MQ': {},
'MR': {},
'MU': {},
'YT': {},
'MX': {},
'FM': {},
'MD': {},
'MC': {},
'MN': {},
'ME': {},
'MS': {},
'MA': {},
'MZ': {},
'MM': {},
'NA': {},
'NR': {},
'NP': {},
'NL': {},
'AN': {},
'NC': {},
'NZ': {},
'NI': {},
'NE': {},
'NG': {},
'NU': {},
'NF': {},
'MP': {},
'NO': {},
'OM': {},
'PK': {},
'PW': {},
'PS': {},
'PA': {},
'PG': {},
'PY': {},
'PE': {},
'PH': {},
'PN': {},
'PL': {},
'PT': {},
'PR': {},
'QA': {},
'RE': {},
'RO': {},
'RU': {},
'RW': {},
'BL': {},
'SH': {},
'KN': {},
'LC': {},
'MF': {},
'PM': {},
'VC': {},
'WS': {},
'SM': {},
'ST': {},
'SA': {},
'SN': {},
'RS': {},
'SC': {},
'SL': {},
'SG': {},
'SK': {},
'SI': {},
'SB': {},
'SO': {},
'ZA': {},
'GS': {},
'ES': {},
'LK': {},
'SD': {},
'SR': {},
'SJ': {},
'SZ': {},
'SE': {},
'CH': {},
'SY': {},
'TW': {},
'TJ': {},
'TZ': {},
'TH': {},
'TL': {},
'TG': {},
'TK': {},
'TO': {},
'TT': {},
'TN': {},
'TR': {},
'TM': {},
'TC': {},
'TV': {},
'UG': {},
'UA': {},
'AE': {},
'GB': {},
'US': {},
'UM': {},
'UY': {},
'UZ': {},
'VU': {},
'VE': {},
'VN': {},
'VG': {},
'VI': {},
'WF': {},
'EH': {},
'YE': {},
'ZM': {},
'ZW': {}
}

worksheets = [ 
{'key': 'o01329000263537073075.6852866848434140453', 'id': 'od6', 'columns': []},
{'key': 'psxuHxrKOcRJ9RTqQaFljeg', 'id': 'od6', 'columns': []},
{'key': 'psxuHxrKOcRKuMWL2DYmQCg', 'id': 'od6', 'columns': []},
]

columns = []

email = 'emailhere'
password = 'passhere'

gd_client = gdata.docs.service.DocsService()
gd_client.email = email
gd_client.password = password
gd_client.ProgrammaticLogin()

gd_client2 = gdata.spreadsheet.service.SpreadsheetsService()
gd_client2.email = email
gd_client2.password = password
gd_client2.ProgrammaticLogin()

def getKeyForSpreadsheetEntry(entry):
  id_parts = entry.id.text.split('/')
  print id_parts
  key = id_parts[-1].replace('spreadsheet%3A', '')
  return key

ws_num = 1
for worksheet in worksheets:
  worksheet['num'] = ws_num
  list_feed = gd_client2.GetListFeed(worksheet['key'], worksheet['id'], visibility='private', projection='values')
  print list_feed.link[0].href, 
  print list_feed.link[1].href,
  print list_feed.link[2].href
  added_columns = False;
  worksheet['title'] = list_feed.title.text
  worksheet['link'] = list_feed.link[0].href
  for entry in list_feed.entry:
    # capitalize and trim the string, to try and match entries in the countries dict
    # note there may be issues with foreign characters used in the spreadsheet country names
    value_to_check = entry.title.text.strip().upper();
    #print value_to_check
    current_country_id = ''
    if countries.has_key(value_to_check):
     # in this case, the key is the ID
     current_country_id = value_to_check
    elif geodata.country_id_mappings.has_key(value_to_check):
     # in this case, the value is the ID
     current_country_id = geodata.country_id_mappings[value_to_check]
    if current_country_id != '':
      for custom_key in entry.custom.keys():
        #(todo) if theres a conflict - and this already exists, log an error message
        if entry.custom[custom_key].text is not None:
          countries[current_country_id][custom_key] = "%d__%s" % (ws_num, entry.custom[custom_key].text)
        if added_columns == False:
          worksheet['columns'].append(custom_key)
          columns.append(custom_key)
      added_columns = True
  ws_num = ws_num + 1

# eliminate duplicates in the columns list
columns_set = set(columns)

wsInfo_csv_arr = ['num,key,id,link,title,columns']
for worksheet in worksheets:
  wsInfo_csv_arr.append("%d,%s,%s,%s,%s,%s" % (worksheet['num'], worksheet['key'], worksheet['id'], worksheet['link'], worksheet['title'], '|'.join(worksheet['columns'])))

wsInfo_csv_str = '\n'.join(wsInfo_csv_arr)
virtual_csv_file = StringIO.StringIO(wsInfo_csv_str)
virtual_media_source = gdata.MediaSource(file_handle=virtual_csv_file, content_type='text/csv', content_length=len(wsInfo_csv_str))
db_entry = gd_client.UploadSpreadsheet(virtual_media_source, 'Geo Tracking Meta Info')
meta_key = getKeyForSpreadsheetEntry(db_entry)

csv_arr = []
header_arr = ['countryiso'];
for column in columns_set:
  if column != '':
    header_arr.append(column)
header_str = ','.join(header_arr)
csv_arr.append(header_str)

for country_id in countries:
  row_arr = [country_id]  
  country = countries[country_id]
  for column in columns_set:
    if not country.has_key(column) or country[column] is None:
      country[column] = ''
    row_arr.append('"' + country[column].replace(',', ' ').replace('\n', ' ') + '"')
  row_str = ','.join(row_arr)
  csv_arr.append(row_str)

csv_str = '\n'.join(csv_arr)

virtual_csv_file = StringIO.StringIO(csv_str)
virtual_media_source = gdata.MediaSource(file_handle=virtual_csv_file, content_type='text/csv', content_length=len(csv_str))
db_entry = gd_client.UploadSpreadsheet(virtual_media_source, 'Geo Tracking')
tracking_key = getKeyForSpreadsheetEntry(db_entry)


# Edit spreadsheet with location information
feed = gd_client2.GetListFeed('pelxSF-Eta6KbiekxtPLiFQ', 'od6')
row_data = {'metakey': meta_key, 'trackingkey': tracking_key, 'columns': header_str}
entry = gd_client2.UpdateRow(feed.entry[0], row_data)
if isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
  print 'Updated!'
