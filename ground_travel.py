import structlog

import pandas as pd

from util import get_duration_string_from_seconds
from util import get_gas_cost
from util import make_distance_matrix_request

structlog.configure(logger_factory=structlog.PrintLoggerFactory())
logger = structlog.get_logger(processors=[structlog.processors.JSONRenderer()])


def _get_driving_option(origin_lat, origin_lon, destination_lat, destination_lon):
    """
    Get the travel information for the driving option
    :param origin_lat: float: latitude of the origin
    :param origin_lon: float: longitude of the origin
    :param destination_lat: float: latitude of the destination
    :param destination_lon: float: longitude of the destination
    :return: pandas.DataFrame: one row containing the travel option of driving
    """
    driving_info = make_distance_matrix_request(
        origins="{},{}".format(origin_lat, origin_lon),
        destinations="{},{}".format(destination_lat, destination_lon),
        origin_labels=["origin"],
        destination_labels=["destination"],
        group_by_origins=True,
    )
    driving_info = driving_info["origin"]["destination"]
    duration = driving_info["duration"]["value"]
    gas_cost = get_gas_cost(
        distance_meters=driving_info["distance"]["value"],
        latitude=origin_lat,
        longitude=origin_lon,
    )

    driving_option = [{
        "travel_time": get_duration_string_from_seconds(duration, "{hours}h {minutes}m"),
        "travel_time_seconds": duration,
        "driving_distance": driving_info["distance"]["text"],
        "driving_distance_meters": driving_info["distance"]["value"],
        "gas_cost": gas_cost,
        "total_cost": gas_cost,
        "travel_method": "driving",
    }]

    return pd.DataFrame(driving_option)


def get_all_ground_travel_options(origin_lat, origin_lon, destination_lat, destination_lon, travel_date):
    """
    Get all of the ground travel options and the detailed information about the options
    :param origin_lat: float: latitude of the origin
    :param origin_lon: float: longitude of the origin
    :param destination_lat: float: latitude of the destination
    :param destination_lon: float: longitude of the destination
    :param travel_date: string ("dd/mm/yyyy"): departure date
    :return: pandas.DataFrame: each row is a travel option, and each column is some information about the travel option
    """
    logger.info("getting all ground travel options")

    driving_option = _get_driving_option(origin_lat, origin_lon, destination_lat, destination_lon)

    return driving_option
