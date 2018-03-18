from config import schedule


class Arrival:

    @classmethod
    def from_stop_time(cls, stop_time):
        arrival = cls()
        arrival.canceled = 0
        arrival.date = None
        arrival.direction = None
        arrival.estimated = 0
        arrival.id = None
        arrival.latitude = None
        arrival.longitude = None
        arrival.stopTime = str(stop_time.arrival_time)
        arrival.trip = stop_time.trip_id
        arrival.vehicle = None

        trip = schedule.trips_by_id(arrival.trip)[0]
        arrival.headsign = trip.trip_headsign
        arrival.route = trip.route_id
        arrival.shape = trip.shape_id

        return arrival
