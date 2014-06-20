#-------------------------------------------------------------------------------
# Name:        analysis
# Purpose:
#
# Author:      krh5058
#
# Created:     30/05/2014
# Copyright:   (c) krh5058 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from utils.resources import DataStore
from utils.event import DayClass

__author__ = 'ken.r.hwang@gmail.com (Ken Hwang)'

COMPARE_PARAMETER_DEFAULT_VALUE = {
    'overlap': True
##    'percent': True,
##    'duration': True
}

def compare_against(data1,data2,**flags):
    """ Compare data1 against data2
    Flags specify comparison parameters
    """

    if data1.__class__.__name__ is not 'DataStore':
        raise Exception('analysis (compare_against) -- Incorrect usage.  Expected DataStore data type.')
    if data2.__class__.__name__ is not 'DataStore':
        raise Exception('analysis (compare_against) -- Incorrect usage.  Expected DataStore data type.')

    # TODO: flags

    span = DayClass.fmt_head.index('span')

    for k in sorted(list(data2.dat.keys())): # Cycle by data2 (e.g. 'scanop')
        if k in list(data1.dat.keys()): # If timestamp of day is also present in data1 (e.g. 'mrislots')

            print("Spans...")
            print('mrislots (a)-----')
            span1 = data1.dat[k].formatted_data_tuple[span]
            for _event in data1.dat[k].formatted_data_tuple[span]:
                print("Start:",DayClass.timestamp_to_datestring(_event[0]),", End:",DayClass.timestamp_to_datestring(_event[1]))

            print('scanop (b)-----')
            span2 = data2.dat[k].formatted_data_tuple[span]
            for _event in data2.dat[k].formatted_data_tuple[span]:
                print("Start:",DayClass.timestamp_to_datestring(_event[0]),", End:",DayClass.timestamp_to_datestring(_event[1]))

            excess1, excess2, overlap = span_compare(data1.dat[k].formatted_data_tuple[span],data2.dat[k].formatted_data_tuple[span])

            print()
            print("Calculations...")
            print('mrislots excess (a)----')
            for _excess in excess1:
                print("Start:",DayClass.timestamp_to_datestring(_excess[0]),", End:",DayClass.timestamp_to_datestring(_excess[1]))
                print("Duration:",(_excess[1] - _excess[0])/60/60)

            print('scanop excess (b)----')
            for _excess in excess2:
                print("Start:",DayClass.timestamp_to_datestring(_excess[0]),", End:",DayClass.timestamp_to_datestring(_excess[1]))
                print("Duration:",(_excess[1] - _excess[0])/60/60)

            print('overlap (c)----')
            for _overlap in overlap:
                print("Start:",DayClass.timestamp_to_datestring(_overlap[0]),", End:",DayClass.timestamp_to_datestring(_overlap[1]))
                print("Duration:",(_overlap[1] - _overlap[0])/60/60)

            print('debug')
##
##    for param,v in COMPARE_PARAMETER_DEFALT_VALUE:
##        if v:
##            if param=='overlap':
##                print('overlap')
##
##            overlap = 0

##                for evt2 in data2[span]:
##                    for evt1 in data1[span]:
##                        start = None
##                        if evt1[1] >= evt2[0]:
##                            start =
##
##                        if start
##                        if evt1[0] < evt2[0]:
##                            start = evt2[0]

