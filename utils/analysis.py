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

    print('debug')

    # TODO: flags

    span = DayClass.fmt_head.index('span')

    for k in sorted(list(data2.dat.keys())): # Cycle by data2 (e.g. 'scanop')
        if k in list(data1.dat.keys()): # If timestamp of day is also present in data1 (e.g. 'mrislots')

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








