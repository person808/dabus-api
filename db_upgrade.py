import json
import os
import requests
import subprocess
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

# Transitfeed api key
API_KEY = os.environ.get('TRANSITFEEDS_API_KEY')
FEED_ID = 'thebus-honolulu/57'
DATABASE_URI = os.environ.get('DATABASE_URL') or os.path.join(
    basedir, 'gtfs.sqlite')

# URL parametes
parameters = {'key': API_KEY, 'feed': FEED_ID}


def new_version_available():
    """Returns True if a new version of the gtfs data is available."""
    response = requests.get(
        'https://api.transitfeeds.com/v1/getFeedVersions', params=parameters)
    versions = json.loads(response.text)
    # Get the start date of the latest feed
    latest_version = versions['results']['versions'][0]['d']['s']
    if latest_version == datetime.now().strftime('%Y%m%d'):
        return True
    return False


if not os.path.isfile(DATABASE_URI) or new_version_available():
    # Download new gtfs zip
    response = requests.get(
        'https://api.transitfeeds.com/v1/getLatestFeedVersion',
        params=parameters,
        stream=True)
    with open('gtfs.zip', mode='wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

    subprocess.run(['gtfs2db', 'overwrite', 'gtfs.zip', DATABASE_URI])
    os.remove('gtfs.zip')