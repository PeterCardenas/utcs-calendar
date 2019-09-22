# UTCS Calendar Importer
This application imports the UTCS calendar into your Google Calendar.

## Install Libraries
`source <virtualenv name>/bin/activate`  
  
`pip3 install -r requirements.txt`

### Getting Google Calendar API Credentials

- Create a Google Cloud Platform project.
- Enable Google Calendar API
- Click the button saying "Download Client Configuration"
- Save the file `credentials.json` to utcs-calendar directory

## Run

`cd utcs-calendar`

`python3 utcs_calendar.py`

### First Time Run

- Sign into Google account
- When "This app isn't verified" pops up, click "Advanced", then click "Go to UTCS Calendar Converter (unsafe)"
- Click "Allow" 3 times
