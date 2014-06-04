#-------------------------------------------------------------------------------
# Name:        DataReport
# Purpose:
#
# Author:      krh5058
#
# Created:     30/05/2014
# Copyright:   (c) krh5058 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import CalendarReports

##import argparse
import os
import sys
from datetime import timedelta, datetime
from utils.event import EventClass
from utils.resources import Configure, DataStore, History
from utils import analysis
import re
import pickle

# Developer parameters
debug = True

### Parser for command-line arguments.
##parser = argparse.ArgumentParser(
##    description=__doc__,
##    formatter_class=argparse.RawDescriptionHelpFormatter,
##    parents=[tools.argparser])

# File path
filename = os.path.dirname(__file__)

def get_data():
    # List 'app-cache'
    ##configure = Configure(debug,path=filename)
    cachepath = Configure._Configure__joinpath(filename, 'app-cache')
    listing = sorted(os.listdir(cachepath))

    # TODO, What to do with other cache
    if listing:
        latest = max(listing) ## Latest date
        if debug:
            print('Using latest cached data, {0}.'.format(latest))
        return pickle.load(open(Configure._Configure__joinpath(cachepath, latest + os.sep + 'data.p'),'rb'))
    else: ## If no cache, recursion
        if debug:
            print('No cache, running CalendarReports.')
        CalendarReports.main(None)
        main()

def main():

    current = get_data()

    cache_order = [store.reports['NAME'] for store in current]

    mrislots = current[cache_order.index('mrislots')] ##.dat[1401220800.0] # MRI Slots
    scanop = current[cache_order.index('scanop')] ##.dat[1401206400.0] # Scanner op

    analysis.compare_against(mrislots,scanop)

    print('done')
##    configure.load_cache()

if __name__ == '__main__':
    main()
