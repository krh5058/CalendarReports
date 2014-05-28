#-------------------------------------------------------------------------------
# Name:        resources
# Purpose:
#
# Author:      krh5058
#
# Created:     15/05/2014
# Copyright:   (c) krh5058 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

"""Resources for Google API service

Configure, query, and store service data
"""

__author__ = 'ken.r.hwang@gmail.com (Ken Hwang)'

import httplib2
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from inspect import getmembers,ismethod
from datetime import timedelta
##import gc
import pickle
import os
import re
import json
from utils.event import EventClass, DayClass, WeekClass

class Configure:
    """Base configuration class

    Class variables: config, directories, configpaths, reports
        'config': Dictionary containing class parameters
            'PATH': Basepath reference, default str ""
            'API': 'type' and 'version' of API
            'REQUEST': 'PARAMETERS' and 'EVENT_PARSE',
                for calendar request parameters and event data parsing data
            'CREDENTIALS': Authorized credentials for HTTP request
            'SERVICE': Discovery service object
        'log': Logging parameters
            'TIME': Current date/time
        'directories': Path directories
        'configpaths': JSON config path directories
        'reports': Placeholder for reports data, default {}
    """

    # Class Attributes
    config = {
            'PATH':"",
            'API':{
                'type':'calendar',
                'version':'v3'
                },
            'REQUEST':{
                'PARAMETERS':{
                    'CALENDARS':None ## Google API HTTP request parameters
                    },
                'EVENT_PARSE':{
                    'SLEIC_REF':None ## Event reference for SLEIC's MRI Slots calendar
                    }
                },
            'CREDENTIALS':None,
            'SERVICE':None
            }

    log = {
        'TIME':None,
        'REQUEST_ORDER':[]
        }

    directories = {
                    'CACHE':None,
                    'CONFIG':None,
                    'DEV':None,
                    'HISTORY':None,
                    'LOG':None,
                    'UTILS':None}
    configpaths = {'CLIENT_SECRETS':None,
                    'CALENDARS':None,
                    'SLEIC_REF':None,
                    'AUTH':None}

    reports = {}

    def __init__(self,debug=False,**kwarg):
        """Initialize Configure class
        Arguments:
            'debug': True/False, to display debug text
            Any key in the Configure.config dict.  'path' is required.
        """
        if kwarg is not None:
            for k,v in kwarg.items():
                arg = k.upper()
                if arg in self.config:
                    param_type = self.config[arg].__class__.__name__
                    arg_type = v.__class__.__name__
                    if param_type==arg_type:
                        self.config[arg] = v
                    else:
                        print('Configure (__init__) -- Expected variable of type "{0}" for argument "{1}" received type "{2}" instead.'.format(param_type,k,arg_type))
                else:
                    print('Configure (__init__) -- Unrecognized argument "{0}" of value "{1}"'.format(k,v))

        self.start_log()

        self.reports['DEFINE_PATHS'] = self.define_paths()
        self.reports['LOAD_JSON_TO_CONFIG'] = self.load_json_to_config()
        self.reports['GEN_CREDENTIALS'] = self.gen_credentials()
        self.reports['CREATE_BASE_SERVICE'] = self.create_base_service()

        if debug:
            file = os.path.split(__file__)
            print('-- DEBUG SUMMARY --')
            print('Directory...',file[0])
            print('SOURCE CODE...',file[1])
            print('MODULE...',__name__)
            print('CLASS...',self.__class__.__name__)
            if self.reports:
                print('REPORTS...')
                for k,v in self.reports.items():
                    if k:
                        print('{0}: {1}'.format(k,v))
            print('-- END DEBUG SUMMARY --')

    def __joinpath(path,file):
        """Join PATH and FILE
        """
        return os.path.join(path + os.sep + file.lower())

    def _get_path(self,key):
        """Get a path directory from class attribute
        Argument: key associated with either 'directories' or
            'configpaths' dictionary
        """
        if key.upper() in self.directories:
            path = self.directories[key.upper()]
        elif key.upper() in self.configpaths:
            path = self.configpaths[key.upper()]
        else:
            print('Configure (_get_path) -- Unrecognized path identifier "{0}"'.format(key))
            return

        if path is None:
            print('Configure (_get_path) -- Path identifier "{0}" returned "None".  Define paths with "define_paths" first.'.format(key))
        else:
            return path

