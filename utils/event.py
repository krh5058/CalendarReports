#-------------------------------------------------------------------------------
# Name:        event
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
    d_cmp = ('d','day','days')
##    mnth_cmp = ('mo','month','months')
##    y_cmp = ('y','yr','yrs','year','years')
    dt_cmp = ('dt','date','datetime')
    tt_cmp = ('tt','tuple','timetuple')
    wn_cmp = ('w','wk','wn','week')

    fmt_head = ('year','month','date','week','weekday','start','end','duration','summary')

##    # Class attributes, redefined at instatiation
##    event = None

    def __init__(self,event):
        self.__event = event
        self.fmt()

    def validate(event):
        """
            Check for valid event fields from Google Calendar response
        """
        isValid = True
        k = list(event.keys())
        if 'start' not in k:
            isValid = False
##            print('start not found')
        else:
            if 'dateTime' not in list(event.get('start').keys()):
                isValid = False
##                print('dateTime in start not found')
        if 'end' not in k:
            isValid = False
##            print('end not found')
        else:
            if 'dateTime' not in list(event.get('end').keys()):
                isValid = False
##                print('dateTime in end not found')

        return isValid

    def datestring_to_timestamp(date_string):
        """
        Converts RFC3399 date string standards into a numeric value (seconds)
        Input is date string.
        """

        datestrings = EventClass.dateTime_pattern.match(date_string)
        date_num = datetime(int(datestrings.group('year')),int(datestrings.group('month')),int(datestrings.group('day')),int(datestrings.group('hour')),int(datestrings.group('minute')))

        return date_num.timestamp()

    def timestamp_to_datestring(time_s):
        """
        Output a RFC3399 string
        """

        time_str = datetime.fromtimestamp(time_s).strftime(EventClass.strfmt)
        return time_str

    def timestamp_to_datetime(time_s):
        """
        Output a datetime() data-type
        """

        time_str = EventClass.timestamp_to_datestring(time_s)
        datestrings = EventClass.dateTime_pattern.match(time_str)
        date_num = [int(x) for x in datestrings.groups()]
        return datetime(date_num[0],date_num[1],date_num[2],date_num[3],date_num[4],date_num[5])

    def timestamp_to_timetuple(time_s):
        """
        Output a datetime().timetuple() data-type
        """

        return EventClass.timestamp_to_datetime(time_s).timetuple()

    def timestamp_to_weeknumber(time_s):
        """
        Output a datetime().isocalendar()[1] data-type (ISO week numbeR)
        """

        return EventClass.timestamp_to_datetime(time_s).isocalendar()[1]

    def timestamp_conversion(time_s,formatting):
        """
        Output a timestamp value according to a formatting argument
        Output can be seconds, minutes, hours, days
        """

        if formatting.lower() in EventClass.s_cmp:
            format_out = time_s
        elif formatting.lower() in EventClass.m_cmp:
            format_out = time_s/60
        elif formatting.lower() in EventClass.h_cmp:
            format_out = time_s/60/60
        elif formatting.lower() in EventClass.d_cmp:
            format_out = time_s/60/60/24
        else:
            raise FormattingError(
                'EventClass (timestamp_conversion): Unrecognized conversion argument, "' + formatting + '".')

        return format_out

    def timestamp_format(time_s,formatting):
        """
        Output a timestamp value according to a formatting argument
        Output can be datetime or timetuple
        """

        if formatting.lower() in EventClass.dt_cmp:
            format_out = EventClass.timestamp_to_datetime(time_s)
        elif formatting.lower() in EventClass.tt_cmp:
            format_out = EventClass.timestamp_to_timetuple(time_s)
        elif formatting.lower() in EventClass.wn_cmp:
            format_out = EventClass.timestamp_to_weeknumber(time_s)
        else:
            raise FormattingError(
                'EventClass (timestamp_format): Unrecognized formatting argument, "' + formatting + '".')

        return format_out

    def today():
        """
        Return datetime type for today
        """
        return datetime.today()

    def fmt(self):
        """ Format class data according to class attribute, fmt_head"""
        # Year, month, date, week number, weekday are based on start time.  Assuming no overnight events
        l = []
        for head in self.fmt_head:
            # TODO Need to make abstracts and error handling
            if head=='year':
                l.append(self.get_start('tt')[0])
            elif head=='month':
                l.append(self.get_start('tt')[1])
            elif head=='date':
                l.append(self.get_start('tt')[2])
            elif head=='week':
                l.append(self.get_start('wn'))
            elif head=='weekday':
                l.append(self.get_start('tt')[6])
            elif head=='start':
                l.append(self.get_start())
            elif head=='end':
                l.append(self.get_end())
            elif head=='duration':
                l.append(self.duration('h'))
            elif head=='count': ## DayClass
                l.append(self.count())
            elif head=='summary': ## EventClass
                l.append(self.__event.get('summary',''))
                # TODO, reference parsing, add to DayClass
            elif head=='span': ## DayClass
                l.append(self.span())
            else:
                raise Exception('EventClass (fmt) -- Unrecognized header type. {0}.'.format(head))

            self.formatted_data_tuple = tuple(l)

    def get_start(self,formatting='s'):
        """ Timestamp format/conversion from event start date string"""

        time_s = EventClass.datestring_to_timestamp(self.__event.get('start').get('dateTime'))

        if formatting.lower() in EventClass.s_cmp:
            format_out = time_s
        elif formatting.lower() in EventClass.dt_cmp + EventClass.tt_cmp + EventClass.wn_cmp:
            format_out = EventClass.timestamp_format(time_s,formatting)
        else:
            raise FormattingError(
                'EventClass (get_start): Unavailable formatting argument, "' + formatting + '".')

        return format_out

    def get_end(self,formatting='s'):
        """ Timestamp format/conversion from event end date string"""

        time_s = EventClass.datestring_to_timestamp(self.__event.get('end').get('dateTime'))

        if formatting.lower() in EventClass.s_cmp:
            format_out = time_s
        elif formatting.lower() in EventClass.dt_cmp + EventClass.tt_cmp + EventClass.wn_cmp:
            format_out = EventClass.timestamp_format(time_s,formatting)
        else:
            raise FormattingError(
                'EventClass (get_end): Unavailable formatting argument, "' + formatting + '".')

        return format_out

    def duration(self,formatting='s'):
        """ Duration calculation of event"""

        if isinstance(self,EventClass):
            dur = (self.get_end() - self.get_start())

            ## Conversion Only
            if formatting.lower() in EventClass.s_cmp + EventClass.m_cmp + EventClass.h_cmp + EventClass.d_cmp:
                format_out = EventClass.timestamp_conversion(dur,formatting)
            else:
                raise FormattingError(
                    'EventClass (duration): Unavailable formatting argument, "' + formatting + '".')

            return format_out
        else:
            raise Exception('EventClass (duration) -- method overwrite required!')

