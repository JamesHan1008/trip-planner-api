import math

import structlog

structlog.configure(logger_factory=structlog.PrintLoggerFactory())
logger = structlog.get_logger(processors=[structlog.processors.JSONRenderer()])


def add_equivalent_travel_cost(travel_options, value_one_hour, value_ten_hours):
    """
    Calculate the dollar equivalent of the travel time, add that to the monetary travel cost, and store the results
    in a new column called `equivalent_travel_cost`
    :param travel_options: pandas.DataFrame: each row is a travel option
    :param value_one_hour:int: value in dollars of 1 hour of time
    :param value_ten_hours: int: value in dollars of 10 hours of time
    :return: pandas.DataFrame: travel_options with the new column `equivalent_travel_cost`
    """
    # Formula used:  Y = a(X^b), where X is the travel time in hours, and Y is the dollar equivalent value
    a = value_one_hour
    b = math.log(value_ten_hours / value_one_hour) / math.log(10)
    logger.info("Calculating dollar equivalent of travel time", formula="Y = a(X^b)", a=a, b=b)

    def calculate_equivalent_travel_cost(row):
        """ Calculate the equivalent travel cost for a single travel option """
        travel_time_hours = row.travel_time_seconds / 3600
        time_value = a * (travel_time_hours ** b)
        return row.total_cost + time_value

    travel_options["equivalent_travel_cost"] = travel_options.apply(calculate_equivalent_travel_cost, axis=1)

    return travel_options
