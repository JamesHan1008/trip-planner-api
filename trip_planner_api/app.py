import falcon

from .controllers.health import HealthCheck
from .controllers.travel import TravelOptions
from .middleware.handle_cors import HandleCORS

api = application = falcon.API(
    middleware=[
        HandleCORS()
    ]
)

health = HealthCheck()
travel = TravelOptions()

api.add_route("/health", health)
api.add_route("/travel", travel)
