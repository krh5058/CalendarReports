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
    # Date string patterns (RFC3399)
    dateTime_pattern = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})')
    date_pattern = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})')
    strfmt = "%Y-%m-%dT%H:%M:%S-04:00" ## Eastern, observing daylight savings
    s_cmp = {'s','sec','secs','second','seconds'}
    m_cmp = {'m','min','mins','minute','minutes'}
    h_cmp = {'h','hr','hrs','hour','hours'}
    d_cmp = {'d','day','date','datetime'}
    i_cmp = {'i','iso'}
##    all_events = []

    # Class attributes, redefined at instatiation
    event = None
    groupable = True

    # Class attributes, redefined in method calls
    start_s = None
    end_s = None
    dur_s = None

    def __init__(self, event):
        self.event = event
        self.start()
        self.end()
        self.duration()
##        EventClass.all_events.append(self)

    def timestamp(self, date_dict):
        """
        Converts RFC3399 date string standards into a numeric value (seconds)
        Input is dictionary key/value pair.
        Check for either "dateTime", or "date" key (all-day)
        Mark ungroupable if all-day
        """

        if 'dateTime' in date_dict:
            date_string = date_dict.get('dateTime')
            datestrings = EventClass.dateTime_pattern.match(date_string)
            date_num = datetime(int(datestrings.group('year')),int(datestrings.group('month')),int(datestrings.group('day')),int(datestrings.group('hour')),int(datestrings.group('minute')))
        elif 'date' in date_dict: ## All day event
            date_string = date_dict.get('date')
            datestrings = EventClass.date_pattern.match(date_string)
            date_num = datetime(int(datestrings.group('year')),int(datestrings.group('month')),int(datestrings.group('day')))
            self.groupable = False ## Can't be grouped
        else:
            raise FormattingError(
                'EventClass (timestamp): Unrecognized key in event dictionary, "' + list(date_dict.keys())[0] + '".')

        return date_num.timestamp()

    def datetime_format(self, time_s):
        """
        Output a datetime() data-type
        """

        time_str = datetime.fromtimestamp(time_s).strftime(EventClass.strfmt)
        datestrings = EventClass.dateTime_pattern.match(time_str)
        date_num = [int(x) for x in datestrings.groups()]
        return datetime(date_num[0],date_num[1],date_num[2],date_num[3],date_num[4],date_num[5])

    def iso_format(self, time_s):
        """
        Output a datetime().isocalendar() data-type
        """

        return self.datetime_format(time_s).isocalendar()

    def timestamp_format(self,time_s,formatting):
        """
        Output a timestamp value according to a formatting argument
        Output can be seconds, minutes, or hours
        """

        if formatting.lower() in EventClass.s_cmp:
            format_out = time_s
        elif formatting.lower() in EventClass.m_cmp:
            format_out = time_s/60
        elif formatting.lower() in EventClass.h_cmp:
            format_out = time_s/60/60
        elif formatting.lower() in EventClass.d_cmp:
            format_out = self.datetime_format(time_s)
        elif formatting.lower() in EventClass.i_cmp:
            format_out = self.iso_format(time_s)
        else:
            raise FormattingError(
                'EventClass (timestamp_format): Unrecognized formatting argument, "' + formatting + '".')

        return format_out

    def start(self,formatting='s'):
        """ Timestamp conversion from event start date string"""

        if self.start_s is None:
            self.start_s = self.timestamp(self.event.get('start'))

        return self.timestamp_format(self.start_s,formatting)

    def end(self,formatting='s'):
        """ Timestamp conversion from event end date string"""

        if self.end_s is None:
            self.end_s = self.timestamp(self.event.get('end'))

        return self.timestamp_format(self.end_s,formatting)

    def duration(self,formatting='s'):
        """ Duration calculation of event"""

        if self.dur_s is None:
            self.dur_s = self.end_s - self.start_s

        if formatting.lower() in EventClass.s_cmp:
            format_out = self.timestamp_format(self.dur_s,formatting)
        elif formatting.lower() in EventClass.m_cmp:
            format_out = self.timestamp_format(self.dur_s,formatting)
        elif formatting.lower() in EventClass.h_cmp:
            format_out = self.timestamp_format(self.dur_s,formatting)
        else:
            raise FormattingError(
                'EventClass (duration): Unavailable formatting argument, "' + formatting + '".')

        return format_out

##class GroupedEventClass(EventClass):
##
##    def __init__(self):
##        for event in self.all_events:
##            print(event.start_s)
##            print(event.end_s)