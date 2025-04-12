from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
import datetime

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Skapa sensorer när integrationen läggs till."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Hämta användarens val av sensornamn från config_flow.
    base_name = entry.data.get("sensor_name", "F1")

    sensors = [
        F1NextRaceSensor(coordinator, f"{base_name}_next_race"),
        F1CurrentSeasonSensor(coordinator, f"{base_name}_current_season"),
    ]
    async_add_entities(sensors, True)


class F1NextRaceSensor(CoordinatorEntity, SensorEntity):
    """En sensor som visar och exponerar data för nästa kommande race."""

    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:flag-checkered"  # Ikon för nästa race

    def _get_next_race(self):
        """Returnera dict för nästa kommande race eller None om inga fler race."""
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
        """Bygger ISO8601-sträng av datum och tid (eller None)."""
        if not date_str:
            return None
        if not time_str:
            time_str = "00:00:00Z"
        dt_str = f"{date_str}T{time_str}".replace("Z", "+00:00")
        try:
            dt = datetime.datetime.fromisoformat(dt_str)
            return dt.isoformat()  # ex: 2025-03-22T07:00:00+00:00
        except ValueError:
            return None

    @property
    def state(self):
        """
        Returnera racets start-tid som ISO8601-string.
        Ex: 2025-04-13T15:00:00+00:00
        """
        next_race = self._get_next_race()
        if not next_race:
            return None
        return self.combine_date_time(next_race.get("date"), next_race.get("time"))

    @property
    def extra_state_attributes(self):
        """Returnera alla relevanta attribut för nästa race."""
        race = self._get_next_race()
        if not race:
            return {}

        circuit = race.get("Circuit", {})
        location = circuit.get("Location", {})

        # Sessioner
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

            # Tider som ISO8601
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
    En sensor som visar info om hela säsongens race.
    State = antal race i säsongen
    Attribut = en lista med all data (Races), plus ev. annan metadata.
    """

    def __init__(self, coordinator, sensor_name):
        super().__init__(coordinator)
        self._attr_name = sensor_name
        self._attr_unique_id = f"{sensor_name}_unique"
        self._attr_icon = "mdi:calendar-month"  # Ikon för säsong-sensorn

    @property
    def state(self):
        """Returnera antal race i säsongen."""
        data = self.coordinator.data
        if not data:
            return None

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        return len(races)

    @property
    def extra_state_attributes(self):
        """Returnera hela racelistan och ev. annan info som attribut."""
        data = self.coordinator.data
        if not data:
            return {}

        mrdata = data.get("MRData", {})
        race_table = mrdata.get("RaceTable", {})
        races = race_table.get("Races", [])

        return {
            "season": race_table.get("season"),
            "races": races,  # Här är en lista med hela säsongens race
        }