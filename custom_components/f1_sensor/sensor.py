# custom_components/f1_sensor/sensor.py

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import async_timeout
import datetime

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Create sensors when the integration is added."""
    data = hass.data[DOMAIN][entry.entry_id]
    base = entry.data.get("sensor_name", "F1")
    enabled = entry.data.get("enabled_sensors", [])

    mapping = {
        "next_race": (F1NextRaceSensor, data["race_coordinator"]),
        "current_season": (F1CurrentSeasonSensor, data["race_coordinator"]),
        "driver_standings": (F1DriverStandingsSensor, data["driver_coordinator"]),
        "constructor_standings": (F1ConstructorStandingsSensor, data["constructor_coordinator"]),
        "weather": (F1WeatherSensor, data["race_coordinator"]),
        "last_race_results": (F1LastRaceSensor, data["last_race_coordinator"]),
        "season_results": (F1SeasonResultsSensor, data["season_results_coordinator"]),
    }

    sensors = []
    for key in enabled:
        cls, coord = mapping.get(key, (None, None))
        if cls and coord:
            sensors.append(cls(coord, f"{base}_{key}"))
    async_add_entities(sensors, True)


class F1NextRaceSensor(CoordinatorEntity, SensorEntity):
    """Sensor that returns date/time (ISO8601) for the next race in 'state'."""

    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:flag-checkered"  # optional icon
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    def _get_next_race(self):
        data = self.coordinator.data
        if not data:
            return None

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        now = datetime.datetime.now(datetime.timezone.utc)

        for race in races:
            race_date_str = race.get("date")
            race_time_str = race.get("time") or "00:00:00Z"
            dt_str = f"{race_date_str}T{race_time_str}".replace("Z", "+00:00")
            try:
                race_dt = datetime.datetime.fromisoformat(dt_str)
            except ValueError:
                continue

            if race_dt > now:
                return race

        return None

    def combine_date_time(self, date_str, time_str):
        if not date_str:
            return None
        if not time_str:
            time_str = "00:00:00Z"
        dt_str = f"{date_str}T{time_str}".replace("Z", "+00:00")
        try:
            dt = datetime.datetime.fromisoformat(dt_str)
            return dt.isoformat()
        except ValueError:
            return None

    @property
    def state(self):
        """Show the start time for the next race (ISO8601) in state."""
        next_race = self._get_next_race()
        if not next_race:
            return None
        return self.combine_date_time(next_race.get("date"), next_race.get("time"))

    @property
    def extra_state_attributes(self):
        race = self._get_next_race()
        if not race:
            return {}

        circuit = race.get("Circuit", {})
        location = circuit.get("Location", {})

        first_practice = race.get("FirstPractice", {})
        second_practice = race.get("SecondPractice", {})
        third_practice = race.get("ThirdPractice", {})
        qualifying = race.get("Qualifying", {})
        sprint_qualifying = race.get("SprintQualifying", {})
        sprint = race.get("Sprint", {})

        return {
            "season": race.get("season"),
            "round": race.get("round"),
            "race_name": race.get("raceName"),
            "race_url": race.get("url"),

            "circuit_id": circuit.get("circuitId"),
            "circuit_name": circuit.get("circuitName"),
            "circuit_url": circuit.get("url"),
            "circuit_lat": location.get("lat"),
            "circuit_long": location.get("long"),
            "circuit_locality": location.get("locality"),
            "circuit_country": location.get("country"),

            "race_start": self.combine_date_time(race.get("date"), race.get("time")),
            "first_practice_start": self.combine_date_time(first_practice.get("date"), first_practice.get("time")),
            "second_practice_start": self.combine_date_time(second_practice.get("date"), second_practice.get("time")),
            "third_practice_start": self.combine_date_time(third_practice.get("date"), third_practice.get("time")),
            "qualifying_start": self.combine_date_time(qualifying.get("date"), qualifying.get("time")),
            "sprint_qualifying_start": self.combine_date_time(sprint_qualifying.get("date"), sprint_qualifying.get("time")),
            "sprint_start": self.combine_date_time(sprint.get("date"), sprint.get("time")),
        }


class F1CurrentSeasonSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing number of races this season."""
    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:calendar-month"

    @property
    def state(self):
        data = self.coordinator.data or {}
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        return len(races)

    @property
    def extra_state_attributes(self):
        table = (self.coordinator.data or {}).get("MRData", {}).get("RaceTable", {})
        return {
            "season": table.get("season"),
            "races": table.get("Races", [])
        }


class F1DriverStandingsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for driver standings."""
    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:account-multiple-check"

    @property
    def state(self):
        lists = (self.coordinator.data or {}).get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        return len(lists[0].get("DriverStandings", [])) if lists else 0

    @property
    def extra_state_attributes(self):
        lists = (self.coordinator.data or {}).get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        if not lists:
            return {}
        first = lists[0]
        return {
            "season": first.get("season"),
            "round": first.get("round"),
            "driver_standings": first.get("DriverStandings", [])
        }


class F1ConstructorStandingsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for constructor standings."""
    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:factory"

    @property
    def state(self):
        lists = (self.coordinator.data or {}).get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        return len(lists[0].get("ConstructorStandings", [])) if lists else 0

    @property
    def extra_state_attributes(self):
        lists = (self.coordinator.data or {}).get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        if not lists:
            return {}
        first = lists[0]
        return {
            "season": first.get("season"),
            "round": first.get("round"),
            "constructor_standings": first.get("ConstructorStandings", [])
        }


