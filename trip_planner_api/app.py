import falcon

from .controllers.health import HealthCheck
from .controllers.travel import TravelOptions


api = application = falcon.API()

health = HealthCheck()
travel = TravelOptions()

api.add_route("/health", health)
api.add_route("/travel", travel)