##
##            elif param=='percent':
##                print('percent')
##
##            elif param=='duration':
##                print('duration')
##
##            else:
##                print('none')
def span_compare(span1,span2):
    """ Compare between two spans of day timestamps
    Returns duration, percentage, non-overlap for span1, and non-overlap for span2
    Overlap rules:
        1. Complete non-overlap, equates to out-of-range scheduling: Added to span1 entity
        2. Partial overlap, equates to parly out-of-range scheduling: span1 excess added to span1's entity, span 2 excess added to span2's entity
        3. Full overlap: same as #2
    Logic:
        1. Excess time is marked in start/end timestamps
    """
    duration = 0
    non_overlap1 = 0
    non_overlap2 = 0

    timestamps_a = []
    timestamps_b = []
    timestamps_c = []

    a = ()
    for _event1 in span1:
        a += _event1
    a = sorted(a)

    b = ()
    for _event2 in span2:
        b += _event2
    b = sorted(b)

    t = sorted(set(a+b))

    t0 = t1 = None
    id0 = id1 = None
    for i in range(0,len(t)-1):

        if t0 is None:
            t0 = t[i]
            t1 = t[i+1]
        else:
            t0 = t1
            if (i+1) > (len(t)-1):
                break
            else:
                t1 = t[i+1]

        print("t0:",t0,",",DayClass.timestamp_to_datestring(t0))
        print("t1:",t1,",",DayClass.timestamp_to_datestring(t1))

        # Skip gaps
        if t0 not in [tup[0] for tup in span1] + [tup[0] for tup in span2]: # t0 is not a starting timestamp
            if t0 in [tup[1] for tup in span1] + [tup[1] for tup in span2]: # t0 is the end of a spanned event
                continue # This means that there are no events that

        if (t0 in a) and (t0 in b):
            id0 = 'c'
        elif (t0 in a):
            id0 = 'a'
        elif (t0 in b):
            id0 = 'b'
        if (t1 in a) and (t1 in b):
            id1 = 'c'
        elif (t1 in a):
            id1 = 'a'
        elif (t1 in b):
            id1 = 'b'

        print("id0:",id0)
        print("id1:",id1)

        if id0 is id1:
            if id0 is 'a':
                timestamps_a.append((t0,t1))
            if id0 is 'b':
                timestamps_b.append((t0,t1))
            if id0 is 'c':
                timestamps_c.append((t0,t1))
        else:
            if id1 is 'b' and id0 is 'a':
                timestamps_a.append((t0,t1))
                a.append(t1)
            elif id1 is 'a' and id0 is 'b':
                timestamps_b.append((t0,t1))
                b.append(t1)
            elif id1 is 'a' and id0 is 'c':
##                timestamps_a.append((t0,t1))
##                timestamps_b.append((t0,t1))
                timestamps_c.append((t0,t1))
                a.remove(t1)
                b.append(t1)

                # Add a temporary start value, so loop does not think next is a gap
                tmp = list(span2)
                tmp.append((t1,0))
                span2 = tuple(tmp)
            elif id1 is 'b' and id0 is 'c':
##                timestamps_a.append((t0,t1))
##                timestamps_b.append((t0,t1))
                timestamps_c.append((t0,t1))
                b.remove(t1)
                a.append(t1)

                # Add a temporary start value, so loop does not think next is a gap
                tmp = list(span1)
                tmp.append((t1,0))
                span1 = tuple(tmp)

            elif id1 is 'c' and id0 is 'a':
                timestamps_a.append((t0,t1))
                a.remove(t1)
            elif id1 is 'c' and id0 is 'b':
                timestamps_b.append((t0,t1))
                b.remove(t1)

    print('debug')

    return tuple(timestamps_a), tuple(timestamps_b), tuple(timestamps_c)



##    for _event2 in span2:
##        for _event1 in span1:
##            if _event2[1] <= _event1[0]:
##                temp = DayClass.timestamp_conversion(_event1[1] - _event1[0],'h')
##                non_overlap1 += temp
##                print("No overlap.",temp,"hours added to event 1.")
##            else:
##                if _event2[1] <= _event1[1]:
##                    if _event1[0] <= _event2[0]:
##                        print("Full overlap (event2's duration)")
##                    else:
##                        print("Partial overlap (event2 end - event1 start)")
##                else:
##                    if _event1[1] <= _event2[0]:
##                        print("No overlap")
##                    elif _event1[0] <= _event2[0]:
##                        print("Partial overlap (event1 end - event2 start)")
##                    else:
##                        print("Full overlap (event1's duration)")

##            if _event1[0] < _event2[1]: # Check start of _event1 is earlier than end of _event2
##                if not _event1[0] < _event2[0]: # Check for any overlap: start of _event1 is later than (or equal to) start of _event2
##                    if _event1[1] <= _event2[1]: # Check for a full overlap: end of _event1 is earlier than (or equal to) end of _event2
##                        duration = duration + (_event1[1] - _event1[0]) # Add entire _event1 to duration
##                    else: # Partial overlap: end of _event1 is later than end of _event2
##                        duration = duration + (_event2[1] - _event1[0]) # Add [end of event2 less start of event1] to duration (partial)
##                else:
##                    if not _event1[1] < _event2[1]: # Check for another partial overlap: end of _event1 is later than start of _event2
##                        duration = duration + (_event1[1] - _event1[0]) # Add [end of event1 less start of event2] to duration (partial)
##                    else: # Check for a full overlap: end of _event1 is later than end of _event2
##                        duration = duration + (_event2[1] - _event2[0]) # Add entire _event2 to duration
##
##            else: # If no overlaps
##                timestamps.append((_event.get_start(),_event.get_end()))
##                end = _event.get_end()
##
##            for t2 in span2:
##                for t1 in span1:
##        ##            if t2[0]
##                    print('test')