##    def __runroutine(self):
####        for i in range(0,len(self._routine)):
####            self._routine[i](self)
####        self._routine = {}
##        methods = getmembers(self, predicate=ismethod)
##        self.reports = {}
##        for method in methods:
##            if method[0] is not '__init__' and 'DataClass' not in method[0]: # Ignore init, and ignore DataClass base methods
##                self.reports[method[0]] = method[1]()

    def start_log(self):
        self.log['TIME'] = EventClass.today()

    def define_paths(self):
        """Define directory paths from basepath, config['PATH']
        Define JSON configure files from config path, directories['CONFIG']
        """

        result = True

        # Parse only pertinent directories
        dirs = [name for name in os.listdir(self.config['PATH']) if os.path.isdir(os.path.join(self.config['PATH'], name))] ## Directories only
        directorykeys = [directory.upper() for directory in dirs if re.match('[._]',directory) is None] ## Remove unnecessary directories

        # Validate directory against class dictionary: 'dictionaries'
        for k in directorykeys:
            if k in self.directories.keys():
                self.directories[k] = os.path.join(self.config['PATH'],k.lower())
            else:
                print('Configure (define_paths) -- Unrecognized directory:',k.lower(),'in',self.config['PATH'])
                result = False

        # Check if all paths exist
        if None in self.directories.values():
            print('Configure (define_paths) -- Incomplete directory listing...')
            for k, v in self.directories.items():
                print(k,':',v)
            result = False

        configpath = self.directories['CONFIG'] ## Config path
        jsonconfig = os.listdir(configpath)

        # Validate json files against class dictionary: 'configpaths'
        for file in jsonconfig:
            filekey = os.path.splitext(file)[0].upper()
            if filekey in self.configpaths.keys():
                self.configpaths[filekey] = os.path.join(configpath,file)
            else:
                print('Configure (define_paths) -- Unrecognized file:',os.path.join(configpath,file))
                result = False

        # Check if all JSON paths exist
        if None in self.configpaths.values():
            print('Configure (define_paths) -- Incomplete config file listing...')
            for k, v in self.configpaths.items():
                print(k,':',v)
            result = False

        return result

    def load_json_to_config(self):
        """Open and load all config data (JSON)
        Read and store data
        """
        result = True

        # For each config entry
        for k in self.config['REQUEST'].keys():
            # Use dictionary keys to obtain file paths from equivalent keys in 'configpaths'
            for key in self.config['REQUEST'][k]:
                try:
                    json_data = open(self.configpaths[key])
                    try:
                        self.config['REQUEST'][k][key] = json.load(json_data) ## Load JSON data
                    except:
                        result = False
                    json_data.close() ## Close files after loaded
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))
                    result = False

        return result

    def save_request_config(self):
        """Save changes to JSON config files
        """
        result = True

        # For each config entry
        for k in self.config['REQUEST'].keys():
            # Use dictionary keys to obtain file paths from equivalent keys in 'configpaths'
            for key in self.config['REQUEST'][k]:
                try:
                    with open(self.configpaths[key],'w') as json_out:
                        try:
                            json.dump(self.config['REQUEST'][k][key],json_out) ## Dump JSON data
                        except:
                            result = False
                    json_out.close() ## Close files after loaded
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))
                    result = False

        return result

    def save_to_cache(self,data):
        """Save DataStore and Configure classes to cache directory
        """
        cachepath = Configure._Configure__joinpath(self.directories['CACHE'],str(self.log['TIME'].timestamp()))
##        if not os.path.exists(cachepath):
        os.mkdir(cachepath)
        pickle.dump(data,open(Configure._Configure__joinpath(cachepath,'data.p'),'wb'))
        pickle.dump(Configure,open(Configure._Configure__joinpath(cachepath,'config.p'),'wb'))

    def load_cache(self):
        """Load cache data
        """
        cachepath = Configure._Configure__joinpath(self.directories['CACHE'],str(self.log['TIME'].timestamp()))
        if os.path.exists(cachepath):
            current = pickle.load(open(Configure._Configure__joinpath(cachepath,'data.p'),'rb'))
            configure = pickle.load(open(Configure._Configure__joinpath(cachepath,'config.p'),'rb'))
            return current, configure

    def gen_credentials(self):
        """Generate credentials with Google OAuth2.0 server,
            or use authentication tokens
        """
        result = True

