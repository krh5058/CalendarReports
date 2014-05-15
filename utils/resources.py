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
import os
import re
import json

class Directory:
    """Directory class for constructing necessary directory paths"""

    # Class variables
    basepath = None
    directories = {'CONFIG':None,
                    'DEV':None,
                    'HISTORY':None,
                    'LOG':None,
                    'UTILS':None}
    configpaths = {'CLIENT_SECRETS':None,
                    'CALENDARS':None,
                    'SLEIC_REF':None,
                    'AUTH':None}

    def __init__(self,basepath,debug=False):
        """
        Initialize Directory class
        Construct directory folder structure
        Arguments:
            basepath, path location of calling file
        """
        self.basepath = basepath
        result = self.define_paths()

        if debug:
            print('-- DEBUG SUMMARY --')
            print('SOURCE CODE...','resources.py')
            print('CLASS...','Directory')
            print('FUNCTION...',' __init__')
            print('BASEPATH...',basepath)
            print('CONFIG PATH...','Not specified')
            print('DEFINE_PATHS RETURNED...', result)
            print('-- END DEBUG SUMMARY --')

    def define_paths(self,*configpath):
        """
        Define directory paths from basepath
        Define JSON configure files from specified 'configpath' or default '/config' path
        """

        result = True

        # Parse only pertinent directories
        dirs = [name for name in os.listdir(self.basepath) if os.path.isdir(os.path.join(self.basepath, name))] ## Directories only
        directorykeys = [directory.upper() for directory in dirs if re.match('[._]',directory) is None] ## Remove unnecessary directories

        # Validate directory against class dictionary: 'dictionaries'
        for k in directorykeys:
            if k in self.directories.keys():
                self.directories[k] = os.path.join(self.basepath,k.lower())
            else:
                print('Directory (define_paths) -- Unrecognized directory:',k.lower(),'in',self.basepath)
                result = False

        # Check if all paths exist
        if None in self.directories.values():
            print('Directory (define_paths) -- Incomplete directory listing...')
            for k, v in self.directories.items():
                print(k,':',v)
            result = False

        # If no provided JSON path argument, use '/config' default
        if not configpath:
            configpath = self.directories['CONFIG'] ## Config path

        jsonconfig = os.listdir(configpath)

        # Validate json files against class dictionary: 'configpaths'
        for file in jsonconfig:
            filekey = os.path.splitext(file)[0].upper()
            if filekey in self.configpaths.keys():
                self.configpaths[filekey] = os.path.join(configpath,file)
            else:
                print('Directory (define_paths) -- Unrecognized file:',os.path.join(configpath,file))
                result = False

        # Check if all JSON paths exist
        if None in self.configpaths.values():
            print('Directory (define_paths) -- Incomplete config file listing...')
            for k, v in self.configpaths.items():
                print(k,':',v)
            result = False

        return result

class Configuration:
    """
    Configuration class for defining configuration parameters used in HTTP service requests
    """

    # Class variables
    API = {'type':'calendar','version':'v3'}
    dir_class = []
    credentials = []
    service = []
    json_files = []
    config_data = {'CALENDARS':None}

    def __init__(self,dir_class,debug=False):
        """
        Initialize Configuration class
        Run through configuration routine
        Arguments:
            dir_class, 'Directory' class instance
        """
        self.dir_class = dir_class
        auth_result = self.authenticate()
        request_result = self.create_http_request()
        load_result = self.load_config_data()

        if debug:
            print('-- DEBUG SUMMARY --')
            print('SOURCE CODE...','resources.py')
            print('CLASS...','Configuration')
            print('FUNCTION...',' __init__')
            print('DIR_CLASS...',dir_class)
            print('AUTHENTICATE RETURNED...', auth_result)
            print('CREATE_HTTP_REQUEST RETURNED...', request_result)
            print('LOAD_CONFIG_DATA RETURNED...', load_result)
            print('-- END DEBUG SUMMARY --')

    def authenticate(self):
        """
        Authenticate with Google OAuth2.0 server, or use authentication tokens
        """
        result = True

        # CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
        # application, including client_id and client_secret. You can see the Client ID
        # and Client secret on the APIs page in the Cloud Console:
        # <https://cloud.google.com/console#/project/561458633478/apiui>
        CLIENT_SECRETS = self.dir_class.configpaths['CLIENT_SECRETS']
        if CLIENT_SECRETS is None:
            print('Configuration (authenticate) -- Failed to find client_secrets file.')
            result = False

        # If the credentials don't exist or are invalid run through the native client
        # flow. The Storage object will ensure that if successful the good
        # credentials will get written back to the file.
        try:
            storage = file.Storage(os.path.join(self.dir_class.directories['CONFIG'],'auth.dat')) ## Read, or write to config path if necessary
            self.credentials = storage.get()
            if self.credentials is None or self.credentials.invalid:
                print('Configuration (authenticate) -- Re-authenticating and re-writing credentials.')

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

    def create_http_request(self):
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
            self.service = discovery.build(self.API['type'], self.API['version'], http=http)
        except:
            result = False

        return result

    def load_config_data(self):
        """
        Open and load all config data (JSON)
        Read and save data
        Close all config files
        """
        result = True

        # Use 'config_data' keys to obtain file paths from 'dir_class'
        for k in self.config_data.keys():
            try:
                json_data = open(self.dir_class.configpaths[k])
                try:
                    self.config_data[k] = json.load(json_data) ## Load JSON data
                except:
                    result = False
                json_data.close() ## Close files after loaded
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
                result = False

        return result

##    def create_service_request(self):
##
##    # Open calendars.json
##    try:
##        calendar_json = open(CALENDARS)
##    except IOError as e:
##        print("I/O error({0}): {1}".format(e.errno, e.strerror))
##
##    # Initialize service, data lists
##    try:
##        calendar_data = json.load(calendar_json)
##
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
##    finally:
##        calendar_json.close()

### Search SLEIC json
##def search_sleic(json_data,pi=None,project=None):
##    out = []
##    for pi_line in json_data:
##        if pi is not None:
##            print('looking for',pi)
##            if pi_line["pi"]==pi:
##                print('found',pi_line["pi"])
##                for project_line in pi_line["project"]:
##                    if project is not None:
##                        print('looking for',project)
##                        if project_line["id"]==project:
##                            print('found',project_line["id"])
##                            out = project_line["subject"]
##                    else:
##                        out.append(project_line["id"])
##        else:
##            out.append(pi_line["pi"])
##
##    return out
##
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