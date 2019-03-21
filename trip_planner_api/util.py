import json
import os
import requests

import structlog

structlog.configure(logger_factory=structlog.PrintLoggerFactory())
logger = structlog.get_logger(processors=[structlog.processors.JSONRenderer()])

GAS_COST_PER_GALLON = None


def get_seconds_from_duration_string(duration_string, duration_format):
    """
    Calculated the number of seconds represented by a duration represented in a string
    :param duration_string: string: duration represented in a human-readable string
    :param duration_format: string: one of the duration string formats supported
    :return: int: number of seconds
    """
    if duration_format == "..h ..m":
        hours, remaining = duration_string.split("h ")
        minutes = remaining.split("m")[0]
        return (int(hours) * 60 + int(minutes)) * 60
    else:
        msg = "unsupported format"
        logger.error(msg, format=duration_format)
        raise Exception(msg)


def get_duration_string_from_seconds(duration_seconds, duration_format):
    """
    Create the human-readable string representation of the duration given in number of seconds
    :param duration_seconds: int: duration in seconds
    :param duration_format: string: format string for the duration
    :return: string: human-readable string of the duration
    """
    try:
        hours, remaining = divmod(duration_seconds, 3600)
        minutes = remaining // 60
        return duration_format.format(hours=hours, minutes=minutes)
    except KeyError:
        msg = "unsupported format"
        logger.error(msg, format=duration_format)
        raise Exception(msg)


def get_distance_string_from_meters(distance_meters, distance_format):
    """
    Create the human-readable string representation of the distance given in meters
    :param distance_meters: int: distance in meters
    :param distance_format: string: format string for the distance
    :return: string: human-readable string of the distance
    """
    try:
        km = distance_meters // 1000
        return distance_format.format(km=km)
    except KeyError:
        msg = "unsupported format"
        logger.error(msg, format=distance_format)
        raise Exception(msg)


def get_gas_cost(distance_meters, latitude, longitude):
    """
    Estimate the gas cost for driving the given distance by using an average fuel consumption and the current gas price
    :param distance_meters: int: distance in meters
    :param latitude: float: latitude of the origin
    :param longitude: float: longitude of the origin
    :return: int: gas cost in U.S. dollars
    """
    global GAS_COST_PER_GALLON

    liters_per_meter = 0.0001
    liters_used = distance_meters * liters_per_meter
    cost_per_liter = 0.75
    cost_per_gallon = None

    if GAS_COST_PER_GALLON is None:
        url = "{route}/{latitude}/{longitude}/{distance}/{fuel_type}/{sort_by}/{apikey}.json?".format(
            route=os.getenv("MYGASFEED_API_ROUTE_DEV"),
            latitude=latitude,
            longitude=longitude,
            distance=50,
            fuel_type="reg",
            sort_by="distance",
            apikey=os.getenv("MYGASFEED_API_KEY_DEV"),
        )
        headers = {"Accept": "application/json"}

        try:
            r = requests.get(url=url, headers=headers).text
            json_begin = r.find("{\"status\":")
            r = r[json_begin:]
            r = json.loads(r)

            if r["status"]["code"] == 200:
                if len(r["stations"]) == 0:
                    logger.info("nearby gas prices not found, use default gas cost per liter: {}".format(cost_per_liter))
                else:
                    cost_per_gallon = float(r["stations"][0]["reg_price"])
                    logger.info("gas price found through myGasFeed", cost_per_gallon=cost_per_gallon)
                    GAS_COST_PER_GALLON = cost_per_gallon
            else:
                logger.error("myGasFeed responded with bad status code",
                             status_code=r["status"]["code"],
                             default_cost_per_liter=cost_per_liter,
                             url=url)
        except Exception as e:
            logger.error("myGasFeed request error",
                         default_cost_per_liter=cost_per_liter,
                         url=url,
                         exception=e)
    else:
        cost_per_gallon = GAS_COST_PER_GALLON

    if cost_per_gallon:
        cost_per_liter = cost_per_gallon / 3.78541

    return liters_used * cost_per_liter


def make_distance_matrix_request(origins, destinations, origin_labels, destination_labels, group_by_origins):
    """
    Make a request to the Google Maps Distance Matrix API.
    :param origins: string: any valid input for the Distance Matrix API's `origins` parameter
    :param destinations:  string: any valid input for the Distance Matrix API's `destinations` parameter
    :param origin_labels: list of strings: labels for the origins
    :param destination_labels: list of strings: labels for the destinations
    :param group_by_origins: boolean: if True, the returned dict would have origins as keys, otherwise destinations
    :return: dict of dict: distances and driving times between each origin and each destination
    """
    if group_by_origins:
        logger.info("requesting Google Maps Distance Matrix API", origins=origins, destinations=destination_labels)
    else:
        logger.info("requesting Google Maps Distance Matrix API", origins=origin_labels, destinations=destinations)

    url = "{route}/{resource}/{format}".format(
        route=os.getenv("GOOGLE_MAPS_API_ROUTE"),
        resource="distancematrix",
        format="json",
    )
    params = {
        "key": os.getenv("GOOGLE_MAPS_API_KEY"),
        "origins": origins,
        "destinations": destinations,
    }
    r = requests.get(url=url, params=params).json()

    if group_by_origins:
        distances = {o: {d: None for d in destination_labels} for o in origin_labels}
    else:
        distances = {d: {o: None for o in origin_labels} for d in destination_labels}

    num_rows = len(origin_labels)
    num_cols = len(destination_labels)
    for row in range(num_rows):
        for col in range(num_cols):
            info = r["rows"][row]["elements"][col]
            info = {k: info[k] for k in ["distance", "duration"]}

            if group_by_origins:
                distances[origin_labels[row]][destination_labels[col]] = info
            else:
                distances[destination_labels[col]][origin_labels[row]] = info

    return distances
