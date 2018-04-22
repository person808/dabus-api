class Arrival:

    def int_to_time(i):
        minutes, seconds = divmod(i, 60)
        hours, minutes = divmod(minutes, 60)
        return f'{hours}:{minutes:02}:{seconds:02}'

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
        arrival.stopTime = Arrival.int_to_time(stop_time.arrival_time)
        arrival.trip = stop_time.trip_id
        arrival.vehicle = None

        arrival.headsign = stop_time.trip.trip_headsign
        arrival.route = stop_time.trip.route_id
        arrival.shape = stop_time.trip.shape_id

        return arrival
