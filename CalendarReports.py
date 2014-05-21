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
from utils.event import EventClass
from utils.resources import Configure, History
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

    # Create configuration
    configure = Configure(debug,path=filename)

    # Read event history
    history = configure._get_path('HISTORY')
    old = []
    for source in configure.config['REQUEST']['PARAMETERS']['CALENDARS']:
        old.append(History(debug,path=history,source=source['name']))

    configure.config['REQUEST']['PARAMETERS']['CALENDARS'][0]['timeMin'] = old[0].reports['REQUESTFROM']
    configure.config['REQUEST']['PARAMETERS']['CALENDARS'][1]['timeMin'] = old[1].reports['REQUESTFROM']
    configure.save_request_config()

    print('done')

##    finally:
##        print("--------------End Calendar HTTP Requests.")

if __name__ == '__main__':
  main(sys.argv)
