import os
from gtfslib.dao import Dao

basedir = os.path.abspath(os.path.dirname(__file__))
API_KEY = os.environ.get('DABUS_API_KEY')
DATABASE_URI = os.environ.get('DATABASE_URL') or os.path.join(basedir, 'gtfs.sqlite')
FEED_ID = 'hnl'
dao = Dao(DATABASE_URI)
