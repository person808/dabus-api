import os
import requests
import subprocess
from config import DATABASE_URI, FEED_ID

basedir = os.path.abspath(os.path.dirname(__file__))

# Transitfeed api key
FEED_URL = 'http://webapps.thebus.org/transitdata/Production/google_transit.zip'

response = requests.get(FEED_URL, stream=True)
with open('gtfs.zip', mode='wb') as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)

subprocess.run(['gtfsdbloader', DATABASE_URI, '--load=gtfs.zip', '--lenient', '--id={}'.format(FEED_ID)])
os.remove('gtfs.zip')