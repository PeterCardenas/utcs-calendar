# UTCS Calendar Converter
This application converts the UTCS Events Calendar to CSV file. This CSV file can then be imported into your Google
Calendar. Google Calendar API implementation in progress.

## Install Libraries
`source <virtualenv name>/bin/activate`  
  
`pip3 install -r requirements.txt`

### Getting Google Calendar API Credentials

- Create a Google Cloud Platform project.
- Enable Google Calendar API
- Click the button saying "Download Client Configuration"
- Save the file `credentials.json` to utcs-calendar directory

## Run
`python3 utcs-calendar/utcs_calendar.py`

