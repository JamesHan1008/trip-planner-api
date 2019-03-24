import falcon
from falcon.http_status import HTTPStatus

ALLOWED_ORIGINS = ["http://localhost:3000"]


class HandleCORS(object):
    def process_request(self, req, resp):
        origin = req.get_header("Origin")
        if origin in ALLOWED_ORIGINS:
            resp.set_header("Access-Control-Allow-Origin", origin)

        resp.set_header("Access-Control-Allow-Methods", "*")
        resp.set_header("Access-Control-Allow-Headers", "*")

        if req.method == "OPTIONS":
            raise HTTPStatus(falcon.HTTP_200, body="\n")
