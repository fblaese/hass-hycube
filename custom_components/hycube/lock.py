"""Platform for HyCube sensor integration."""
import logging

from homeassistant.components.lock import LockEntity
from homeassistant.core import ( HomeAssistant, callback )
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from functools import partial

from .pyhycube import Hycube
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    _LOGGER.debug("async_setup_entry")

    entries = []
    api: Hycube
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Wallbox
    device = "Wallbox 1"
    entries.append(HycubeLock(api, coordinator, device, 'wallbox1.lock', api.wallbox1.setLock, 'Charging Lock'))
    device = "Wallbox 2"
    entries.append(HycubeLock(api, coordinator, device, 'wallbox2.lock', api.wallbox2.setLock, 'Charging Lock'))
    device = "Wallbox 3"
    entries.append(HycubeLock(api, coordinator, device, 'wallbox3.lock', api.wallbox3.setLock, 'Charging Lock'))

    async_add_entities(entries)


class HycubeLock(CoordinatorEntity, LockEntity):

    def __init__(self, api: Hycube, coordinator: DataUpdateCoordinator, device: str, api_str: str, api_lock: callable, name: str) -> None:
        super().__init__(coordinator)
        self._state = None
        self._api = api
        self._api_str = api_str
        self._api_lock = api_lock
        self.coordinator = coordinator

        self._attr_name = device + " " + name

        self._attr_unique_id = device + "_" + name
        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, device)
            },
            "name": device,
            "manufacturer": 'Hycube',
        }

    @callback
    def _handle_coordinator_update(self):
        state = eval("self._api." + self._api_str)

        if state == 0 or state == 1:
            self._attr_is_locked = state
        else:
            self._attr_is_locked = None

        self.async_write_ha_state()
    
    async def async_lock(self, **kwargs):
        await self.hass.async_add_executor_job(partial(self._api_lock, value=1))
        await self.coordinator.async_refresh()

    async def async_unlock(self, **kwargs):
        await self.hass.async_add_executor_job(partial(self._api_lock, value=0))
        await self.coordinator.async_refresh()
