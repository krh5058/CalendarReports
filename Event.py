#-------------------------------------------------------------------------------
# Name:        Event
# Purpose:
#
# Author:      krh5058
#
# Created:     28/04/2014
# Copyright:   (c) krh5058 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from datetime import timedelta, datetime
import re

class FormattingError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)

class EventClass:
    """Event class for storing and formatting Google Calendar API event data"""

    # Class attributes
    # Date string pattern (RFC3399)
    datestring_pattern = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})')
    s_cmp = {'s','sec','secs','second','seconds'}
    m_cmp = {'m','min','mins','minute','minutes'}
    h_cmp = {'h','hr','hrs','hour','hours'}
    all_events = []

    # Class attributes, redefined at instatiation
    event = None

    # Class attributes, redefined in method calls
    start_s = None
    end_s = None

    def __init__(self, event):
        self.event = event
        self.start()
        self.end()
        EventClass.all_events.append(self)

    def timestamp(self, date_string):
        """Converts RFC3399 date string standards into a numeric value (seconds)"""

        datestrings = EventClass.datestring_pattern.match(date_string)
        date_num = datetime(int(datestrings.group('year')),int(datestrings.group('month')),int(datestrings.group('day')),int(datestrings.group('hour')),int(datestrings.group('minute')))
        return date_num.timestamp()

    def time_format(self,time_s,formatting):
        """Output a timestamp value according to a formatting argument (seconds, minutes, hours)"""

        if formatting.lower() in EventClass.s_cmp:
            format_out = time_s
        elif formatting.lower() in EventClass.m_cmp:
            format_out = time_s/60
        elif formatting.lower() in EventClass.h_cmp:
            format_out = time_s/60/60
        else:
            raise FormattingError(
                'EventClass (time_format): Unrecognized formatting argument, "' + formatting + '".')

        return format_out

    def start(self,formatting='s'):
        """ Timestamp conversion from event start date string"""

        if self.start_s is None:
            self.start_s = self.timestamp(self.event.get('start').get('dateTime'))

        return self.time_format(self.start_s,formatting)

    def end(self,formatting='s'):
        """ Timestamp conversion from event end date string"""

        if self.end_s is None:
            self.end_s = self.timestamp(self.event.get('end').get('dateTime'))

        return self.time_format(self.end_s,formatting)

##class DayClass(EventClass):
##    def __init__(self, *arg):
##
##        for event in arg:
