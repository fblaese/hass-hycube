"""HyCube integration"""

from datetime import timedelta
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
import homeassistant.core as core
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import CONF_NAME, CONF_HOST

from .pyhycube import Hycube

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

""" CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): vol.All(cv.string)
            }
        )
    }
)
"""

async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up Hycube platforms and services"""

    _LOGGER.debug("async_setup")

    return True

async def async_setup_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hycube entries"""

    _LOGGER.debug("async_setup_entry")
    _LOGGER.debug(repr(entry.data))

    name = entry.data[CONF_NAME]
    host = entry.data[CONF_HOST]

    api = Hycube(entry.data[CONF_HOST])
    coordinator = ApiCoordinator(hass, api)

    await coordinator.async_refresh()

    serial = api.serial
    model = api.type

    device_registry = dr.async_get(hass)

    device_registry.async_get_or_create(
        config_entry_id = entry.entry_id,
        #connections = {(dr.CONNECTION_NETWORK_MAC, config.mac)},
        identifiers = {(DOMAIN, serial)},
        manufacturer = "Hycube",
        name = name,
        model = model,
        #sw_version = config.swversion,
    )

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True

async def async_unload_entry(hass: core.HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug(f"Unloading '{entry.data[CONF_HOST]}")

    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    return True


class ApiCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: core, api: Hycube):
        super().__init__(hass, _LOGGER, name="test", update_interval=timedelta(seconds=10))
        self.api = api

    async def _async_update_data(self):
        return await self.hass.async_add_executor_job(self.api.requestStatus)
