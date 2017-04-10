#!/usr/bin/python3
from cloudbot import hook
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from datetime import timezone
import datetime
import pytz
import dateutil.parser

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = '/home/michael/irc/client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

def aslocaltimestr(utc_dt):
    return utc_dt.strftime('%Y-%m-%d %I:%M %p')

def aslocaltimestr2(utc_dt):
    return utc_dt.strftime('%I:%M %p')

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    return credentials

@hook.command(autohelp=False)
def calendar():
    """Gets next TC Maker calendar event"""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    #print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='twincitiesmaker@gmail.com', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    for event in events:
        start = dateutil.parser.parse(event['start'].get('dateTime', event['start'].get('date')))
        end = dateutil.parser.parse(event['end'].get('dateTime', event['end'].get('date')))
        if event['summary'] != "":
            s = '{} - {}: \x02{}\x02'.format(aslocaltimestr(start), aslocaltimestr2(end), event['summary'])
            return s