##        print("(gen_credentials) -- Path:",self.configpaths['CLIENT_SECRETS'])
        CLIENT_SECRETS = self.configpaths['CLIENT_SECRETS']

        # CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
        # application, including client_id and client_secret. You can see the Client ID
        # and Client secret on the APIs page in the Cloud Console:
        # <https://cloud.google.com/console#/project/561458633478/apiui>
        if CLIENT_SECRETS is None:
            print('(gen_credentials) -- Failed to find client_secrets file.')
            result = False

        # If the credentials don't exist or are invalid run through the native client
        # flow. The Storage object will ensure that if successful the good
        # credentials will get written back to the file.
        try:
            storage = file.Storage(self.configpaths['AUTH']) ## Read, or write to config path if necessary
            self.config['CREDENTIALS'] = storage.get()
            if self.config['CREDENTIALS'] is None or self.config['CREDENTIALS'].invalid:
                print('(gen_credentials) -- Re-authenticating and re-writing credentials.')

                # Set up a Flow object to be used for authentication.
                # Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
                # NEED. For more information on using scopes please see
                # <https://developers.google.com/+/best-practices>.
                FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
                  scope=[
                      'https://www.googleapis.com/auth/calendar',
                      'https://www.googleapis.com/auth/calendar.readonly',
                    ],
                    message=tools.message_if_missing(CLIENT_SECRETS))
                self.config['CREDENTIALS'] = tools.run_flow(FLOW, storage, flags)
        except:
            result = False

        return result

    def create_base_service(self):
        """Create an HTTP request type for API type and version
        """
        result = True

        try:
            # Create an httplib2.Http object to handle our HTTP requests and authorize it
            # with our good Credentials.
            http = httplib2.Http()
            http = self.config['CREDENTIALS'].authorize(http)

            # Construct the service object for the interacting with the Calendar API.
            self.config['SERVICE'] = discovery.build(self.config['API']['type'], self.config['API']['version'], http=http)
        except:
            result = False

        return result

    def gen_service_requests(self,weeksAhead=2):
        """Generate parameters for all service requests
        Arguments: weeksAhead, value of weeks ahead from today events should be drawn
        Returns list of services
        """

        if self.config['API']['type']=='calendar':

            # timeMax, specify weeks in the future
            timeMaxStr = (self.log['TIME'] + timedelta(weeks=weeksAhead)).strftime(EventClass.strfmt)

            # Iterate through services
            services = []
            for __config in self.config['REQUEST']['PARAMETERS']['CALENDARS']:
                self.log['REQUEST_ORDER'].append(__config['name'])
                __service = self.config['SERVICE']
                services.append(__service.events().list(
                            calendarId=__config["calendarId"],
                            singleEvents=__config["singleEvents"],
                            orderBy=__config["orderBy"],
                            timeZone = __config["timeZone"],
                            timeMin = __config["timeMin"],
                            timeMax = timeMaxStr
                        )
                    )
            return services
        else:
            print('Unsupported API type: {0}'.format(self.config['API']['type']))

def set_timestamp_args(f):
    def wrapper(obj,**kwargs):
        args = {'start':obj.reports['FIRST'],'end':obj.reports['LAST']} ## Default
        if kwargs:
            for k,v in kwargs.items():
                if k in args.keys(): ## If valid keyword
                    if v.__class__.__name__ == args[k].__class__.__name__: ## If valid class type
                        args[k] = v
                    else:
                        raise Exception('set_timestamp_args - Unexpected argument type {0}!'.format(v.__class__.__name__))
        return f(obj,args['start'],args['end'])
    return wrapper

class DataStore():
    """Base data storage class

    Class variables: read, write

    Will generate events using a Google discovery service, 'source', and save
    to instance storage.  After instantiation, will automatically run
    gen_events() and gen_report().  If debug=True, a summary will be printed.
    """

    read = True
    write = False

    def __init__(self,debug,source,name):
        """
        Initialize DataStore class type.
        Arguments:
            'debug': True/False, to display debug text
            source: Source for get_events to pull event data from
                Service instance for GET requests, or Path for loading JSON
        """

        # Instance Variables

        self.source = source

        self.reports = {
                    'NAME':name,
                    'TYPE':None,
                    'COUNT':None,
                    'FIRST':None,
                    'LAST':None,
                    'RANGE':None,
                    'REQUESTFROM':None
                }
        self.dat = {}

        # Read events
        if self.read:
            self.get_events()
        else:
            print('DataStore (__init__) -- READ set to "{0}".'.format(self.read))

