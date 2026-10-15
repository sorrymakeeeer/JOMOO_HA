"""JOMOO SQ9650 experimental Home Assistant integration."""

from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .ble_client import SQ9650Client
from .const import CONF_ADDRESS, DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.BUTTON, Platform.SENSOR, Platform.SWITCH]


class SQ9650Coordinator(DataUpdateCoordinator[dict]):
    """Retain explicitly queried state without pretending it is live."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        super().__init__(hass, _LOGGER, name="九牧 SQ9650")
        self.address = address
        self.client = SQ9650Client(hass, address)
        self.last_received: datetime | None = None

    async def async_query(self) -> None:
        state = await self.client.query()
        self.last_received = dt_util.utcnow()
        self.async_set_updated_data(state)

    async def async_set_light(self, enabled: bool) -> None:
        state = await self.client.set_night_light(enabled)
        self.last_received = dt_util.utcnow()
        self.async_set_updated_data(state)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if bluetooth.async_scanner_count(hass, connectable=True) == 0:
        raise ConfigEntryNotReady("没有可主动连接的蓝牙适配器；请先检查蓝牙集成")
    coordinator = SQ9650Coordinator(hass, entry.data[CONF_ADDRESS])
    # No initial connection/poll; start with unknown values until queried.
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
