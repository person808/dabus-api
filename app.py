import requests
import xmltodict
from Arrival import Arrival
from config import API_KEY, FEED_ID, dao
from flask import Flask, abort, jsonify, make_response

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
    stop = dao.stop(stop_id, FEED_ID)
    return jsonify_clean(vars(stop))


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
    except IndexError:
        abort(404)


@app.route('/thebus/api/v1.0/routes', methods=['GET'])
def get_routes():
    return jsonify_clean([vars(route) for route in dao.routes()])


@app.route('/thebus/api/v1.0/routes/shape/<string:route_id>', methods=['GET'])
def get_route_shape(route_id):
    route = dao.route(route_id, FEED_ID)
    shape_id = route.trips[0].shape_id
    return get_shape(shape_id)


@app.route('/thebus/api/v1.0/shapes/<string:shape_id>', methods=['GET'])
def get_shape(shape_id):
    points = list(map(lambda x: vars(x), dao.shape(shape_id, FEED_ID).points))
    return jsonify_clean(points)


@app.route('/thebus/api/v1.0/trips/<string:trip_id>', methods=['GET'])
def get_trip(trip_id):
    return jsonify_clean(vars(dao.trip(trip_id, FEED_ID)))


if __name__ == '__main__':
    app.run()