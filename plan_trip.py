import structlog

from air_travel import get_all_air_travel_options

structlog.configure(logger_factory=structlog.PrintLoggerFactory())
logger = structlog.get_logger(processors=[structlog.processors.JSONRenderer()])


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
