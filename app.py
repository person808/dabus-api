import requests
import xmltodict
from flask import Flask, abort, jsonify, make_response
from gtfslib.model import Stop, StopTime, Trip

from Arrival import Arrival
from config import API_KEY, FEED_ID, dao

app = Flask(__name__)


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
    return jsonify_clean([vars(stop) for stop in dao.stops(batch_size=900)])


@app.route('/thebus/api/v1.0/stops/<string:stop_id>', methods=['GET'])
def get_stop(stop_id):
    try:
        stop = dao.stop(stop_id, FEED_ID)
        return jsonify_clean(vars(stop))
    except TypeError:
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
    '/thebus/api/v1.0/arrivals/scheduled/<string:stop_id>', methods=['GET'])
def get_scheduled_stop_arrivals(stop_id):
    try:
        stop = dao.stop(stop_id, FEED_ID)
        response_list = []
        for stop_time in stop.stop_times:
            response_list.append(vars(Arrival.from_stop_time(stop_time)))
        return jsonify_clean(response_list)
    except AttributeError:
        abort(404)


@app.route('/thebus/api/v1.0/routes', methods=['GET'])
def get_routes():
    return jsonify_clean([vars(route) for route in dao.routes()])


@app.route('/thebus/api/v1.0/routes/<string:route_id>/shape', methods=['GET'])
def get_route_shape(route_id):
    try:
        route = dao.route(route_id, FEED_ID)
        shape_id = route.trips[0].shape_id
        return get_shape(shape_id)
    except AttributeError:
        abort(404)


@app.route('/thebus/api/v1.0/routes/<string:route_id>/stops', methods=['GET'])
def get_route_stops(route_id):
    try:
        stops = dao.stops(fltr=(StopTime.trip_id == Trip.trip_id) \
                          & (Trip.route_id == route_id) \
                          & (StopTime.stop_id == Stop.stop_id))
        stop_set = [vars(stop) for stop in stops]
        return jsonify_clean(stop_set)
    except AttributeError:
        abort(404)


@app.route('/thebus/api/v1.0/shapes/<string:shape_id>', methods=['GET'])
def get_shape(shape_id):
    try:
        points = list(map(lambda x: vars(x), dao.shape(shape_id, FEED_ID).points))
        return jsonify_clean(points)
    except AttributeError:
        abort(404)


@app.route('/thebus/api/v1.0/trips/<string:trip_id>', methods=['GET'])
def get_trip(trip_id):
    try:
        return jsonify_clean(remove_keys(vars(dao.trip(trip_id, FEED_ID)), 'stop_times'))
    except TypeError:
        abort(404)

@app.route('/thebus/api/v1.0/vehicles/realtime/<string:vehicle_id>', methods=['GET'])
def get_realtime_vehicle(vehicle_id):
    url_parameters = {'key': API_KEY, 'num': vehicle_id}
    try:
        response = requests.get(
            'http://api.thebus.org/vehicle', params=url_parameters)
    except ConnectionError:
        abort(404)
    # Get xml tree from response and convert it to a dictionary
    response_dict = xmltodict.parse(response.text)
    if 'vehicle' in response_dict['vehicles']:
        # In some cases the api returns old vehicle data. Always use the new one.
        if isinstance(response_dict['vehicles']['vehicle'], list):
            return jsonify_clean(response_dict['vehicles']['vehicle'][0])
        else:
            return jsonify_clean(response_dict['vehicles']['vehicle'])
    else:
        return jsonify_clean(response_dict)

if __name__ == '__main__':
    app.run()