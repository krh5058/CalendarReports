#-------------------------------------------------------------------------------
# Name:        fledgling
# Purpose:
#
# Author:      krh5058
#
# Created:     22/04/2014
# Copyright:   (c) krh5058 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

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

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

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

    try:
        request = service.events().list(
##            calendarId='b4h134knp68e157iavnrrlfho4@group.calendar.google.com', ## MRI Slots
            calendarId='7pvr3e5ebphbtih6l1n2044ko4@group.calendar.google.com', ## Scanner Operator Availability
            singleEvents=True,
            orderBy="startTime",
            timeZone = "America/New_York",
            timeMin = "2014-04-21T00:00:00-00:00",
            timeMax = "2014-04-28T00:00:00-00:00"
            )
        # Loop until all pages have been processed.
        while request != None:
            # Get the next page.
            response = request.execute()
            # Accessing the response like a dict object with an 'items' key
            # returns a list of item objects (events).
            for event in response.get('items', []):
                # The event object is a dict object with a 'summary' key.
                print(event.get('summary', 'NO SUMMARY'))
                print(event.get('start', 'NO START'))
                print(event.get('end', 'NO END'))
                # Get the next request object by passing the previous request object to
                # the list_next method.
                request = service.events().list_next(request, response)

        input("Press Enter to continue...")
    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
          "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)