##        # Write Events
##        if self.write:
##            self.save_events()
##        else:
##            print('DataStore -- Write set to "{0}".'.format(self.write))

        self.gen_report()

        if debug:
            file = os.path.split(__file__)
            print('-- DEBUG SUMMARY --')
            print('Directory...',file[0])
            print('SOURCE CODE...',file[1])
            print('MODULE...',__name__)
            print('CLASS...',self.__class__.__name__)
            if self.reports:
                print('REPORTS...')
                for k,v in self.reports.items():
                    if k:
                        print('{0}: {1}'.format(k,v))
            print('-- END DEBUG SUMMARY --')

    def gen_report(self):
        """Generate reports based on event storage
        """
        l = list(self.dat.keys())
        self.reports['COUNT'] = len(l)
        self.reports['FIRST'] = min(l)
        self.reports['TYPE'] = type(self.dat[min(l)]) ## Use first as exemplar
        self.reports['LAST'] = max(l)
        self.reports['RANGE'] = max(l) - min(l)
        reqfrom_t = self.dat[max(l)].get_end() + 1
        self.reports['REQUESTFROM'] = EventClass.timestamp_to_datestring(reqfrom_t)

    def get_events(self):
        """Get events from discovery service
        Paginate through responses, and execute more responses when no more
        event items.  End requests, when no more event data received.
        Each event is validated as appropriate data for EventClass, then stored
        against their timestamp (float) in instance.
        """
        # HTTP Requests
        try:
            print("getEvents -- Starting calendar HTTP Requests...")
            # Scanner Operator Availability
            # Loop until all pages have been processed.
            while self.source != None:
                # Get the next page.
                response = self.source.execute()
                # Accessing the response like a dict object with an 'items' key
                # returns a list of item objects (events).
                for event in response.get('items', []):
                    # The event object is a dict object.
                    # Store event as EventClass
                    if EventClass.validate(event):
                        obj = EventClass(event)
                        self.dat[obj.get_start()] = obj

                    # Get the next request object by passing the previous request object to
                    # the list_next method.
                    self.source = Configure.config['SERVICE'].events().list_next(self.source, response)
        except client.AccessTokenRefreshError:
            print ("The credentials have been revoked or expired, please re-run"
              "the application to re-authorize")
        finally:
            print("getEvents -- Finished calendar HTTP Requests...")

    def add_to_dat_dict(self,d):
        """
        Update dictionary with more items
        Argument:
            'd': dictionary, assumed to include timestamp key values and
                EventClass object values.
        """
        if not isinstance(d,dict):
            raise Exception('DataStore (add_to_dat_dict) -- Argument is not dictionary instance!')

        self.dat.update(d)
        self.gen_report()

    @set_timestamp_args
    def find_events(self,start,end):
        """

        """
        event_keys = sorted([k for k in list(self.dat.keys()) if end >= k >= start])
        out = {}
        if event_keys:
            for t in event_keys:
                out[t] = self.dat[t]

        return out

    def to_days(self):
        """ Organize events into days
        Consolidates events by day, and creates a DayClass
        Replaces self.dat instance attribute, from EventClass to DayClass
        Keys are timestamps from get_start(), start of first event of the day
        """

        if self.reports['TYPE'] is EventClass:

            days = {}
            temp = []
            _current = (0,0,0)
            for k in sorted(list(self.dat.keys())):
                day = self.dat[k].formatted_data_tuple[0:3] ## EventClass
                if not _current == day:
    ##                print('Length of temp:',len(temp))
                    _current = day
    ##                print(_current[1],_current[2],_current[0])
                    if temp:
                        dayObj = DayClass(*temp)
                        days[dayObj.get_start()] = dayObj
                        del temp[:] ## Clear list
    ##                gc.collect() ## Clear unreferenced memory
                temp.append(self.dat.pop(k))

            # Last DayClass instance
            if temp:
                dayObj = DayClass(*temp)
                days[dayObj.get_start()] = dayObj
                del temp[:] ## Clear list

            self.add_to_dat_dict(days)

        elif self.reports['TYPE'] is WeekClass:

            print('Convert to days from week')
##            days = {}
##            temp = []
##            _current = (0,0,0)
##            for k in sorted(list(self.dat.keys())):
##                day = self.dat[k].formatted_data_tuple[0:3] ## EventClass
##                if not _current == day:
##    ##                print('Length of temp:',len(temp))
##                    _current = day
##    ##                print(_current[1],_current[2],_current[0])
##                    if temp:
##                        dayObj = DayClass(*temp)
##                        days[dayObj.get_start()] = dayObj
##                        del temp[:] ## Clear list
##    ##                gc.collect() ## Clear unreferenced memory
##                temp.append(self.dat.pop(k))
##
##            # Last DayClass instance
##            if temp:
##                dayObj = DayClass(*temp)
##                days[dayObj.get_start()] = dayObj
##                del temp[:] ## Clear list
##
##            self.add_to_dat_dict(days)
##            self.gen_report()

        else:
            raise Exception('DataStore (to_days) -- Incorrect usage.  Expected EventClass or WeekClass data type.')

    def to_events(self):
        """ Organize days into events
        Unpack days into events, and creating one or more EventClasses
        Replaces self.dat instance attribute, from DayClass to EventClass
        Keys are timestamps from get_start(), start of event
        """

        if self.reports['TYPE'] is not DayClass:
            raise Exception('DataStore (to_events) -- Incorrect usage.  Expected DayClass data type.')

        temp = {}
        for k in sorted(list(self.dat.keys())):
            dayObj = self.dat.pop(k)
            temp.update(dayObj.unpack_events())
        self.add_to_dat_dict(temp)

