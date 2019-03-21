# trip-planner-api

## Local Testing
1. Open up terminal and navigate to the root directory of `trip-planner-api`
2. $ pipenv shell
3. $ gunicorn --reload trip_planner_api.app
4. Open up another terminal
- Health check: $ http localhost:8000/health
- Get travel options: $ http localhost:8000/travel origin_lat==37.6737957 origin_lon==-122.0795195
destination_lat==34.0932502 destination_lon==-118.1165166 travel_date==01/06/2019 value_one_hour==20
value_ten_hours==150
