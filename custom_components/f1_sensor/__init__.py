import logging
from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed
)

from .const import DOMAIN, PLATFORMS, API_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration via config flow."""
    coordinator = F1DataCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Nytt sätt att ladda flera plattformar asynkront utan for-loop och async_add_job:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Avregistrera entiteter och rensa data."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class F1DataCoordinator(DataUpdateCoordinator):
    """Samordnare för att hämta och uppdatera F1-data."""

    def __init__(self, hass: HomeAssistant):
        """Initiera koordinatorn."""
        super().__init__(
            hass,
            _LOGGER,
            name="F1 Data Coordinator",
            update_interval=timedelta(hours=6),
        )
        self._session = aiohttp.ClientSession()

    async def _async_update_data(self):
        """Hämta data från jolpica-F1-API."""
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(API_URL) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"Fel vid hämtning av F1-data: {response.status}")
                    return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Fel vid hämtning: {err}") from err