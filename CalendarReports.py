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

# Development output
DEV = os.path.join(os.path.dirname(__file__), 'dev/')

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

    # Initialize service, data lists
    try:
        calendar_data = json.load(calendar_json)

        # timeMin
        if use_cache:
            cacheMax = datetime(2014,4,26,16,0,1)
            timeMinStr = cacheMax.strftime(Event.EventClass.strfmt)
        else:
            # Untested
            timeMinStr = None

        # timeMax, specify weeks in the future
        weeksFuture = 2
        timeMaxStr = (datetime.today() + timedelta(weeks=weeksFuture)).strftime(Event.EventClass.strfmt)

        scanop_data = calendar_data["calendars"]["scanop"]
        scanop = service.events().list(
            calendarId=scanop_data["calendarId"],
            singleEvents=(scanop_data["singleEvents"]=="True"),
            orderBy=scanop_data["orderBy"],
            timeZone = scanop_data["timeZone"],
            timeMin = timeMinStr,
            timeMax = timeMaxStr
            )
        scanop_events = {}

        mrislots_data = calendar_data["calendars"]["mrislots"]
        mrislots = service.events().list(
            calendarId=mrislots_data["calendarId"],
            singleEvents=(mrislots_data["singleEvents"]=="True"),
            orderBy=mrislots_data["orderBy"],
            timeZone = mrislots_data["timeZone"],
            timeMin = timeMinStr,
            timeMax = timeMaxStr
            )
        mrislots_events = {}
    finally:
        calendar_json.close()

    # Old cache of events
    if use_cache:
        print("--------------Start Cache...")
        try:
            print("--------------Start Scanner Operator Cache...")
            cache = os.listdir(HISTORY + "scanop/")
            for filename in cache:
                event_json = open(HISTORY + "scanop/" + filename)
                time_s = float(filename[:-5]) ## No file extension
                json_data = json.load(event_json)
                if Event.EventClass.validate(json_data):
                    scanop_events[time_s] = Event.EventClass(json_data)
                    print(datetime.fromtimestamp(time_s))
                event_json.close()

            print("--------------Start MRI Slots Cache...")
            cache = os.listdir(HISTORY + "mrislots/")
            for filename in cache:
                event_json = open(HISTORY + "mrislots/" + filename)
                time_s = float(filename[:-5]) ## No file extension
                json_data = json.load(event_json)
                if Event.EventClass.validate(json_data):
                    mrislots_events[time_s] = Event.EventClass(json_data)
                    print(datetime.fromtimestamp(time_s))
                event_json.close()
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        finally:
            print("--------------End Cache.")

    # HTTP Requests
    try:
        print("--------------Start Calendar HTTP Requests...")

        # Scanner Operator Availability
        # Loop until all pages have been processed.
        print("--------------Start Scanner Operator Requests...")
        while scanop != None:
            # Get the next page.
            response = scanop.execute()
            # Accessing the response like a dict object with an 'items' key
            # returns a list of item objects (events).
            for event in response.get('items', []):
                # The event object is a dict object.
                # Store event as EventClass
                if Event.EventClass.validate(event):
                    obj = Event.EventClass(event)
                    scanop_events[obj.get_start()] = obj
    ##                scanop_events.append(Event.EventClass(event))
                    print(datetime.fromtimestamp(obj.get_start()))

                    if write_cache:
                        outfile = open(HISTORY + "scanop/" + str(obj.get_start()) + '.json','w')
    ##                    outfile = open(HISTORY + "scanop/" + str(scanop_events[-1].start_s) + '.json','w')
                        json.dump(event,outfile)
                        outfile.close()

                # Get the next request object by passing the previous request object to
                # the list_next method.
                scanop = service.events().list_next(scanop, response)

        # MRI Slots
        # Loop until all pages have been processed.
        print("--------------Start MRI Slots Requests...")
        while mrislots != None:
            # Get the next page.
            response = mrislots.execute()
            # Accessing the response like a dict object with an 'items' key
            # returns a list of item objects (events).
            for event in response.get('items', []):
                # The event object is a dict object.
                # Store event as EventClass
                if Event.EventClass.validate(event):
                    obj = Event.EventClass(event)
                    mrislots_events[obj.get_start()] = obj
    ##                mrislots_events.append(Event.EventClass(event))
                    print(datetime.fromtimestamp(obj.get_start()))

                    if write_cache:
                        outfile = open(HISTORY + "mrislots/" + str(obj.get_start()) + '.json','w')
    ##                    outfile = open(HISTORY + "mrislots/" + str(mrislots_events[-1].start_s) + '.json','w')
                        json.dump(event,outfile)
                        outfile.close()

                # Get the next request object by passing the previous request object to
                # the list_next method.
                mrislots = service.events().list_next(mrislots, response)

        head = ['pi', 'project-id', 'full-event','date', 'start', 'end', 'duration', 'hrs-use-category','subject-id']
##
##        fwrite = csv.writer(csvfile, delimiter=',')
##        write_csv(fwrite,head)
        lastweek = (datetime.today() - timedelta(weeks=1)).timestamp()
        tomorrow = (datetime.today() + timedelta(days=1)).timestamp()
        for event in mrislots_events.keys():
            if (event > lastweek) and (event < tomorrow):
                print(mrislots_events[event].event)
                summary = mrislots_events[event].event.get('summary')
                print('Full Event:', summary)
                pi = re.search('\w{3}\d{1,4}',summary)
                if pi:
                    print('PI:',pi.group(0))
                proj = re.search('\w{1,4}',summary)
                if proj:
                    print('Project ID:',proj.group(0))
                print(mrislots_events[event].event.get('start').get('dateTime'))
                print(mrislots_events[event].event.get('end').get('dateTime'))
                print(mrislots_events[event].duration('m'))

        input("Press Enter to continue...")
    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
          "the application to re-authorize")
    finally:
        print("--------------End Calendar HTTP Requests.")

if __name__ == '__main__':
  main(sys.argv)
