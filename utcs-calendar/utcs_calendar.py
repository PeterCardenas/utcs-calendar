from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import date
from datetime import datetime
import sys
import re
from urllib.parse import urljoin

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar']

UTCS_LINK = "https://apps.cs.utexas.edu"

CALENDAR_LINK = UTCS_LINK + "/calendar/events"


def get_address():
    location_name = ""

    location = ""
    if "GDC" in location_name:
        location = "Gates Dell Complex"
    elif "POB" in location_name:
        location = "Peter O'Donnell Jr Building"
    elif "1.304" in location_name:
        location = "Gates Dell Complex"
    elif "EER" in location_name:
        location = "Engineering Education and Research Center (EER)"
    elif "AT&T" in location_name:
        location = "AT&T Executive Education and Conference Center"
    elif "Union" in location_name:
        location = "Texas Union"
    elif "Etter-Harbin" in location_name:
        location = "Etter-Harbin Alumni Center"
    elif "Frank Erwin" in location_name:
        location = "Frank C. Erwin, Jr., Special Events Center"
    elif "Pizza" in location_name:
        location = "The Varsity Pizza & Pints"
    elif "Palmer" in location_name:
        location = "Palmer Events Center"
    elif "ECJ" in location_name:
        location = "Ernest Cockrell Jr, Hall"

    if len(location) == 0:
        print("No address stored for location name:", location_name)

    return location


def create_event(title, year, month, day, description, location, all_day, start_time_hour=0, start_time_minute=0,
                 end_time_hour=0, end_time_minute=0):
    event = dict()
    event['summary'] = title
    event['description'] = description
    event['location'] = location
    event["start"] = dict()
    event["end"] = dict()

    if all_day:
        event["start"]["date"] = date(year, month, day).isoformat()
        event["end"]["date"] = date(year, month, day).isoformat()
    else:
        event["start"]["dateTime"] = datetime(year, month, day,
                                              start_time_hour, start_time_minute, 0, 0).isoformat()
        event["start"]["timeZone"] = "America/Chicago"
        event["end"]["dateTime"] = datetime(year, month, day,
                                            end_time_hour, end_time_minute, 0, 0).isoformat()
        event["end"]["timeZone"] = "America/Chicago"

    return event


def scrape_events():
    year = 2019
    month = 9
    event_list = []
    while year != 2020 or month != 6:
        month_link = CALENDAR_LINK + "/month/" + str(year) + "-" + str(month)
        month_html = requests.get(month_link).content
        driver = BeautifulSoup(markup=month_html, features="html.parser")
        day_elements = driver.select(selector="td.single-day")
        for day_element in day_elements:
            sys.stdout.write("\r%i events added" % len(event_list))
            sys.stdout.flush()
            raw_date = day_element.get(key="data-date")
            day = int(raw_date.split(sep="-")[2])
            events = day_element.select(selector='div.item')
            for event in events:
                title_element = event.select(selector="div.views-field-title a")[0]
                url = urljoin(UTCS_LINK, title_element.get(key="href"))
                title = title_element.get_text()
                location_element = event.select(selector="div.views-field-field-location-1")[0]
                location = location_element.get_text()
                if location == "":
                    room_element = event.select(selector="div.views-field-field-room-1")[0]
                    location = room_element.get_text()
                description = "URL: " + url
                all_day = True
                time_elements = event.select(selector="div.date-display-range")
                if len(time_elements) > 0:
                    all_day = False
                    time_element = time_elements[0]
                    start_time_element = time_element.select(selector="span.date-display-start")[0]
                    start_time = start_time_element.get_text()
                    start_time_components = re.split(pattern="[ :]", string=start_time)
                    start_time_hour = int(start_time_components[0])
                    start_time_minute = int(start_time_components[1])
                    if start_time_components[2] == "pm" and start_time_hour != 12:
                        start_time_hour += 12
                    end_time_element = time_element.select(selector="span.date-display-end")[0]
                    end_time = end_time_element.get_text()
                    end_time_components = re.split(pattern="[ :]", string=end_time)
                    end_time_hour = int(end_time_components[0])
                    end_time_minute = int(end_time_components[1])
                    if end_time_components[2] == "pm" and end_time_hour != 12:
                        end_time_hour += 12
                    event = create_event(title=title, year=year, month=month, day=day, start_time_hour=start_time_hour,
                                         start_time_minute=start_time_minute, end_time_hour=end_time_hour,
                                         end_time_minute=end_time_minute, description=description, location=location,
                                         all_day=all_day)
                else:
                    event = create_event(title=title, year=year, month=month, day=day,
                                         description=description, location=location, all_day=all_day)
                event_list.append(event)
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    return event_list


def google_calendar():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def upload_events(service, events):
    page_token = None
    next_page_exists = True
    calendar_list = service.calendarList().list(pageToken=page_token).execute()
    calendar = None
    while not calendar and next_page_exists:
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == 'UTCS':
                calendar = calendar_list_entry
        if not calendar:
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                next_page_exists = False

    if calendar:
        service.calendars().delete(calendarId=calendar['id']).execute()

    calendar_body = {
        'summary': 'UTCS'
    }
    calendar = service.calendars().insert(body=calendar_body).execute()
    batch = service.new_batch_http_request()

    for index, event in enumerate(events):
        sys.stdout.write("\rUploaded %i Events" % index)
        sys.stdout.flush()
        try:
            batch.add(service.events().insert(calendarId=calendar['id'], body=event))
        except TypeError:
            print(event)
    batch.execute()


def main():
    print('Getting authentication...')
    service = google_calendar()
    print('Authenticated.')
    print('Getting events...')
    events = scrape_events()
    print('\nGot events.')
    print('Uploading events...')
    upload_events(service, events)
    print('\nUploaded events.')


main()
