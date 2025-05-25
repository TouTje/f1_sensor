import logging
from datetime import datetime, timezone, timedelta
import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    PLATFORMS,
    API_URL,
    DRIVER_STANDINGS_URL,
    CONSTRUCTOR_STANDINGS_URL,
    LAST_RACE_RESULTS_URL,
    SEASON_RESULTS_URL,
)

_LOGGER = logging.getLogger(__name__)

class F1DataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url, name):
        self.url = url
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"API error {resp.status}")
                return await resp.json()

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration via config flow."""
    race_coordinator = F1DataCoordinator(hass, API_URL, "F1 Race Data Coordinator")
    driver_coordinator = F1DataCoordinator(hass, DRIVER_STANDINGS_URL, "F1 Driver Standings Coordinator")
    constructor_coordinator = F1DataCoordinator(hass, CONSTRUCTOR_STANDINGS_URL, "F1 Constructor Standings Coordinator")
    last_race_coordinator = F1DataCoordinator(hass, LAST_RACE_RESULTS_URL, "F1 Last Race Results Coordinator")
    season_results_coordinator = F1DataCoordinator(hass, SEASON_RESULTS_URL, "F1 Season Results Coordinator")

    await race_coordinator.async_config_entry_first_refresh()
    await driver_coordinator.async_config_entry_first_refresh()
    await constructor_coordinator.async_config_entry_first_refresh()
    await last_race_coordinator.async_config_entry_first_refresh()
    await season_results_coordinator.async_config_entry_first_refresh()

    # ─── Dynamisch URL bepalen voor kwalificatie ──────────────────────────────
    races = race_coordinator.data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    now = datetime.now(timezone.utc)

    past_race = None
    for race in races:
        date = race.get("date")
        time = race.get("time", "00:00:00Z")
        dt_str = f"{date}T{time}".replace("Z", "+00:00")
        try:
            race_dt = datetime.fromisoformat(dt_str)
        except ValueError:
            continue
        if race_dt > now:
            break
        past_race = race

    weekday = now.weekday()  # 0 = maandag, ..., 6 = zondag
    _LOGGER.debug("Huidige weekday (UTC): %s", weekday)

    if weekday >= 3:
        # Vanaf donderdag: gebruik huidige race (deze week)
        target_round = int(past_race.get("round", "0")) if past_race else 1
    else:
        # Tot woensdag: gebruik vorige race
        target_round = int(past_race.get("round", "0")) - 1 if past_race else 1

    qualifying_url = f"https://api.jolpi.ca/ergast/f1/current/{target_round}/qualifying.json"
    _LOGGER.debug("F1 Qualifying URL: %s", qualifying_url)

    last_qualifying_coordinator = F1DataCoordinator(
        hass, qualifying_url, "F1 Last Qualifying Results Coordinator"
    )
    await last_qualifying_coordinator.async_config_entry_first_refresh()

    # ─── Registreren van coordinators ─────────────────────────────────────────
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "race_coordinator": race_coordinator,
        "driver_coordinator": driver_coordinator,
        "constructor_coordinator": constructor_coordinator,
        "last_race_coordinator": last_race_coordinator,
        "last_qualifying_coordinator": last_qualifying_coordinator,
        "season_results_coordinator": season_results_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class F1DataCoordinator(DataUpdateCoordinator):
    """Handles updates from a given F1 endpoint."""

    def __init__(self, hass: HomeAssistant, url: str, name: str):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(hours=1),
        )
        self._session = aiohttp.ClientSession()
        self._url = url

    async def _async_update_data(self):
        """Fetch data from the F1 API."""
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(self._url) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Error fetching data: {response.status}")
                    return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
