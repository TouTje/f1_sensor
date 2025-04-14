import logging
from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    PLATFORMS,
    API_URL,
    DRIVER_STANDINGS_URL,
    CONSTRUCTOR_STANDINGS_URL
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration via config flow."""

    # Koordinator för "Current Season"
    race_coordinator = F1DataCoordinator(
        hass,
        API_URL,
        "F1 Race Data Coordinator"
    )

    # Koordinator för "Driver Standings"
    driver_coordinator = F1DataCoordinator(
        hass,
        DRIVER_STANDINGS_URL,
        "F1 Driver Standings Coordinator"
    )

    # Koordinator för "Constructor Standings" – krävs för constructor-sensorn
    constructor_coordinator = F1DataCoordinator(
        hass,
        CONSTRUCTOR_STANDINGS_URL,
        "F1 Constructor Standings Coordinator"
    )

    # Första initiala anrop
    await race_coordinator.async_config_entry_first_refresh()
    await driver_coordinator.async_config_entry_first_refresh()
    await constructor_coordinator.async_config_entry_first_refresh()

    # Spara i hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "race_coordinator": race_coordinator,
        "driver_coordinator": driver_coordinator,
        "constructor_coordinator": constructor_coordinator,  # Viktigt
    }

    # Ladda sensor.py (och ev. andra plattformar)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Rensa när integrationen tas bort."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class F1DataCoordinator(DataUpdateCoordinator):
    """Hanterar uppdateringar från en given F1-endpoint."""

    def __init__(self, hass: HomeAssistant, url: str, name: str):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(hours=6)
        )
        self._session = aiohttp.ClientSession()
        self._url = url

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(self._url) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Fel vid hämtning: {response.status}")
                    return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Fel vid hämtning: {err}") from err