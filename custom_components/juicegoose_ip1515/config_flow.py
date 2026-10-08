"""Config flow for Juice Goose IP-series controllers."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    JuiceGooseApi,
    JuiceGooseApiError,
    JuiceGooseInvalidResponseError,
)
from .const import DEFAULT_PORT, DOMAIN


class JuiceGooseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up a Juice Goose controller through the UI."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Accept a host and port, then validate the device status endpoint."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            try:
                await self._async_validate_input(self.hass, host, port)
            except JuiceGooseInvalidResponseError:
                errors["base"] = "invalid_response"
            except (JuiceGooseApiError, ValueError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host.lower()}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Juice Goose ({host})",
                    data={CONF_HOST: host, CONF_PORT: port},
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): vol.All(str, vol.Length(min=1)),
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    async def _async_validate_input(
        hass: HomeAssistant, host: str, port: int
    ) -> None:
        """Verify the host serves a valid controller status document."""
        api = JuiceGooseApi(host, port, async_get_clientsession(hass))
        await api.async_get_status()