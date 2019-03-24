import json

import falcon
import simplejson
import structlog

from trip_planner_api.plan_trip import analyze_travel_option

structlog.configure(logger_factory=structlog.PrintLoggerFactory())
logger = structlog.get_logger(processors=[structlog.processors.JSONRenderer()])


class TravelOptions(object):
    """ Travel options resource """
    def on_post(self, req, resp):
        logger.info("requesting TravelOptions API resource")

        # req_body = req.stream.read()
        # req_json = json.loads(req_body)
        #
        # trip_params = dict()
        # trip_params["origin_lat"] = float(req_json["origin_lat"])
        # trip_params["origin_lon"] = float(req_json["origin_lon"])
        # trip_params["destination_lat"] = float(req_json["destination_lat"])
        # trip_params["destination_lon"] = float(req_json["destination_lon"])
        # trip_params["travel_date"] = req_json["travel_date"]
        #
        # traveler_params = dict()
        # traveler_params["value_one_hour"] = int(req_json["value_one_hour"])
        # traveler_params["value_ten_hours"] = int(req_json["value_ten_hours"])
        #
        # logger.info("TravelOptions trip parameters", trip_params=trip_params)
        # logger.info("TravelOptions traveler parameters", traveler_params=traveler_params)
        #
        # ordered_travel_options = analyze_travel_option(trip_params, traveler_params)
        # ordered_travel_options = ordered_travel_options.to_dict(orient="index")
        #
        # resp.content_type = falcon.MEDIA_JSON
        # resp.body = simplejson.dumps(ordered_travel_options, ignore_nan=True)

        with open("trip_planner_api/fixtures/travel_options.json", "r") as f:
            resp_body = json.load(f)
        resp.body = json.dumps(resp_body)
