from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
import datetime

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Skapa sensorer när integrationen läggs till."""
    data_dict = hass.data[DOMAIN][entry.entry_id]

    # Koordinatorer från __init__.py
    race_coordinator = data_dict["race_coordinator"]
    driver_coordinator = data_dict["driver_coordinator"]
    constructor_coordinator = data_dict["constructor_coordinator"]

    base_name = entry.data.get("sensor_name", "F1")

    # Skapa redan befintliga sensorer
    sensors = [
        F1NextRaceSensor(race_coordinator, f"{base_name}_next_race"),
        F1CurrentSeasonSensor(race_coordinator, f"{base_name}_current_season"),
        F1DriverStandingsSensor(driver_coordinator, f"{base_name}_driver_standings"),

        # Ny sensor för konstruktörsställning
        F1ConstructorStandingsSensor(constructor_coordinator, f"{base_name}_constructor_standings"),
    ]

    async_add_entities(sensors, True)


class F1NextRaceSensor(CoordinatorEntity, SensorEntity):
    """Sensor som returnerar datum/tid (ISO8601) för nästa race i 'state'."""

    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:flag-checkered"  # valfri ikon

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
        """Visa start-tiden för nästa race (ISO8601) i state."""
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
    """
    Sensor som visar info om hela säsongen.
    - state = antal race
    - attribut = säsong, race-lista osv
    """

    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:calendar-month"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        return len(races)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}

        mrdata = data.get("MRData", {})
        race_table = mrdata.get("RaceTable", {})
        races = race_table.get("Races", [])

        return {
            "season": race_table.get("season"),
            "races": races,
        }


class F1DriverStandingsSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor för att exponera Driver Standings.
    - state = antal förare
    - attribut = driver_standings (lista), season, round
    """

    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:account-multiple-check"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None

        standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        if not standings_lists:
            return 0

        driver_standings = standings_lists[0].get("DriverStandings", [])
        return len(driver_standings)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}

        standings_table = data.get("MRData", {}).get("StandingsTable", {})
        standings_lists = standings_table.get("StandingsLists", [])

        if not standings_lists:
            return {}

        first_list = standings_lists[0]
        driver_standings = first_list.get("DriverStandings", [])

        return {
            "season": first_list.get("season"),
            "round": first_list.get("round"),
            "driver_standings": driver_standings,
        }


class F1ConstructorStandingsSensor(CoordinatorEntity, SensorEntity):
    """
    Ny sensor för att exponera Constructor Standings.
    - state = antal constructors
    - attribut = constructor_standings (lista), season, round
    """

    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:factory"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None

        standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        if not standings_lists:
            return 0

        constructor_standings = standings_lists[0].get("ConstructorStandings", [])
        return len(constructor_standings)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}

        standings_table = data.get("MRData", {}).get("StandingsTable", {})
        standings_lists = standings_table.get("StandingsLists", [])

        if not standings_lists:
            return {}

        first_list = standings_lists[0]
        constructor_standings = first_list.get("ConstructorStandings", [])

        return {
            "season": first_list.get("season"),
            "round": first_list.get("round"),
            "constructor_standings": constructor_standings,
        }