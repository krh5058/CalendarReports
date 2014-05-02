#-------------------------------------------------------------------------------
# Name:        CalendarReports
# Purpose:     Retrieve data from SLEIC calendars for reporting
#
# Author:      Ken Hwang
#
# Created:     22/04/2014
# Copyright:   (c) krh5058 2014
# Licence:     Derivative work of skeleton application for Calendar API (copyright below)

# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#`
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#-------------------------------------------------------------------------------

"""Command-line skeleton application for Calendar API.
Usage:
  $ python CalendarReports.py

You can also get help on all the command-line flags the program understands
by running:

  $ python CalendarReports.py --help

"""

# Skeleton imports
import argparse
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Additional imports
from datetime import timedelta, datetime
import Event
import re
import json

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])

# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/561458633478/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'config/client_secrets.json')

# CALENDARS is the name of the file containing data fields to construct a Google Calendar API service request
CALENDARS = os.path.join(os.path.dirname(__file__), 'config/calendars.json')

# History directory for cache read and write
use_cache = True
write_cache = False
HISTORY = os.path.join(os.path.dirname(__file__), 'history/')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

# Main
def main(argv):
    # Parse the command-line flags.
    flags = parser.parse_args(argv[1:])

    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = file.Storage('sample.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        print('Using storage...')
        credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    service = discovery.build('calendar', 'v3', http=http)

    # Open calendars.json
    try:
        calendar_json = open(CALENDARS)
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))

    try:
        calendar_data = json.load(calendar_json)

        if use_cache:
            cacheMax = "2014-04-26T16:00:01-04:00"
        else:
            # Untested
            cacheMax = None

        scanop_data = calendar_data["calendars"]["scanop"]
        scanop = service.events().list(
            calendarId=scanop_data["calendarId"], ## Scanner Operator Availability
            singleEvents=(scanop_data["singleEvents"]=="True"),
            orderBy=scanop_data["orderBy"],
            timeZone = scanop_data["timeZone"],
            timeMin = cacheMax
##            timeMax = "2014-04-28T00:00:00-00:00"
            )
    ##        mrislots = service.events().list(
    ##            calendarId='b4h134knp68e157iavnrrlfho4@group.calendar.google.com', ## MRI Slots
    ##            singleEvents=True,
    ##            orderBy="startTime",
    ##            timeZone = "America/New_York",
    ####            TODO: Perform weekly/daily split
    ##            timeMin = "2014-04-21T00:00:00-00:00",
    ##            timeMax = "2014-04-28T00:00:00-00:00"
    ##            )
    finally:
        calendar_json.close()

    if use_cache:
        print("Start Cache...")
        try:
            cache = os.listdir(HISTORY)
            for filename in cache:
                print(datetime.fromtimestamp(float(filename[:-5])))
                event_json = open(HISTORY + filename)
                Event.EventClass(json.load(event_json))
                event_json.close()
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        finally:
            print("End Cache.")

    try:
        print("Start Calendar HTTP Requests...")
        # Loop until all pages have been processed.
        while scanop != None:
            # Get the next page.
            response = scanop.execute()
            # Accessing the response like a dict object with an 'items' key
            # returns a list of item objects (events).
            for event in response.get('items', []):
                # The event object is a dict object.
                # Store event as EventClass
                Event.EventClass(event)
                print(datetime.fromtimestamp(Event.EventClass.all_events[-1].start_s))

                if write_cache:
                    outfile = open(HISTORY + str(Event.EventClass.all_events[-1].start_s) + '.json','w')
                    json.dump(event,outfile)
                    outfile.close()

                # Get the next request object by passing the previous request object to
                # the list_next method.
                scanop = service.events().list_next(scanop, response)

        input("Press Enter to continue...")
    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
          "the application to re-authorize")
    finally:
        print("End Calendar HTTP Requests.")

if __name__ == '__main__':
  main(sys.argv)
