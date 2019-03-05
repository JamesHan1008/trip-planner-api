import os
import requests

RESOURCE_DISTANCE_MATRIX = "distancematrix"
RESPONSE_FORMAT = "json"


def make_distance_matrix_request():
    url = "{route}/{resource}/{format}".format(
        route=os.getenv("GOOGLE_MAPS_API_ROUTE"),
        resource=RESOURCE_DISTANCE_MATRIX,
        format=RESPONSE_FORMAT,
    )
    params = {
        "key": os.getenv("GOOGLE_MAPS_API_KEY"),
        "origins": "Boston,MA",
        "destinations": "Charlestown,MA",
    }
    r = requests.get(url=url, params=params)
    print(r.url)
    print(r.json())


def main():
    make_distance_matrix_request()


if __name__ == "__main__":
    main()
