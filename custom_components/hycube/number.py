"""Platform for HyCube sensor integration."""
import logging

from homeassistant.components.number import NumberEntity
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
    entries.append(HycubeNumber(api, coordinator, device, 'wallbox1.minChargingPower', api.wallbox1.setMinChargingPower, 'wallbox1.phaseCount', 'Min. Charging Power'))
    device = "Wallbox 2"
    entries.append(HycubeNumber(api, coordinator, device, 'wallbox2.minChargingPower', api.wallbox2.setMinChargingPower, 'wallbox2.phaseCount', 'Min. Charging Power'))
    device = "Wallbox 3"
    entries.append(HycubeNumber(api, coordinator, device, 'wallbox3.minChargingPower', api.wallbox3.setMinChargingPower, 'wallbox3.phaseCount', 'Min. Charging Power'))

    async_add_entities(entries, update_before_add=True)


class HycubeNumber(CoordinatorEntity, NumberEntity):

    def __init__(self, api: Hycube, coordinator: DataUpdateCoordinator, device: str, api_str: str, api_set: callable, api_phaseCount: str, name: str) -> None:
        super().__init__(coordinator)
        self._api = api
        self._api_str = api_str
        self._api_set = api_set
        self._api_phase_count = api_phaseCount
        self.coordinator = coordinator

        self._attr_name = device + " " + name

        self._attr_native_step = 69
        self._attr_native_min_value = 4140
        self._attr_native_max_value = 11040

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
        self._attr_native_value = eval("self._api." + self._api_str)

        # FIXME: hardcoded min/max values :-(
        self._attr_native_step = int(eval("self._api." + self._api_phase_count) * 230 * 0.1)
        self._attr_native_min_value = eval("self._api." + self._api_phase_count) * 230 * 6
        self._attr_native_max_value = eval("self._api." + self._api_phase_count) * 230 * 16

        self.async_write_ha_state()

    async def async_set_native_value(self, value: int):
        await self.hass.async_add_executor_job(partial(self._api_set, value=value))
        await self.coordinator.async_refresh()
