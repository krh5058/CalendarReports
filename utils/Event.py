#-------------------------------------------------------------------------------
# Name:        Event
# Purpose:
#
# Author:      Ken Hwang
#
# Created:     28/04/2014
# Copyright:   (c) krh5058 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

__author__ = 'ken.r.hwang@gmail.com (Ken Hwang)'

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
    s_cmp = ('s','sec','secs','second','seconds')
    m_cmp = ('m','min','mins','minute','minutes')
    h_cmp = ('h','hr','hrs','hour','hours')
    dt_cmp = ('d','day','date','datetime')
    tt_cmp = ('t','tt','tuple','timetuple')

    # Class attributes, redefined at instatiation
    event = None

    def __init__(self):
        self.event = event

    def validate(event):
        """
            Check for valid event fields from Google Calendar response
        """
        isValid = True
        k = list(event.keys())
        if 'start' not in k:
            isValid = False
            print('start not found')
        else:
            if 'dateTime' not in list(event.get('start').keys()):
                isValid = False
                print('dateTime in start not found')
        if 'end' not in k:
            isValid = False
            print('end not found')
        else:
            if 'dateTime' not in list(event.get('end').keys()):
                isValid = False
                print('dateTime in end not found')

        return isValid

    def datestring_to_timestamp(date_string):
        """
        Converts RFC3399 date string standards into a numeric value (seconds)
        Input is date string.
        """

        datestrings = EventClass.dateTime_pattern.match(date_string)
        date_num = datetime(int(datestrings.group('year')),int(datestrings.group('month')),int(datestrings.group('day')),int(datestrings.group('hour')),int(datestrings.group('minute')))

        return date_num.timestamp()

    def timestamp_to_datetime(time_s):
        """
        Output a datetime() data-type
        """

        time_str = datetime.fromtimestamp(time_s).strftime(EventClass.strfmt)
        datestrings = EventClass.dateTime_pattern.match(time_str)
        date_num = [int(x) for x in datestrings.groups()]
        return datetime(date_num[0],date_num[1],date_num[2],date_num[3],date_num[4],date_num[5])

    def timestamp_to_timetuple(time_s):
        """
        Output a datetime().isocalendar() data-type
        """

        return EventClass.timestamp_to_datetime(time_s).timetuple()

    def timestamp_conversion(time_s,formatting):

        if formatting.lower() in EventClass.s_cmp:
            format_out = time_s
        elif formatting.lower() in EventClass.m_cmp:
            format_out = time_s/60
        elif formatting.lower() in EventClass.h_cmp:
            format_out = time_s/60/60
        else:
            raise FormattingError(
                'EventClass (timestamp_conversion): Unrecognized conversion argument, "' + formatting + '".')

        return format_out

    def timestamp_format(time_s,formatting):
        """
        Output a timestamp value according to a formatting argument
        Output can be seconds, minutes, or hours
        """

        if formatting.lower() in EventClass.dt_cmp:
            format_out = EventClass.timestamp_to_datetime(time_s)
        elif formatting.lower() in EventClass.tt_cmp:
            format_out = EventClass.timestamp_to_timetuple(time_s)
        else:
            raise FormattingError(
                'EventClass (timestamp_format): Unrecognized formatting argument, "' + formatting + '".')

        return format_out

    def get_start(self,formatting='s'):
        """ Timestamp format/conversion from event start date string"""

        time_s = EventClass.datestring_to_timestamp(self.event.get('start').get('dateTime'))

        if formatting.lower() in EventClass.s_cmp + EventClass.m_cmp + EventClass.h_cmp:
            format_out = EventClass.timestamp_conversion(time_s,formatting)
        elif formatting.lower() in EventClass.dt_cmp + EventClass.tt_cmp:
            format_out = EventClass.timestamp_format(time_s,formatting)
        else:
            raise FormattingError(
                'EventClass (get_start): Unavailable formatting argument, "' + formatting + '".')

        return format_out

    def get_end(self,formatting='s'):
        """ Timestamp format/conversion from event end date string"""

        time_s = EventClass.datestring_to_timestamp(self.event.get('end').get('dateTime'))

        if formatting.lower() in EventClass.s_cmp + EventClass.m_cmp + EventClass.h_cmp:
            format_out = EventClass.timestamp_conversion(time_s,formatting)
        elif formatting.lower() in EventClass.dt_cmp + EventClass.tt_cmp:
            format_out = EventClass.timestamp_format(time_s,formatting)
        else:
            raise FormattingError(
                'EventClass (get_start): Unavailable formatting argument, "' + formatting + '".')

        return format_out

    def duration(self,formatting='s'):
        """ Duration calculation of event"""

        if isinstance(self,EventClass):
            dur_test = (self.get_end() - self.get_start())

            ## Conversion Only
            if formatting.lower() in EventClass.s_cmp + EventClass.m_cmp + EventClass.h_cmp:
                format_out = EventClass.timestamp_conversion(dur_test,formatting)
            else:
                raise FormattingError(
                    'EventClass (duration): Unavailable formatting argument, "' + formatting + '".')

            return format_out
        else:
            print("EventClass (duration): Placeholder")

##class GroupedEventClass(EventClass):
##
##    def __init__(self):
##        for event in self.all_events:
##            print(event.start_s)
##            print(event.end_s)