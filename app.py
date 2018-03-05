import os
import pygtfs
import requests
import xmltodict
from flask import Flask, abort, jsonify, make_response


basedir = os.path.abspath(os.path.dirname(__file__))
API_KEY = os.environ.get('DABUS_API_KEY')
DATABASE_URI = os.environ.get('DATABASE_URL') or os.path.join(basedir, 'gtfs.sqlite')
app = Flask(__name__)
schedule = pygtfs.Schedule(DATABASE_URI)


def remove_keys(obj, rubbish):
    if isinstance(obj, dict):
        obj = {
            key: remove_keys(value, rubbish)
            for key, value in obj.items()
            if key not in rubbish}
    elif isinstance(obj, list):
        obj = [remove_keys(item, rubbish)
               for item in obj
               if item not in rubbish]
    return obj


def jsonify_clean(obj):
    """Wrapper around jsonify the removes instances of '_sa_instance_state' key
    from response."""
    return jsonify(remove_keys(obj, ['_sa_instance_state']))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/thebus/api/v1.0/stops', methods=['GET'])
def get_stops():
    return jsonify_clean([vars(stop) for stop in schedule.stops])


@app.route('/thebus/api/v1.0/stops/<int:stop_id>', methods=['GET'])
def get_stop(stop_id):
    try:
        stop = schedule.stops_by_id(stop_id)[0]
        return jsonify_clean(vars(stop))
    except IndexError:
        abort(404)


@app.route('/thebus/api/v1.0/arrivals/realtime/<int:stop_id>', methods=['GET'])
def get_realtime_stop_arrivals(stop_id):
    url_parameters = {'key': API_KEY, 'stop': stop_id}
    try:
        response = requests.get(
            'http://api.thebus.org/arrivals', params=url_parameters)
    except ConnectionError:
        abort(404)
    # Get xml tree from response and convert it to a dictionary
    response_dict = xmltodict.parse(response.text)
    if 'arrival' in response_dict['stopTimes']:
        return jsonify_clean(response_dict['stopTimes']['arrival'])
    else:
        return jsonify_clean([])


@app.route(
    '/thebus/api/v1.0/arrivals/scheduled/<int:stop_id>', methods=['GET'])
def get_scheduled_stop_arrivals(stop_id):
    try:
        stop = schedule.stops_by_id(stop_id)[0]
        response_list = [vars(arrival) for arrival in stop.stop_times]
        for arrival in response_list:
            # Convert timedelta back to 24 hour time
            arrival['arrival_time'] = str(arrival['arrival_time'])
            arrival['departure_time'] = str(arrival['departure_time'])
            # Add missing trip fields to response
            trip = schedule.trips_by_id(arrival['trip_id'])[0]
            arrival['headsign'] = trip.trip_headsign
            arrival['route'] = trip.route_id
            arrival['shape'] = trip.shape_id
        return jsonify_clean(response_list)
    except IndexError:
        abort(404)


@app.route('/thebus/api/v1.0/routes', methods=['GET'])
def get_routes():
    return jsonify_clean([vars(route) for route in schedule.routes])


@app.route('/thebus/api/v1.0/shapes/<string:shape_id>', methods=['GET'])
def get_shape(shape_id):
    return jsonify_clean([vars(shape) for shape in schedule.shapes if shape.shape_id == shape_id])


@app.route('/thebus/api/v1.0/trips/<string:trip_id>', methods=['GET'])
def get_trip(trip_id):
    return jsonify_clean(vars(schedule.trips_by_id(trip_id)[0]))


if __name__ == '__main__':
    app.run(host='0.0.0.0')