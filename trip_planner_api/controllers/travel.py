import json

import falcon

from trip_planner_api.plan_trip import analyze_travel_option


class TravelOptions(object):
    """ Travel options resource """
    def on_get(self, req, resp):
        trip_params = dict()
        trip_params["origin_lat"] = float(req.get_param("origin_lat", required=True))
        trip_params["origin_lon"] = float(req.get_param("origin_lon", required=True))
        trip_params["destination_lat"] = float(req.get_param("destination_lat", required=True))
        trip_params["destination_lon"] = float(req.get_param("destination_lon", required=True))
        trip_params["travel_date"] = req.get_param("travel_date", required=True)

        traveler_params = dict()
        traveler_params["value_one_hour"] = req.get_param_as_int("value_one_hour", required=True)
        traveler_params["value_ten_hours"] = req.get_param_as_int("value_ten_hours", required=True)

        ordered_travel_options = analyze_travel_option(trip_params, traveler_params)

        resp.content_type = falcon.MEDIA_JSON
        resp.body = json.dumps(ordered_travel_options, indent=4)
