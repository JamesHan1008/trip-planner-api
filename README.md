# trip-planner-api

## Local Testing
1. Open up Terminal and navigate to the root directory of `trip-planner-api`
2. $ pipenv shell
3. $ gunicorn --reload trip_planner_api.app --timeout 180
- Leave at least 3 minutes to ensure the API does not timeout
- The hostname and port number will be shown on the Terminal (e.g. "Listening at: http://127.0.0.1:8000")
4. Open up another terminal and send API requests to the hostname and port number that this service is hosted at
- Health check: $ http http://127.0.0.1:8000/health
5. Clone or download trip-planner-ui, and run `npm start` to start up the UI on localhost

### Environment Variables
GOOGLE_MAPS_API_ROUTE=https://maps.googleapis.com/maps/api
GOOGLE_MAPS_API_KEY=*****************
GOOGLE_MAPS_API_EXPIRATION_DATE=2020/03/04

SKYPICKER_API_ROUTE=https://api.skypicker.com

MYGASFEED_API_ROUTE_DEV=http://devapi.mygasfeed.com/stations/radius
MYGASFEED_API_ROUTE_PROD=http://api.mygasfeed.com/stations/radius
MYGASFEED_API_KEY_DEV=rfej9napna

ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:3002"]
