import os
import requests


def make_distance_matrix_request(origins, destinations, group_by_origins=True):
    """
    Make a request to the Google Maps Distance Matrix API.
    :param origins: string: any valid input for the Distance Matrix API's `origins` parameter
    :param destinations:  string: any valid input for the Distance Matrix API's `destinations` parameter
    :param group_by_origins: boolean: if True, the returned dict would have origins as keys, otherwise destinations
    :return: dict of dict: distances and driving times between each origin and each destination
    """
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

    origins = origins.split("|")
    destinations = destinations.split("|")

    if group_by_origins:
        distances = {o: {d: None for d in destinations} for o in origins}
    else:
        distances = {d: {o: None for o in origins} for d in destinations}

    for row in range(len(r["rows"])):
        for col in range(2):
            info = r["rows"][row]["elements"][col]
            info = {k: info[k] for k in ["distance", "duration"]}

            if group_by_origins:
                distances[origins[row]][destinations[col]] = info
            else:
                distances[destinations[col]][origins[row]] = info

    return distances


def find_nearby_airports(latitude, longitude):
    """
    Find the nearby airports of a given coordinate.
    :param latitude: float: latitude of the location of interest
    :param longitude: float: longitude of the location of interest
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
        "limit": 20,
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
            "airline": flight["airlines"],
            "routes": flight["routes"],
        }

    return flights


def main():
    r = make_distance_matrix_request("37.6737957,-122.0795195", "Boston,MA|Charlestown,MA", group_by_origins=False)
    print(r)

    # find_nearby_airports(latitude=37.6737957, longitude=-122.0795195)
    # search_flights(origin="SFO", destination="LAX", date_from="14/03/2019", date_to="14/03/2019")


if __name__ == "__main__":
    main()
