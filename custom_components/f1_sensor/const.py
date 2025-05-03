# custom_components/f1_sensor/const.py

DOMAIN = "f1_sensor"
PLATFORMS = ["sensor"]

API_URL = "https://api.jolpi.ca/ergast/f1/current.json"
DRIVER_STANDINGS_URL = "https://api.jolpi.ca/ergast/f1/current/driverstandings.json"
CONSTRUCTOR_STANDINGS_URL = "https://api.jolpi.ca/ergast/f1/current/constructorstandings.json"
LAST_RACE_RESULTS_URL = "https://api.jolpi.ca/ergast/f1/current/last/results.json"
SEASON_RESULTS_URL = "https://api.jolpi.ca/ergast/f1/current/results.json?limit=100"

# --- Tillagd rad för kvalsensor ---
LAST_QUALIFYING_URL = "https://api.jolpi.ca/ergast/f1/current/last/qualifying.json"