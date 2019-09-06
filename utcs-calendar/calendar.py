from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
            all_day = "False"

            start_time_elements = driver.find_elements(By.CSS_SELECTOR, "span.date-display-start")
            start_time = ""
            if len(start_time_elements) > 0:
                start_time = start_time_elements[0].text
                start_time = start_time[:-2] + " " + start_time[-2:].upper()
                end_time_elements = driver.find_elements(By.CSS_SELECTOR, "span.date-display-end")
                end_time = ""
                if len(end_time_elements) > 0:
                    end_time = end_time_elements[0].text
                    end_time = end_time[:-2] + " " + end_time[-2:].upper()
            else:
                all_day = "True"

            description_parts = driver.find_elements(By.CSS_SELECTOR, "div.field-type-text-with-summary p")
            description = ""
            if len(description_parts) > 0:
                description = combine_description(description_parts)

            contact_name_elements = driver.find_elements(By.CSS_SELECTOR, "div.field-name-field-name div.field-items")
            contact_name = ""
            if len(contact_name_elements) > 0:
                contact_name = contact_name_elements[0].text

            contact_email_elements = driver.find_elements(By.CSS_SELECTOR, "div.field-name-field-email div.field-items")
            contact_email = ""
            if len(contact_email_elements) > 0:
                contact_email = contact_email_elements[0].text

            location_elements = driver.find_elements(By.CSS_SELECTOR, "div.field-name-field-location div.field-items")
            location = ""
            if len(location_elements) > 0:
                location = location_elements[0].text
            else:
                room_elements = driver.find_elements(By.CSS_SELECTOR, "div.field-name-field-room div.field-items")
                if len(room_elements) > 0:
                    location = room_elements[0].text
                else:
                    location = "GDC"
            if "GDC" in location:
                location = "Gates Dell Complex"
            elif "POB" in location:
                location = "Peter O'Donnell Jr Building"
            elif "1.304" in location:
                location = "Gates Dell Complex"
            elif "EER" in location:
                location = "Engineering Education and Research Center (EER)"
            elif "AT&T" in location:
                location = "AT&T Executive Education and Conference Center"
            elif "Union" in location:
                location = "Texas Union"
            elif "Etter-Harbin" in location:
                location = "Etter-Harbin Alumni Center"
            elif "Frank Erwin" in location:
                location = "Frank C. Erwin, Jr., Special Events Center"
            elif "Pizza" in location:
                location = "The Varsity Pizza & Pints"
            elif "Palmer" in location:
                location = "Palmer Events Center"
            else:
                print("Subject:", subject, "Date:", date, "Location:", location, "URL:", url)

            description = "\"{0}{1}URL: {2}\n\n{3}\"".format(
                "Contact Name: " + contact_name + "\n\n" if len(contact_name) > 0 else contact_name,
                "Contact Email: " + contact_email + "\n\n" if len(contact_email) > 0 else contact_email,
                url,
                description
            )
            location = "\"" + location + "\""
            subject = "\"" + subject + "\""
            csv.write(subject + "," +
                      date + "," +
                      start_time + "," +
                      date + "," +
                      end_time + "," +
                      all_day + "," +
                      description + "," +
                      location + "," +
                      "False"
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


write_csv()
