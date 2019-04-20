import structlog

from trip_planner_api.air_travel import get_all_air_travel_options
from trip_planner_api.ground_travel import get_all_ground_travel_options
from trip_planner_api.options_analysis import add_equivalent_travel_cost

structlog.configure(logger_factory=structlog.PrintLoggerFactory())
logger = structlog.get_logger(processors=[structlog.processors.JSONRenderer()])


def analyze_travel_option(trip_params, traveler_params):
    """
    Get all of the travel options and order them based on the traveler's preferences
    :param trip_params: dict: parameters relating to the trip itself
        origin_lat: float: latitude of the origin
        origin_lon: float: longitude of the origin
        destination_lat: float: latitude of the destination
        destination_lon: float: longitude of the destination
        travel_date: string ("dd/mm/yyyy"): departure date
    :param traveler_params: dict: parameters relating to the traveler's cost and utility functions
        value_one_hour: int: value in dollars of 1 hour of time
        value_ten_hours: int: value in dollars of 10 hours of time
    :return: pandas.DataFrame: each row is a travel option, and each column is some information about the travel option.
        Ordered by a best guess of the traveler's preferences.
    """
    logger.info("finding all travel options")
    air_travel_options = get_all_air_travel_options(
        origin_lat=trip_params["origin_lat"],
        origin_lon=trip_params["origin_lon"],
        destination_lat=trip_params["destination_lat"],
        destination_lon=trip_params["destination_lon"],
        travel_date=trip_params["travel_date"],
    )
    ground_travel_options = get_all_ground_travel_options(
        origin_lat=trip_params["origin_lat"],
        origin_lon=trip_params["origin_lon"],
        destination_lat=trip_params["destination_lat"],
        destination_lon=trip_params["destination_lon"],
        travel_date=trip_params["travel_date"],
    )
    all_travel_options = air_travel_options.append(ground_travel_options, ignore_index=True, sort=False)

    logger.info("analyze the travel options and ordering by preference")
    all_travel_options = add_equivalent_travel_cost(
        travel_options=all_travel_options,
        value_one_hour=traveler_params["value_one_hour"],
        value_ten_hours=traveler_params["value_ten_hours"],
    )
    ordered_travel_options = all_travel_options.sort_values(by=["equivalent_travel_cost"])
    ordered_travel_options = ordered_travel_options.reset_index(drop=True)
    ordered_travel_options["rank"] = ordered_travel_options.index

    return ordered_travel_options


def main():
    """ Command line entry point for local testing """
    create_new_fixture = True

    logger.info("CLI invocation")
    trip_params = {
        "origin_lat": 37.6737957,
        "origin_lon": -122.0795195,
        "destination_lat": 34.0932502,
        "destination_lon": -118.1165166,
        "travel_date": "01/06/2019",
    }
    traveler_params = {
        "value_one_hour": 20,
        "value_ten_hours": 150,
    }

    ordered_travel_options = analyze_travel_option(trip_params, traveler_params)

    if create_new_fixture:
        ordered_travel_options.to_json("trip_planner_api/fixtures/travel_options.json", orient="records")
    else:
        print(ordered_travel_options)


if __name__ == "__main__":
    main()
