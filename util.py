import os
import requests

import structlog

structlog.configure(logger_factory=structlog.PrintLoggerFactory())
logger = structlog.get_logger(processors=[structlog.processors.JSONRenderer()])


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
