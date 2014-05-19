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

__author__ = 'ken.r.hwang@gmail.com (Ken Hwang)'

import httplib2
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from inspect import getmembers,ismethod
import os
import re
import json
from utils import Event

class Configure:
    """
    Base data storage class
    Class variables: config, dat, reports
        'config': Dictionary containing generic object parameters
            'PATH': Basepath reference, default str ""
            'SOURCE': Target subdirectory, default str ""
        'reports': Placeholder for reports data, default {}
    """
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
                }
            }

    directories = {'CONFIG':None,
                    'DEV':None,
                    'HISTORY':None,
                    'LOG':None,
                    'UTILS':None}
    configpaths = {'CLIENT_SECRETS':None,
                    'CALENDARS':None,
                    'SLEIC_REF':None,
                    'AUTH':None}

    credentials = []
    service = []

    reports = {}

    def __init__(self,debug=False,**kwarg):
        if kwarg is not None:
            for k,v in kwarg.items():
                arg = k.upper()
                if arg in self.config:
                    param_type = self.config[arg].__class__.__name__
                    arg_type = v.__class__.__name__
                    if param_type==arg_type:
                        self.config[arg] = v
                    else:
                        print('(__init__) -- Expected variable of type "{0}" for argument "{1}" received type "{2}" instead.'.format(param_type,k,arg_type))
                else:
                    print('(__init__) -- Unrecognized argument "{0}" of value "{1}"'.format(k,v))

        self.reports['DEFINE_PATHS'] = self.define_paths()
        self.reports['LOAD_JSON_TO_CONFIG'] = self.load_json_to_config()
        self.reports['GEN_CREDENTIALS'] = self.gen_credentials()
        self.reports['CREATE_SERVICE_REQUEST'] = self.create_service_request()

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
        """
        Join PATH and FILE
        """
        return os.path.join(path + os.sep + file.lower())

    def _get_path(self,key):
        if key.upper() in self.directories:
            path = self.directories[key.upper()]
        elif key.upper() in self.configpaths:
            path = self.directories[key.upper()]
        else:
            print('(_get_path) -- Unrecognized path identifier "{0}"'.format(key))
            return

        if path is None:
            print('(_get_path) -- Path identifier "{0}" returned "None".  Define paths with "define_paths" first.'.format(key))
        else:
            return path

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

##    def __runroutine(self):
####        for i in range(0,len(self._routine)):
####            self._routine[i](self)
####        self._routine = {}
##        methods = getmembers(self, predicate=ismethod)
##        self.reports = {}
##        for method in methods:
##            if method[0] is not '__init__' and 'DataClass' not in method[0]: # Ignore init, and ignore DataClass base methods
##                self.reports[method[0]] = method[1]()

    def define_paths(self):
        """
        Define directory paths from basepath, config['PATH']
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
                print('(define_paths) -- Unrecognized directory:',k.lower(),'in',self.config['PATH'])
                result = False

        # Check if all paths exist
        if None in self.directories.values():
            print('(define_paths) -- Incomplete directory listing...')
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
                print('(define_paths) -- Unrecognized file:',os.path.join(configpath,file))
                result = False

        # Check if all JSON paths exist
        if None in self.configpaths.values():
            print('(define_paths) -- Incomplete config file listing...')
            for k, v in self.configpaths.items():
                print(k,':',v)
            result = False

        return result

    def load_json_to_config(self):
        """
        Open and load all config data (JSON)
        Read and save data
        Close all config files
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

    def gen_credentials(self):
        """
        Generate credentials with Google OAuth2.0 server, or use authentication tokens
        """
        result = True

        print("(gen_credentials) -- Path:",self.configpaths['CLIENT_SECRETS'])
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
            self.credentials = storage.get()
            if self.credentials is None or self.credentials.invalid:
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
                self.credentials = tools.run_flow(FLOW, storage, flags)
        except:
            result = False

        return result

    def create_service_request(self):
        """
        Create an HTTP request type for the API type and version
        """
        result = True

        try:
            # Create an httplib2.Http object to handle our HTTP requests and authorize it
            # with our good Credentials.
            http = httplib2.Http()
            http = self.credentials.authorize(http)

            # Construct the service object for the interacting with the Calendar API.
            self.service = discovery.build(self.config['API']['type'], self.config['API']['version'], http=http)
        except:
            result = False

        return result

    def modify_service_request(self):
