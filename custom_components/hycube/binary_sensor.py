"""Platform for HyCube sensor integration."""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import TEMP_CELSIUS, POWER_WATT, ELECTRIC_CURRENT_AMPERE, ELECTRIC_POTENTIAL_VOLT, PERCENTAGE, FREQUENCY_HERTZ
from homeassistant.core import ( HomeAssistant, callback )
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
    entries.append(HycubeBinarySensor(api, coordinator, device, 'wallbox1.carConnected', 'Car Connected'))
    entries.append(HycubeBinarySensor(api, coordinator, device, 'wallbox1.carChargingRequest', 'Car Charging Request'))
    device = "Wallbox 2"
    entries.append(HycubeBinarySensor(api, coordinator, device, 'wallbox2.carConnected', 'Car Connected'))
    entries.append(HycubeBinarySensor(api, coordinator, device, 'wallbox2.carChargingRequest', 'Car Charging Request'))
    device = "Wallbox 3"
    entries.append(HycubeBinarySensor(api, coordinator, device, 'wallbox3.carConnected', 'Car Connected'))
    entries.append(HycubeBinarySensor(api, coordinator, device, 'wallbox3.carChargingRequest', 'Car Charging Request'))

    async_add_entities(entries, update_before_add=True)


class HycubeBinarySensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, api: Hycube, coordinator, device: str, api_str: str, name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._state = None
        self._api = api
        self._api_str = api_str

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

        self._attr_is_on = state

        self.async_write_ha_state()
