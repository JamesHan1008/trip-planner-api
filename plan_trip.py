import os
import requests

import structlog

import pandas as pd

structlog.configure(logger_factory=structlog.PrintLoggerFactory())
logger = structlog.get_logger(processors=[structlog.processors.JSONRenderer()])


def _get_seconds_from_duration_string(duration_string, duration_format):
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


def _get_duration_string_from_seconds(duration_seconds, duration_format):
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


def find_nearby_airports(latitude, longitude, limit=20):
    """
    Find the nearby airports of a given coordinate.
    :param latitude: float: latitude of the location of interest
    :param longitude: float: longitude of the location of interest
    :param limit: int: maximum number of airports to find
    :return: dict: keys are airport three letter codes, and values are dictionaries of airport information
    """
    max_lat_diff = 0.5
    max_lon_diff = 0.5

    url = "{route}/{resource}".format(
        route=os.getenv("SKYPICKER_API_ROUTE"),
        resource="locations",
    )
    params = {
        "type": "box",
        "low_lat": latitude - max_lat_diff,
        "high_lat": latitude + max_lat_diff,
        "low_lon": longitude - max_lon_diff,
        "high_lon": longitude + max_lon_diff,
        "locale": "en-US",
        "location_types": "airport",
        "limit": limit,
    }
    r = requests.get(url=url, params=params).json()

    airports = {}
    for location in r["locations"]:
        airports[location["code"]] = {
            "latitude": location["location"]["lat"],
            "longitude": location["location"]["lon"],
        }

    return airports


def search_flights(origin, destination, date_from, date_to):
    """
    Search for flights based on the origin and destination airports, and with in a certain date range.
    :param origin: string: three letter code of the origin airport
    :param destination: string: three letter code of the destination airport
    :param date_from: string ("dd/mm/yyyy"): departure date to begin searching from
    :param date_to: string ("dd/mm/yyyy"): departure date to stop searching at
    :return: dict: keys are trip IDs (multiple IDs separated with '|' if flight has stops), and values are dictionaries
        of flight information.
    """
    url = "{route}/{resource}".format(
        route=os.getenv("SKYPICKER_API_ROUTE"),
        resource="flights",
    )
    params = {
        "flyFrom": "airport:" + origin,
        "to": "airport:" + destination,
        "dateFrom": date_from,
        "dateTo": date_to,
        "partner": "picky",
    }
    r = requests.get(url=url, params=params).json()

    flights = {}
    for flight in r["data"]:
        flights[flight["id"]] = {
            "price": flight["price"],
            "duration": flight["fly_duration"],
            "airlines": flight["airlines"],
            "routes": flight["routes"],
        }

    return flights


def get_airports_travel_info(latitude, longitude, airports, to_airports):
    """
    Get the travel information of going to or from nearby airports
    :param latitude: float: latitude of the location of interest
    :param longitude: float: longitude of the location of interest
    :param airports: dict: keys are airport three letter codes, and values are dictionaries of airport information
    :param to_airports: boolean: True if getting travel information to airports, and False if from airports
    :return: dict: keys are airport three letter codes, and values are dictionaries of travel information, including:
        distance: int: distance in meters
        duration: int: travel time in seconds
    """
    airport_codes = []
    airport_locations = []
    for code, info in airports.items():
        airport_codes.append(code)
        airport_locations.append("{},{}".format(info["latitude"], info["longitude"]))

    if to_airports:
        distances = make_distance_matrix_request(
            origins="{},{}".format(latitude, longitude),
            destinations="|".join(airport_locations),
            origin_labels=["origin"],
            destination_labels=airport_codes,
            group_by_origins=True,
        )
        distances = distances["origin"]
    else:
        distances = make_distance_matrix_request(
            origins="|".join(airport_locations),
            destinations="{},{}".format(latitude, longitude),
            origin_labels=airport_codes,
            destination_labels=["destinations"],
            group_by_origins=False,
        )
        distances = distances["destinations"]

    return distances


def get_all_air_travel_options(origin_lat, origin_lon, destination_lat, destination_lon, travel_date):
    """
    Get all of the air travel options and the detailed information about the options
    :param origin_lat: float: latitude of the origin
    :param origin_lon: float: longitude of the origin
    :param destination_lat: float: latitude of the destination
    :param destination_lon: float: longitude of the destination
    :param travel_date: string ("dd/mm/yyyy"): departure date to search flights on
    :return: pandas.DataFrame: each row is a travel option, and each column is some information about the travel option
    """
    logger.info("getting all air travel options")

    origin_airports = find_nearby_airports(latitude=origin_lat, longitude=origin_lon)
    destination_airports = find_nearby_airports(latitude=destination_lat, longitude=destination_lon)

    travel_to_airports = get_airports_travel_info(
        latitude=origin_lat, longitude=origin_lon,
        airports=origin_airports, to_airports=True)
    travel_from_airports = get_airports_travel_info(
        latitude=destination_lat, longitude=destination_lon,
        airports=destination_airports, to_airports=False)

    travel_options = []
    for origin_airport in origin_airports:
        for destination_airport in destination_airports:
            duration_to_airport = travel_to_airports[origin_airport]["duration"]["value"]
            duration_from_airport = travel_from_airports[destination_airport]["duration"]["value"]

            flights = search_flights(
                origin=origin_airport,
                destination=destination_airport,
                date_from=travel_date,
                date_to=travel_date,
            )
            logger.info("{} to {}: {} flights found".format(origin_airport, destination_airport, len(flights)))

            for flight_ids, flight_info in flights.items():
                duration = _get_seconds_from_duration_string(flight_info["duration"], "..h ..m")
                duration += duration_to_airport + duration_from_airport

                time_at_airport = 5400
                duration += time_at_airport * 2

                travel_options.append({
                    "origin_airport": origin_airport,
                    "destination_airport": destination_airport,
                    "travel_time": _get_duration_string_from_seconds(duration, "{hours}h {minutes}m"),
                    "travel_time_seconds": duration,
                    "airlines": flight_info["airlines"],
                    "price": flight_info["price"],
                    "travel_method": "flight",
                })

    return pd.DataFrame(travel_options)


def main():
    travel_options = get_all_air_travel_options(
        origin_lat=37.6737957,
        origin_lon=-122.0795195,
        destination_lat=34.0932502,
        destination_lon=-118.1165166,
        travel_date="19/03/2019",
    )
    travel_options.to_csv("travel_options.csv")


if __name__ == "__main__":
    main()
