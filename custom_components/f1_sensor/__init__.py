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
BASE_URL = "https://api.jolpi.ca/ergast/f1/current/{round}/qualifying.json"

async def find_latest_valid_qualifying_round_upwards(start_round: int, max_round: int = 24):
    latest_valid_round = None
    async with aiohttp.ClientSession() as session:
        for round_num in range(start_round, max_round + 1):
            url = BASE_URL.format(round=round_num)
            try:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        break
                    data = await resp.json()
                    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
                    if races:
                        _LOGGER.debug("Geldige qualifying data gevonden voor round %s", round_num)
                        latest_valid_round = round_num
                    else:
                        break
            except Exception as e:
                _LOGGER.warning("Fout bij ophalen qualifying data voor round %s: %s", round_num, e)
                break
    return latest_valid_round


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
