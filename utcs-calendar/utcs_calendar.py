from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar']

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
WINDOW_SIZE = "1920,1080"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.binary_location = CHROME_PATH

CALENDAR_LINK = "https://apps.cs.utexas.edu/calendar/events/"

driver = webdriver.Chrome(
    executable_path=CHROMEDRIVER_PATH,
    options=chrome_options
)


def combine_description(description_parts):
    description_text = map(lambda part: part.text, description_parts)
    desc = "\n\n".join(description_text)
    return desc


def get_address():
    location_elements = driver.find_elements(By.CSS_SELECTOR, "div.field-name-field-location div.field-items")
    location_name = ""
    if len(location_elements) > 0:
        location_name = location_elements[0].text
    else:
        room_elements = driver.find_elements(By.CSS_SELECTOR, "div.field-name-field-room div.field-items")
        if len(room_elements) > 0:
            location_name = room_elements[0].text
        else:
            location_name = "GDC"

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

    if len(location) == 0:
        print("No address stored for location name:", location_name)

    return location


def get_time():
    start_time_elements = driver.find_elements(By.CSS_SELECTOR, "span.date-display-start")
    start_time = ""
    end_time_elements = driver.find_elements(By.CSS_SELECTOR, "span.date-display-end")
    end_time = ""
    all_day = "False"
    if len(start_time_elements) > 0:
        start_time = start_time_elements[0].text
        start_time = start_time[:-2] + " " + start_time[-2:].upper()
        if len(end_time_elements) > 0:
            end_time = end_time_elements[0].text
            end_time = end_time[:-2] + " " + end_time[-2:].upper()
    else:
        all_day = "True"

    ret = {
        start_time: start_time,
        end_time: end_time,
        all_day: all_day
    }
    return ret


def get_contact():
    contact_name_elements = driver.find_elements(By.CSS_SELECTOR, "div.field-name-field-name div.field-items")
    contact_name = ""
    if len(contact_name_elements) > 0:
        contact_name = contact_name_elements[0].text

    contact_email_elements = driver.find_elements(By.CSS_SELECTOR, "div.field-name-field-email div.field-items")
    contact_email = ""
    if len(contact_email_elements) > 0:
        contact_email = contact_email_elements[0].text

    return contact_name, contact_email


def get_description(contact_name, contact_email, url):
    description_parts = driver.find_elements(By.CSS_SELECTOR, "div.field-type-text-with-summary p")
    description = ""
    if len(description_parts) > 0:
        description = combine_description(description_parts)

    description = "\"{0}{1}URL: {2}\n\n{3}\"".format(
        "Contact Name: " + contact_name + "\n\n" if len(contact_name) > 0 else contact_name,
        "Contact Email: " + contact_email + "\n\n" if len(contact_email) > 0 else contact_email,
        url,
        description
    )

    return description


def write_csv():
    csv = open("events.csv", "w+")
    year = 2019
    month = 9
    csv.write("Subject,Start Date,Start Time,End Date,End Time,All Day Event,Description,Location,Private\n")
    while year != 2020 and month != 6:
        month_link = CALENDAR_LINK + "month/" + str(year) + "-" + str(month)
        driver.get(month_link)
        events = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td.single-day div.contents"))
        )
        for index in range(len(events)):
            link = events[index].find_element(By.CSS_SELECTOR, "a")
            link.click()
            url = driver.current_url
            subject = driver.find_element(By.CSS_SELECTOR, "h1#page-title").text
            date = driver.find_element(By.CSS_SELECTOR, "span.date-display-single").text.split(" ")[1]

            time = get_time()

            contact_name, contact_email = get_contact()

            location = get_address()

            description = get_description(contact_name, contact_email, url)
            location = "\"" + location + "\""
            subject = "\"" + subject + "\""
            csv.write(subject + "," +
                      date + "," +
                      time.get("start_time") + "," +
                      date + "," +
                      time.get("end_time") + "," +
                      time.get("all_day") + "," +
                      description + "," +
                      location + "," +
                      "False" +
                      "\n")
            driver.get(month_link)
            events = driver.find_elements(By.CSS_SELECTOR, "td.single-day div.contents")
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    csv.close()
    driver.quit()


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


def upload_events(calendar):
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    page_token = None
    next_page_exists = True
    calendar_list = calendar.calendarList().list(pageToken=page_token).execute()
    calendar = None
    while not calendar and next_page_exists:
        for calendar_list_entry in calendar_list['items']:
            if calendar_list_entry['summary'] == 'UTCS':
                calendar = calendar_list_entry
        if not calendar:
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                next_page_exists = False


def main():
    service = google_calendar()
    upload_events(service)


main()
