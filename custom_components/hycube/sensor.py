"""Platform for HyCube sensor integration."""
import dataclasses
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .pyhycube import Hycube
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
hyc: Hycube

async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    _LOGGER.debug("async_setup_entry")

    entries = []

    entries.append(ExampleSensor('test1'))
    entries.append(ExampleSensor('test2'))
    entries.append(ExampleSensor('test3'))

    async_add_entities(entries)

class ExampleSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_unique_id: str
    _attr_device_info: dict

    def __init__(self, name) -> None:
        """Initialize the sensor."""
        self._state = None
        self._attr_unique_id = name
        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, name)
            },
            "name": name,
            "manufacturer": 'Hycube',
        }

        _LOGGER.debug(repr(self._attr_device_info))

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return 'Example Temperature'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = 23.0