class History(DataStore):
    """History subclass of DataStore
    Overridden get_events()
    """

    def get_events(self):
        """
        Get events from saved local JSON data
        'source' is a path directory for 'history' files
        """
        result = True

        # Read from source
        print("History (read) -- Reading from {0}".format(self.source))
        try:
            listing = os.listdir(self.source)
            for filename in listing:
                event_json = open(os.path.join(self.source + os.sep + filename))
                time_s = float(os.path.splitext(filename)[0]) ## Filename (timestamp) to float
                json_data = json.load(event_json)
                if EventClass.validate(json_data):
                    self.dat[time_s] = EventClass(json_data)
##                        print(EventClass.timestamp_to_datetime(time_s))
                event_json.close()
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            result = False
        finally:
            print("History (read) -- read() finished.")
            self.gen_report()

        return result

##    # Search SLEIC json
##    def _get_event_ref(pi=None,project=None):
##        out = []
##        for pi_line in self.config['REQUEST']['EVENT_PARSE']['SLEIC_REF']:
##            if pi is not None:
##                print('looking for',pi)
##                if pi_line["pi"]==pi:
##                    print('found',pi_line["pi"])
##                    for project_line in pi_line["project"]:
##                        if project is not None:
##                            print('looking for',project)
##                            if project_line["id"]==project:
##                                print('found',project_line["id"])
##                                out = project_line["subject"]
##                        else:
##                            out.append(project_line["id"])
##            else:
##                out.append(pi_line["pi"])
##
##        return out

### Open SLEIC dictionary resource
##    try:
##        sleic_json = open(SLEIC)
##    except IOError as e:
##        print("I/O error({0}): {1}".format(e.errno, e.strerror))
##
##    # SLEIC PI, project, and subject parsing
##    try:
##        sleic_data = json.load(sleic_json)
##
####            head = ['pi', 'project-id', 'full-event','date', 'start', 'end', 'duration', 'hrs-use-category','subject-id']
####
####        fwrite = csv.writer(csvfile, delimiter=',')
####        write_csv(fwrite,head)
##
##        lastweek = (datetime.today() - timedelta(weeks=1)).timestamp()
##        tomorrow = (datetime.today() + timedelta(days=1)).timestamp()
##        for event in mrislots_events.keys():
##            if (event > lastweek) and (event < tomorrow):
####                print(mrislots_events[event].event)
##                summary = mrislots_events[event].event.get('summary')
##                print('Full Event:', summary)
##                pi = re.search('\w{3}\d{1,4}',summary)
##                if pi:
##                    print('PI:',pi.group(0))
##                    sub1 = re.sub(pi.group(0),'',summary,1) ## Remove PI
##                    sub2 = re.sub('^[_\s]*(?<=\w)','',sub1) ## Remove leading underscores
##                    sumsplit = re.split('[_\s]',sub2,1) ## Split one underscore or space
####                    proj = re.search('([^_\s]{3,4})(?=\W)?',sub1)
##                    if len(sumsplit)==1:
##                        if len(sumsplit[0])==4:
##                            proj = sumsplit[0]
##                            print('Suggested project ID:',proj)
##                        else:
##                            print('Unclear segment:',sumsplit[0])
##
##                    elif len(sumsplit) == 2:
##                        print('Segment 1:',sumsplit[0])
##                        print('Segment 2:',sumsplit[1])
####                        print('Project ID:',proj.group(0))
####                        sub2 = re.sub(proj.group(0),'',sub1,1)
####                        sub3 = re.sub('[_\s]','',sub2)
####                        if sub3:
####                            print('Subject:',sub3)
##                print(mrislots_events[event].event.get('start').get('dateTime'))
##                print(mrislots_events[event].event.get('end').get('dateTime'))
##                print(mrislots_events[event].duration('m'))
##    except IOError as e:
##        print("I/O error({0}): {1}".format(e.errno, e.strerror))
##    finally:
##        sleic_json.close()
##
##def main():
##    pass
##
##if __name__ == '__main__':
##    main()