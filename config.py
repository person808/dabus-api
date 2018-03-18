import os
import pygtfs

basedir = os.path.abspath(os.path.dirname(__file__))
API_KEY = os.environ.get('DABUS_API_KEY')
DATABASE_URI = os.environ.get('DATABASE_URL') or os.path.join(basedir, 'gtfs.sqlite')
schedule = pygtfs.Schedule(DATABASE_URI)