##        # timeMin
##        if use_cache:
##            cacheMax = datetime(2014,4,26,16,0,1)
##            timeMinStr = cacheMax.strftime(Event.EventClass.strfmt)
##        else:
##            # Untested
##            timeMinStr = None
##
##        # timeMax, specify weeks in the future
##        weeksFuture = 2
##        timeMaxStr = (datetime.today() + timedelta(weeks=weeksFuture)).strftime(Event.EventClass.strfmt)
##
##        scanop_data = calendar_data["calendars"]["scanop"]
##        scanop = service.events().list(
##            calendarId=scanop_data["calendarId"],
##            singleEvents=(scanop_data["singleEvents"]=="True"),
##            orderBy=scanop_data["orderBy"],
##            timeZone = scanop_data["timeZone"],
##            timeMin = timeMinStr,
##            timeMax = timeMaxStr
##            )
##        scanop_events = {}
##
##        mrislots_data = calendar_data["calendars"]["mrislots"]
##        mrislots = service.events().list(
##            calendarId=mrislots_data["calendarId"],
##            singleEvents=(mrislots_data["singleEvents"]=="True"),
##            orderBy=mrislots_data["orderBy"],
##            timeZone = mrislots_data["timeZone"],
##            timeMin = timeMinStr,
##            timeMax = timeMaxStr
##            )
##        mrislots_events = {}
##
##        return result

##    def modify_request_config(self):
##        """
##        Modify configuration parameters for handling request data
##        """
##        return 0
##
##    def query_data(self):
##        # HTTP Requests
##        try:
##            print("--------------Start Calendar HTTP Requests...")
##
##            # Scanner Operator Availability
##            # Loop until all pages have been processed.
##            print("--------------Start Scanner Operator Requests...")
##            while scanop != None:
##                # Get the next page.
##                response = scanop.execute()
##                # Accessing the response like a dict object with an 'items' key
##                # returns a list of item objects (events).
##                for event in response.get('items', []):
##                    # The event object is a dict object.
##                    # Store event as EventClass
##                    if Event.EventClass.validate(event):
##                        obj = Event.EventClass(event)
##                        scanop_events[obj.get_start()] = obj
##        ##                scanop_events.append(Event.EventClass(event))
##                        print(datetime.fromtimestamp(obj.get_start()))
##
##                        if write_cache:
##                            outfile = open(HISTORY + "scanop/" + str(obj.get_start()) + '.json','w')
##        ##                    outfile = open(HISTORY + "scanop/" + str(scanop_events[-1].start_s) + '.json','w')
##                            json.dump(event,outfile)
##                            outfile.close()
##
##                    # Get the next request object by passing the previous request object to
##                    # the list_next method.
##                    scanop = service.events().list_next(scanop, response)
##
##            # MRI Slots
##            # Loop until all pages have been processed.
##            print("--------------Start MRI Slots Requests...")
##            while mrislots != None:
##                # Get the next page.
##                response = mrislots.execute()
##                # Accessing the response like a dict object with an 'items' key
##                # returns a list of item objects (events).
##                for event in response.get('items', []):
##                    # The event object is a dict object.
##                    # Store event as EventClass
##                    if Event.EventClass.validate(event):
##                        obj = Event.EventClass(event)
##                        mrislots_events[obj.get_start()] = obj
##        ##                mrislots_events.append(Event.EventClass(event))
##                        print(datetime.fromtimestamp(obj.get_start()))
##
##                        if write_cache:
##                            outfile = open(HISTORY + "mrislots/" + str(obj.get_start()) + '.json','w')
##        ##                    outfile = open(HISTORY + "mrislots/" + str(mrislots_events[-1].start_s) + '.json','w')
##                            json.dump(event,outfile)
##                            outfile.close()
##
##                    # Get the next request object by passing the previous request object to
##                    # the list_next method.
##                    mrislots = service.events().list_next(mrislots, response)
##
##            input("Press Enter to continue...")
##        except client.AccessTokenRefreshError:
##            print ("The credentials have been revoked or expired, please re-run"
##              "the application to re-authorize")

class History():

    history = []
    path = None
    source = None
    read = True,
    write = False

    def __init__(self,path=None,source=None):
        self.path = path
        self.source = source

    def read(self):
        result = True

        # Read from source
        if self.read:
            fullpath = Configure._Configure__joinpath(self.path,self.source)
            print("History (read) -- Reading from {0}".format(fullpath))
            try:
                listing = os.listdir(fullpath)
                for filename in listing:
                    event_json = open(os.path.join(fullpath + os.sep + filename))
                    time_s = float(os.path.splitext(filename)[0]) ## Filename (timestamp) to float
                    json_data = json.load(event_json)
                    if Event.EventClass.validate(json_data):
                        self.history.append(Event.EventClass(json_data))
##                        print(Event.EventClass.timestamp_to_datetime(time_s))
                    event_json.close()
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
                result = False
            finally:
                print("History (read) -- read() finished.")
        else:
            print('History (read) -- READ set to "{0}".'.format(self.read))
            result = False

        return result

##    def write(self):

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