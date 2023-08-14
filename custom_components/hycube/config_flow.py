from datetime import timedelta
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = timedelta(seconds=10)
MIN_UPDATE_INTERVAL = timedelta(seconds=5)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
	"""config flow"""
	async def async_step_user(self, info):
		if info is not None:
			_LOGGER.debug(info)
			return self.async_create_entry(title=info[CONF_NAME], data=info)

		return self.async_show_form(
			step_id="user", data_schema=vol.Schema(
				{
					vol.Required(CONF_NAME): str,
					vol.Required(CONF_HOST): str,
					vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
				}
			)
		)

	@staticmethod
	@callback
	def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
		"""Get the options flow for this handler."""
		return HycubeOptionsFlowHandler(config_entry)

class HycubeOptionsFlowHandler(config_entries.OptionsFlow):
	"option flow"

	def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
		"""Initialize options flow."""
		self.config_entry = config_entry

	async def async_step_init(self, info) -> FlowResult:
		"""Handle options flow."""
		if info is not None:
			return self.async_create_entry(title="", data=info)

		data_schema = vol.Schema(
			{
				vol.Optional(
					CONF_SCAN_INTERVAL,
					default=self.config_entry.options.get(
						CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
					),
				): cv.positive_int
			}
		)
		return self.async_show_form(step_id="init", data_schema=vol.Schema(
				{
					vol.Optional(CONF_SCAN_INTERVAL, default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): cv.positive_int,
				}
			)
		)
