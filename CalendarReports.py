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
##import argparse
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Additional imports
from datetime import timedelta, datetime
from utils.event import EventClass
from utils.resources import Configure, DataStore, History
import re
import json

# Developer parameters
debug = True

### Parser for command-line arguments.
##parser = argparse.ArgumentParser(
##    description=__doc__,
##    formatter_class=argparse.RawDescriptionHelpFormatter,
##    parents=[tools.argparser])

# File path
filename = os.path.dirname(__file__)

### Flags for cache read and write
##use_cache = True
##write_cache = False

# Create configuration
configure = Configure(debug,path=filename)

# Read event history and update config
# TODO, deprecate JSON file storage
def read_history():
    history = configure._get_path('HISTORY')
    old = []
    for name in configure.log['REQUEST_ORDER']:
        fullpath = Configure._Configure__joinpath(history,name)
        old.append(History(debug,fullpath,name))

    # Set/save new timeMin for available history
    # Get calendar order in config
    for calendar in configure.config['REQUEST']['PARAMETERS']['CALENDARS']:
        for r in old:
            if os.path.split(r.source)[1]==calendar['name']:
                print('Updating request parameter, {0}, from {1} to {2}'.format('timeMin',calendar['timeMin'],r.reports['REQUESTFROM']))
                calendar['timeMin'] = r.reports['REQUESTFROM']

    if configure.save_request_config():
        print('JSON request parameters saved.')
    else:
        print('Saving JSON request parameters failed.')

    return old

# Request events, in order, and update with history if they exist
def request_events(old=None):
    # Generate service requests, same as 'REQUEST_ORDER' order
    services = configure.gen_service_requests(weeksAhead=0)

    current = []
    for i in range(0,len(configure.log['REQUEST_ORDER'])):
        current.append(DataStore(debug,services[i],configure.log['REQUEST_ORDER'][i]))
        if old: ## If history exists
            current[i].add_to_dat_dict(old[i].dat)

    return current

# Main
def main(argv):

##    # Parse the command-line flags.
##    flags = parser.parse_args(argv[1:])

    # Read event history
    if History.read:
        old = read_history() # TODO, deprecate JSON

    # Read new events and consolidate with history
    if DataStore.read:
        # Request events
        if 'old' in locals():
            current = request_events(old)
        else:
            current = request_events()

        ##    t1 = datetime(2014, 5, 10, 10, 35, 5, 217250).timestamp()
        ##    t2 = datetime(2014, 5, 20, 10, 35, 5, 217250).timestamp()
        ##    current[0].find_events()

        current[0].to_days()
        current[1].to_days()

        ##    current[0].to_events()
        ##    current[1].to_events()

        # Store current data and configuration to cache
        # TODO, Cache management
        configure.save_to_cache(current)

    print('done')

if __name__ == '__main__':
  main(sys.argv)
