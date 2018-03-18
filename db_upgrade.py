import os
import requests
import subprocess

basedir = os.path.abspath(os.path.dirname(__file__))

# Transitfeed api key
DATABASE_URI = os.environ.get('DATABASE_URL') or os.path.join(
    basedir, 'gtfs.sqlite')
FEED_URL = 'http://webapps.thebus.org/transitdata/Production/google_transit.zip'

response = requests.get(FEED_URL, stream=True)
with open('gtfs.zip', mode='wb') as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)

subprocess.run(['gtfs2db', 'overwrite', 'gtfs.zip', DATABASE_URI])
os.remove('gtfs.zip')