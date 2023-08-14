"""Platform for HyCube sensor integration."""
import logging

from homeassistant.components.sensor import SensorEntity
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
    entries.append(HycubeSensor(api, coordinator, device, 'wallbox1.connection', 'Connected', None, None))
    entries.append(HycubeSensor(api, coordinator, device, 'wallbox1.p', 'Power', POWER_WATT, 1))
    device = "Wallbox 2"
    entries.append(HycubeSensor(api, coordinator, device, 'wallbox2.connection', 'Connected', None, None))
    entries.append(HycubeSensor(api, coordinator, device, 'wallbox2.p', 'Power', POWER_WATT, 1))
    device = "Wallbox 3"
    entries.append(HycubeSensor(api, coordinator, device, 'wallbox3.connection', 'Connected', None, None))
    entries.append(HycubeSensor(api, coordinator, device, 'wallbox3.p', 'Power', POWER_WATT, 1))

    # Grid Meter
    device = "Grid"
    entries.append(HycubeSensor(api, coordinator, device, 'grid.f', 'Frequency', FREQUENCY_HERTZ, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'grid.p', 'Power', POWER_WATT, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'grid.u1', 'Voltage (L1)', ELECTRIC_POTENTIAL_VOLT, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'grid.u2', 'Voltage (L2)', ELECTRIC_POTENTIAL_VOLT, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'grid.u3', 'Voltage (L3)', ELECTRIC_POTENTIAL_VOLT, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'grid.i1', 'Current (L1)', ELECTRIC_CURRENT_AMPERE, 2))
    entries.append(HycubeSensor(api, coordinator, device, 'grid.i2', 'Current (L2)', ELECTRIC_CURRENT_AMPERE, 2))
    entries.append(HycubeSensor(api, coordinator, device, 'grid.i3', 'Current (L3)', ELECTRIC_CURRENT_AMPERE, 2))


    # Home Meter
    device = "Home"
    entries.append(HycubeSensor(api, coordinator, device, 'home.p', 'Power', POWER_WATT, 1))

    # Solar Meter
    device = "Solar"
    entries.append(HycubeSensor(api, coordinator, device, 'solar.p', 'Power', POWER_WATT, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'solar.p1', 'Power (String 1)', POWER_WATT, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'solar.p2', 'Power (String 2)', POWER_WATT, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'solar.i1', 'Current (String 1)', ELECTRIC_CURRENT_AMPERE, 2))
    entries.append(HycubeSensor(api, coordinator, device, 'solar.i2', 'Current (String 2)', ELECTRIC_CURRENT_AMPERE, 2))
    entries.append(HycubeSensor(api, coordinator, device, 'solar.u1', 'Voltage (String 1)', ELECTRIC_POTENTIAL_VOLT, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'solar.u2', 'Voltage (String 2)', ELECTRIC_POTENTIAL_VOLT, 1))

    # Battery
    device = "Battery"
    entries.append(HycubeSensor(api, coordinator, device, 'battery.soc', 'State of Charge', PERCENTAGE, 0))
    entries.append(HycubeSensor(api, coordinator, device, 'battery.p', 'Power', POWER_WATT, 1))
    entries.append(HycubeSensor(api, coordinator, device, 'battery.u', 'Voltage', ELECTRIC_POTENTIAL_VOLT, 2))
    entries.append(HycubeSensor(api, coordinator, device, 'battery.i', 'Current', ELECTRIC_CURRENT_AMPERE, 2))
    entries.append(HycubeSensor(api, coordinator, device, 'battery.t', 'Temperature', TEMP_CELSIUS, 1))

    async_add_entities(entries, update_before_add=True)


class HycubeSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, api: Hycube, coordinator, device: str, api_str: str, name: str, unit: str, suggested_precision: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._state = None
        self._api = api
        self._api_str = api_str

        self._attr_suggested_display_precision = suggested_precision

        self._attr_name = device + " " + name
        self._attr_native_unit_of_measurement = unit

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

        self._attr_sensor_state = state
        self._state = state

        self.async_write_ha_state()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    # @property
    # def extra_state_attributes(self):
    #     if self.name == "Solar Power":
    #         attrs = {
    #             "String 1": self._api.solar.p1,
    #             "String 2": self._api.solar.p2,
    #         }

    #         return attrs
    #     else:
    #         return super().extra_state_attributes
