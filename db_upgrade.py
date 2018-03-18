import os
import requests
import subprocess
from config import DATABASE_URI

basedir = os.path.abspath(os.path.dirname(__file__))

# Transitfeed api key
FEED_URL = 'http://webapps.thebus.org/transitdata/Production/google_transit.zip'

response = requests.get(FEED_URL, stream=True)
with open('gtfs.zip', mode='wb') as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)

subprocess.run(['gtfs2db', 'overwrite', 'gtfs.zip', DATABASE_URI])
os.remove('gtfs.zip')