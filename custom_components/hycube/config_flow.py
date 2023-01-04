from datetime import timedelta
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_HOST

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = timedelta(seconds=10)
MIN_UPDATE_INTERVAL = timedelta(seconds=5)

class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
	"""Example config flow."""
	async def async_step_user(self, info):
		if info is not None:
			_LOGGER.debug(info)
			return self.async_create_entry(title=info[CONF_HOST], data=info)

		return self.async_show_form(
			step_id="user", data_schema=vol.Schema(
				{
					vol.Required(CONF_NAME): str,
					vol.Required(CONF_HOST): str,
				}
			)
		)
