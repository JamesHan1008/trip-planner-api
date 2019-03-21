import json

import falcon


class HealthCheck(object):
    """ Health check resource """
    def on_get(self, req, resp):
        doc = {
            "name": "trip_planner_api"
        }

        resp.content_type = falcon.MEDIA_JSON
        resp.body = json.dumps(doc)