class DayClass(EventClass):

    fmt_head = ('year','month','date','week','weekday','start','end','duration','count','span')

    def __init__(self,*events):
        self.__event = []
        for eventObj in events:
            # Valide event
            # Assumed constructor only aggregates upwards (EventClass > Dayclass)
            # Using name mangled, _EventClass__event
            # Assuming type check occured before passing arguments to constructor
            if EventClass.validate(eventObj._EventClass__event):
                self.__event.append(eventObj)
        self.fmt()

    def unpack_events(self):
        """
        """
        out = {}
        for eventObj in self.__event:
            out[eventObj.get_start()] = eventObj ## Reconstruct dictionary

        return out

    def get_start(self,formatting='s'):
        """ Timestamp format/conversion from earliest event"""

        time_s = min([_event.get_start() for _event in self.__event])
##        time_s = EventClass.datestring_to_timestamp(self.event.get('start').get('dateTime'))

        if formatting.lower() in EventClass.s_cmp:
            format_out = time_s
        elif formatting.lower() in EventClass.dt_cmp + EventClass.tt_cmp + EventClass.wn_cmp:
            format_out = EventClass.timestamp_format(time_s,formatting)
        else:
            raise FormattingError(
                'EventClass (get_start): Unavailable formatting argument, "' + formatting + '".')

        return format_out

    def get_end(self,formatting='s'):
        """ Timestamp format/conversion from event end date string"""

        time_s = max([_event.get_end() for _event in self.__event])
##        time_s = EventClass.datestring_to_timestamp(self.event.get('end').get('dateTime'))

        if formatting.lower() in EventClass.s_cmp:
            format_out = time_s
        elif formatting.lower() in EventClass.dt_cmp + EventClass.tt_cmp + EventClass.wn_cmp:
            format_out = EventClass.timestamp_format(time_s,formatting)
        else:
            raise FormattingError(
                'EventClass (get_end): Unavailable formatting argument, "' + formatting + '".')

        return format_out

    def duration(self,formatting='s'):
        """ Duration calculation of day
        Cumulative duration of all events.
        Overlapping events are merged.
        """

        end = 0
        dur = 0
        for i in range(0,len(self.__event)):
            if self.__event[i].get_start() < end: # If at least partially overlapping
                if not self.__event[i].get_end() < end: # Only if not entirely overlapping
                    dur = dur + (self.__event[i].get_end() - end)
                    end = self.__event[i].get_end()
            else: # If no overlaps
                dur = dur + (self.__event[i].get_end() - self.__event[i].get_start())
                end = self.__event[i].get_end()

        ## Conversion Only
        if formatting.lower() in EventClass.s_cmp + EventClass.m_cmp + EventClass.h_cmp + EventClass.d_cmp:
            format_out = EventClass.timestamp_conversion(dur,formatting)
        else:
            raise FormattingError(
                'EventClass (duration): Unavailable formatting argument, "' + formatting + '".')

        return format_out

    def span(self,formatting='s'):
        """ Span of start and end timestamps across day (indempotent)
        Assumes events are listed in order [see utils.resources.DataStore.to_days()]
        Consolidates overlapping events into spans, creates starting and ending timestamps of event spans
        Returns tuple containing (start,end) tuple pairs of timestamp spans
        """
        timestamps = []
        end = 0
        for _event in self.__event:
            if _event.get_start() <= end: # If at least partially overlapping (or start equals prior end)
                if not _event.get_end() <= end: # Only if not entirely overlapping (or end equals prior end)
                    temp = timestamps.pop() # Remove last entry
                    timestamps.append((temp[0],_event.get_end())) # Use last entry, with modified end timestamp
                    end = _event.get_end() # Set new timestamp
            else: # If no overlaps
                timestamps.append((_event.get_start(),_event.get_end()))
                end = _event.get_end()

        format_out = []
        for s,e in timestamps:
            ## Conversion Only
            if formatting.lower() in EventClass.s_cmp + EventClass.m_cmp + EventClass.h_cmp + EventClass.d_cmp:
                _start = EventClass.timestamp_conversion(s,formatting)
                _end = EventClass.timestamp_conversion(e,formatting)
                format_out.append((_start,_end))
            else:
                raise FormattingError(
                    'EventClass (duration): Unavailable formatting argument, "' + formatting + '".')

        return tuple(format_out)

    def count(self):
        """ Number of events in the day
        """

        return len(self.__event)