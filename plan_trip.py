import structlog

from air_travel import get_all_air_travel_options
from ground_travel import get_all_ground_travel_options

structlog.configure(logger_factory=structlog.PrintLoggerFactory())
logger = structlog.get_logger(processors=[structlog.processors.JSONRenderer()])


def main():
    air_travel_options = get_all_air_travel_options(
        origin_lat=37.6737957,
        origin_lon=-122.0795195,
        destination_lat=34.0932502,
        destination_lon=-118.1165166,
        travel_date="01/06/2019",
    )
    ground_travel_options = get_all_ground_travel_options(
        origin_lat=37.6737957,
        origin_lon=-122.0795195,
        destination_lat=34.0932502,
        destination_lon=-118.1165166,
        travel_date="01/06/2019",
    )

    all_travel_options = air_travel_options.append(ground_travel_options, ignore_index=True, sort=False)
    all_travel_options.to_csv("travel_options.csv")


if __name__ == "__main__":
    main()