class F1WeatherSensor(CoordinatorEntity, SensorEntity):
    """Sensor for current and race-start weather."""
    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:weather-partly-cloudy"
        self._current = {}
        self._race = {}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        removal = self.coordinator.async_add_listener(lambda: self.hass.async_create_task(self._update_weather()))
        self.async_on_remove(removal)
        await self._update_weather()

    async def _update_weather(self):
        race = F1NextRaceSensor(self.coordinator, "")._get_next_race()
        loc = race.get("Circuit", {}).get("Location", {}) if race else {}
        lat, lon = loc.get("lat"), loc.get("long")
        if lat is None or lon is None:
            return
        session = async_get_clientsession(self.hass)
        url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
        headers = {"User-Agent": "homeassistant-f1_sensor"}
        try:
            async with async_timeout.timeout(10):
                resp = await session.get(url, headers=headers)
                data = await resp.json()
        except Exception:
            return
        times = data.get("properties", {}).get("timeseries", [])
        if not times:
            return
        curr = times[0].get("data", {}).get("instant", {}).get("details", {})
        self._current = self._extract(curr)
        start_iso = F1NextRaceSensor(self.coordinator, "").combine_date_time(race.get("date"), race.get("time")) if race else None
        self._race = {k: None for k in self._current}
        if start_iso:
            start_dt = datetime.datetime.fromisoformat(start_iso)
            same_day = [t for t in times if datetime.datetime.fromisoformat(t["time"]).date() == start_dt.date()]
        if same_day:
            closest = min(same_day, key=lambda t: abs(datetime.datetime.fromisoformat(t["time"]) - start_dt))
            data_entry = closest.get("data", {})
            instant_details = data_entry.get("instant", {}).get("details", {})
            precip_1h = data_entry.get("next_1_hours", {}).get("details", {}).get("precipitation_amount", 0)
            rd = dict(instant_details)
            rd["precipitation_amount"] = precip_1h
            self._race = self._extract(rd)
        self.async_write_ha_state()

    def _extract(self, d):
        wd = d.get("wind_from_direction")
        return {
            "temperature": d.get("air_temperature"),
            "temperature_unit": "celsius",
            "humidity": d.get("relative_humidity"),
            "humidity_unit": "%",
            "cloud_cover": d.get("cloud_area_fraction"),
            "cloud_cover_unit": "%",
            "precipitation": d.get("precipitation_amount", 0),
            "precipitation_unit": "mm",
            "wind_speed": d.get("wind_speed"),
            "wind_speed_unit": "m/s",
            "wind_direction": self._abbr(wd),
            "wind_from_direction_degrees": wd,
            "wind_from_direction_unit": "degrees"
        }

    def _abbr(self, deg):
        if deg is None:
            return None
        dirs = [(i*22.5, d) for i, d in enumerate([
            "N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW","N"
        ])]
        return min(dirs, key=lambda x: abs(deg - x[0]))[1]

    @property
    def state(self):
        return self._current.get("temperature")

    @property
    def extra_state_attributes(self):
        attrs = {f"current_{k}": v for k, v in self._current.items()}
        attrs.update({f"race_{k}": v for k, v in self._race.items()})
        return attrs


class F1LastRaceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for results of the latest race."""
    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:trophy"

    @property
    def state(self):
        races = self.coordinator.data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            return None
        results = races[0].get("Results", [])
        winner = next((r for r in results if r.get("positionText") == "1"), None)
        return winner.get("Driver", {}).get("familyName") if winner else None

    @property
    def extra_state_attributes(self):
        races = self.coordinator.data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            return {}
        race = races[0]
        # Helper to filter result entries
        def _clean_result(r):
            return {
                "number": r.get("number"),
                "position": r.get("position"),
                "points": r.get("points"),
                "status": r.get("status"),
                "driver": {
                    "permanentNumber": r.get("Driver", {}).get("permanentNumber"),
                    "code": r.get("Driver", {}).get("code"),
                    "givenName": r.get("Driver", {}).get("givenName"),
                    "familyName": r.get("Driver", {}).get("familyName"),
                },
                "constructor": {
                    "constructorId": r.get("Constructor", {}).get("constructorId"),
                    "name": r.get("Constructor", {}).get("name"),
                }
            }
        cleaned = [_clean_result(r) for r in race.get("Results", [])]
        return {
            "round": race.get("round"),
            "race_name": race.get("raceName"),
            "results": cleaned
        }


class F1SeasonResultsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for entire season's results."""
    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:podium"

    @property
    def state(self):
        races = self.coordinator.data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        return len(races)

    @property
    def extra_state_attributes(self):
        races_raw = self.coordinator.data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        # Helper to filter result entries
        def _clean_result(r):
            return {
                "number": r.get("number"),
                "position": r.get("position"),
                "points": r.get("points"),
                "status": r.get("status"),
                "driver": {
                    "permanentNumber": r.get("Driver", {}).get("permanentNumber"),
                    "code": r.get("Driver", {}).get("code"),
                    "givenName": r.get("Driver", {}).get("givenName"),
                    "familyName": r.get("Driver", {}).get("familyName"),
                },
                "constructor": {
                    "constructorId": r.get("Constructor", {}).get("constructorId"),
                    "name": r.get("Constructor", {}).get("name"),
                }
            }
        cleaned_races = []
        for race in races_raw:
            cleaned_results = [_clean_result(r) for r in race.get("Results", [])]
            cleaned_races.append({
                "round": race.get("round"),
                "race_name": race.get("raceName"),
                "results": cleaned_results
            })
        return {"races": cleaned_races}
