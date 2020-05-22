#!/usr/bin/env python
# coding: utf-8

# In[134]:

from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import numpy as np
from imdb import IMDb
from imdb.helpers import sortedEpisodes
from itertools import dropwhile, islice, takewhile
from datetime import date
from time import sleep, strptime
import locale

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = r"C:\Users\Jonathan\TVScheduler\credentials.json"

def get_calendar_service():
   creds = None
   # The file token.pickle stores the user's access and refresh tokens, and is
   # created automatically when the authorization flow completes for the first
   # time.
   if os.path.exists(r"C:\Users\Jonathan\TVScheduler\token.pickle"):
       with open(r"C:\Users\Jonathan\TVScheduler\token.pickle", 'rb') as token:
           creds = pickle.load(token)
   # If there are no (valid) credentials available, let the user log in.
   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file(
               CREDENTIALS_FILE, SCOPES)
           creds = flow.run_local_server(port=0)

       # Save the credentials for the next run
       with open(r"C:\Users\Jonathan\TVScheduler\token.pickle", 'wb') as token:
           pickle.dump(creds, token)

   service = build('calendar', 'v3', credentials=creds)
   return service


# In[135]:


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(r"C:\Users\Jonathan\TVScheduler\token.pickle"):
        with open(r"C:\Users\Jonathan\TVScheduler\token.pickle", 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r"C:\Users\Jonathan\TVScheduler\credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(r"C:\Users\Jonathan\TVScheduler\token.pickle", 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 100 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    main()


# In[136]:


SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
if os.path.exists(r"C:\Users\Jonathan\TVScheduler\token.pickle"):
    with open(r"C:\Users\Jonathan\TVScheduler\token.pickle", 'rb') as token:
        creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
                r"C:\Users\Jonathan\TVScheduler\credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
    with open(r"C:\Users\Jonathan\TVScheduler\token.pickle", 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)


# In[137]:

locale.setlocale(locale.LC_ALL,'')

def getEps(title):
    #strip title input by user
    title=title.strip()
    # Create IMDb object
    i=IMDb()
    #search for title
    search_results=i.search_movie(title)
    # Get first search result that is a TV series
    search_results= filter(lambda s:s['kind']=='tv series',search_results)
    search_results=list(islice(search_results,0,1))
    #if no result found
    if len(search_results)==0: 
        return 'No TV series matches were found for "%s".'%title
    s=search_results[0]
    i.update(s,'episodes')
    s_title=s['long imdb title']
    #if no episode info found
    if (not s.has_key('episodes')) or len(s['episodes'])==0: 
        return 'Episode info is unavailable for %s.'%s_title
    s=sortedEpisodes(s)
    if len(s)==0: 
        return 'Episode info is unavailable for %s.'%s_title
    s.reverse()
    date_today=date.today()
    e=[]
    for ep_ind in range(0, len(s)):
        if s[ep_ind].has_key('original air date'):
            if (len(s[ep_ind]['original air date'])) == 4:
                s[ep_ind]['date']=strptime(s[ep_ind]['original air date'],'%Y')
            else:
                s[ep_ind]['date']=strptime(s[ep_ind]['original air date'].replace('.',''),'%d %b %Y')
        if s[ep_ind].has_key('date'):
            s[ep_ind]['date']=date(*s[ep_ind]['date'][0:3])
            s[ep_ind]['age']=(date_today - s[ep_ind]['date']).days
            if s[ep_ind]['age']>0:
                s[ep_ind]['has aired']=True
            else:
                s[ep_ind]['has aired']=False
                e.append(s[ep_ind])
        else:
            s[ep_ind]['has aired']=False
            e.append(s[ep_ind])
    #function to get season episode format for description 
    def getSE(e):
        if not isinstance(e['season'],int): 
            return ''
        Sstr='S'+str(e['season']).zfill(2)
        Estr='E'+str(e['episode']).zfill(2)
        return ' ('+Sstr+Estr+')'
    #function to get age of episode (negative if has not aired, positive if has aired)
    def getAge(e): 
        return locale.format('%i',abs(e['age']),grouping=True)
    #function to get date of episode 
    def getDate(e): 
        return e['date'].strftime('%a, ')+str(e['date'].day)+e['date'].strftime(' %b %y')
    titles = []
    descriptions = []
    dates = []
    for i in e:
        e_out=''
        if len(e)>0:
            e=i
            titles.append(s_title)
            descriptions.append(getSE(e))
            e_out=e_out+'The next upcoming episode '+ 'for '+s_title+ ' ' +'is "'+e['title']+'"'+getSE(e)+'.'
            if e.has_key('age'):
                e_schedule= 'in %s days'%getAge(e)
                e_out=e_out+' It airs '+e_schedule+', '+getDate(e)+'.'
                dates.append(getDate(e))
            else:
                e_out=e_out+' Its air date is unavailable.'
                dates.append('unknown')
        print(e_out)
    return titles, descriptions, dates


# In[149]:



def add_events(shows):
    #get current events listed in calendar
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=100, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    #accumulate the summary and description of events current in calendar
    event_summary=[]
    event_description=[]
    for event in events:
        event_summary.append(event.get('summary'))
        event_description.append(event.get('description'))
    #iterate over shows and add events
    for show in shows:
        a = getEps(show)
        if len(a) == 3:
            titles, descriptions, dates= a[0], a[1], a[2]
            if len(titles)>0:
                for i in range(0, len(titles)):
                    if dates[i] != 'unknown':
                        title = titles[i]
                        description = descriptions[i]
                        air_date = dates[i]
                        date_time = datetime.datetime.strptime(air_date, '%a, %d %b %y').strftime('%Y-%m-%d')
                        start = date_time + 'T07:00:00-07:00'
                        end = date_time + 'T22:00:00-07:00'
                        event = {
                          'summary': title,
                          'description': description,
                          'start': {
                            'dateTime': start,
                            'timeZone': 'America/New_York',
                          },
                          'end': {
                            'dateTime': end,
                            'timeZone': 'America/New_York',
                          },
                        }
                        #if event already in calendar dont add it
                        series_eps = [index for index,value in enumerate(event_summary) if value == event['summary']]
                        if len(series_eps) > 0:
                            if not (event['description'] in list(np.array(event_description)[series_eps])):
                                event = service.events().insert(calendarId='primary', body=event).execute()
                        else:
                            event = service.events().insert(calendarId='primary', body=event).execute()
                print('Events created for %s' % (show))
            else:
                print('No upcoming episode information for %s' % (show))
        else:
            print('No TV series matches were found for %s' % (show))
    return 'All events created'


# In[150]:


shows = ["It's Always Sunny in Philadelphia",'Los Espookys', "Bob's Burgers", "Black Monday", "Saturday Night Live", 
         "Barry", "Brooklyn Nine-Nine", 'Rick and Morty','Dave', "Tacoma FD", 'Last Week Tonight with John Oliver', 
         'The Righteous Gemstones', 'South Park', 'A.P. Bio', 'Atlanta', 'The Last Dance']
add_events(shows)

