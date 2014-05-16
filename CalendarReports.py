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
from utils import Event
from utils import resources
import re
import json

# Developer parameters
debug = True

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])

# File path
filename = os.path.dirname(__file__)

# Flags for cache read and write
use_cache = True
write_cache = False

# Main
def main(argv):

##    # Parse the command-line flags.
##    flags = parser.parse_args(argv[1:])

##    obj = resources.DataClass(debug)

    # Format directory structure
    dirObj = resources.Directory(debug,path=filename)
    dirObj.define_paths()

##    # Configure requests
##    configObj = resources.Configuration(dirObj,debug)
##
##    # Read event history
##    histObj1 = resources.History(path=dirObj.directories['HISTORY'],source='scanop')
##    histObj1.read()
##    histObj2 = resources.History(path=dirObj.directories['HISTORY'],source='mrislots')
##    histObj2.read()

    print('done')
##
##    # Old cache of events
##    if use_cache:
##        print("--------------Start Cache...")
##        try:
##            print("--------------Start Scanner Operator Cache...")
##            cache = os.listdir(HISTORY + "scanop/")
##            for filename in cache:
##                event_json = open(HISTORY + "scanop/" + filename)
##                time_s = float(filename[:-5]) ## No file extension
##                json_data = json.load(event_json)
##                if Event.EventClass.validate(json_data):
##                    scanop_events[time_s] = Event.EventClass(json_data)
##                    print(datetime.fromtimestamp(time_s))
##                event_json.close()
##
##            print("--------------Start MRI Slots Cache...")
##            cache = os.listdir(HISTORY + "mrislots/")
##            for filename in cache:
##                event_json = open(HISTORY + "mrislots/" + filename)
##                time_s = float(filename[:-5]) ## No file extension
##                json_data = json.load(event_json)
##                if Event.EventClass.validate(json_data):
##                    mrislots_events[time_s] = Event.EventClass(json_data)
##                    print(datetime.fromtimestamp(time_s))
##                event_json.close()
##        except IOError as e:
##            print("I/O error({0}): {1}".format(e.errno, e.strerror))
##        finally:
##            print("--------------End Cache.")
##
##    # HTTP Requests
##    try:
##        print("--------------Start Calendar HTTP Requests...")
##
##        # Scanner Operator Availability
##        # Loop until all pages have been processed.
##        print("--------------Start Scanner Operator Requests...")
##        while scanop != None:
##            # Get the next page.
##            response = scanop.execute()
##            # Accessing the response like a dict object with an 'items' key
##            # returns a list of item objects (events).
##            for event in response.get('items', []):
##                # The event object is a dict object.
##                # Store event as EventClass
##                if Event.EventClass.validate(event):
##                    obj = Event.EventClass(event)
##                    scanop_events[obj.get_start()] = obj
##    ##                scanop_events.append(Event.EventClass(event))
##                    print(datetime.fromtimestamp(obj.get_start()))
##
##                    if write_cache:
##                        outfile = open(HISTORY + "scanop/" + str(obj.get_start()) + '.json','w')
##    ##                    outfile = open(HISTORY + "scanop/" + str(scanop_events[-1].start_s) + '.json','w')
##                        json.dump(event,outfile)
##                        outfile.close()
##
##                # Get the next request object by passing the previous request object to
##                # the list_next method.
##                scanop = service.events().list_next(scanop, response)
##
##        # MRI Slots
##        # Loop until all pages have been processed.
##        print("--------------Start MRI Slots Requests...")
##        while mrislots != None:
##            # Get the next page.
##            response = mrislots.execute()
##            # Accessing the response like a dict object with an 'items' key
##            # returns a list of item objects (events).
##            for event in response.get('items', []):
##                # The event object is a dict object.
##                # Store event as EventClass
##                if Event.EventClass.validate(event):
##                    obj = Event.EventClass(event)
##                    mrislots_events[obj.get_start()] = obj
##    ##                mrislots_events.append(Event.EventClass(event))
##                    print(datetime.fromtimestamp(obj.get_start()))
##
##                    if write_cache:
##                        outfile = open(HISTORY + "mrislots/" + str(obj.get_start()) + '.json','w')
##    ##                    outfile = open(HISTORY + "mrislots/" + str(mrislots_events[-1].start_s) + '.json','w')
##                        json.dump(event,outfile)
##                        outfile.close()
##
##                # Get the next request object by passing the previous request object to
##                # the list_next method.
##                mrislots = service.events().list_next(mrislots, response)
##
##        input("Press Enter to continue...")
##    except client.AccessTokenRefreshError:
##        print ("The credentials have been revoked or expired, please re-run"
##          "the application to re-authorize")
##    finally:
##        print("--------------End Calendar HTTP Requests.")

if __name__ == '__main__':
  main(sys.argv)
