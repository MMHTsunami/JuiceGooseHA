"""Config flow for Juice Goose IP-series controllers."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .api import (
    JuiceGooseApi,
    JuiceGooseApiError,
    JuiceGooseAuthError,
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
            username = user_input.get(CONF_USERNAME, "").strip()
            password = user_input.get(CONF_PASSWORD, "")
            try:
                await self._async_validate_input(
                    self.hass, host, port, username or None, password
                )
            except JuiceGooseInvalidResponseError:
                errors["base"] = "invalid_response"
            except JuiceGooseAuthError:
                errors["base"] = "invalid_auth"
            except (JuiceGooseApiError, ValueError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host.lower()}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Juice Goose ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): vol.All(str, vol.Length(min=1)),
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Optional(CONF_USERNAME, default=""): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Optional(CONF_PASSWORD, default=""): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    async def _async_validate_input(
        hass: HomeAssistant,
        host: str,
        port: int,
        username: str | None = None,
        password: str = "",
    ) -> None:
        """Verify the host serves a valid controller status document."""
        api = JuiceGooseApi(
            host, port, async_get_clientsession(hass), username, password
        )
        await api.async_get_status()

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> JuiceGooseOptionsFlow:
        """Create a flow for updating controller credentials."""
        return JuiceGooseOptionsFlow(config_entry)


class JuiceGooseOptionsFlow(config_entries.OptionsFlow):
    """Update HTTP credentials for an existing controller entry."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Store the config entry being updated."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Validate and save optional HTTP Basic Auth credentials."""
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]
            try:
                await JuiceGooseConfigFlow._async_validate_input(
                    self.hass,
                    self._config_entry.data[CONF_HOST],
                    self._config_entry.data[CONF_PORT],
                    username or None,
                    password,
                )
            except JuiceGooseInvalidResponseError:
                errors["base"] = "invalid_response"
            except JuiceGooseAuthError:
                errors["base"] = "invalid_auth"
            except (JuiceGooseApiError, ValueError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="",
                    data={CONF_USERNAME: username, CONF_PASSWORD: password},
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=self._config_entry.options.get(
                        CONF_USERNAME,
                        self._config_entry.data.get(CONF_USERNAME, ""),
                    ),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(
                    CONF_PASSWORD,
                    default=self._config_entry.options.get(
                        CONF_PASSWORD,
                        self._config_entry.data.get(CONF_PASSWORD, ""),
                    ),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="init", data_schema=schema, errors=errors
        )