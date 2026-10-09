"""Juice Goose IP-series Home Assistant integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import JuiceGooseApi
from .const import PLATFORMS
from .coordinator import JuiceGooseCoordinator


@dataclass
class JuiceGooseRuntimeData:
    """Objects shared by the integration's platforms."""

    api: JuiceGooseApi
    coordinator: JuiceGooseCoordinator


JuiceGooseConfigEntry: TypeAlias = ConfigEntry[JuiceGooseRuntimeData]


async def async_setup_entry(
    hass: HomeAssistant, entry: JuiceGooseConfigEntry
) -> bool:
    """Set up a configured controller and its platforms."""
    api = JuiceGooseApi(
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        async_get_clientsession(hass),
        entry.options.get(
            CONF_USERNAME, entry.data.get(CONF_USERNAME, "")
        )
        or None,
        entry.options.get(
            CONF_PASSWORD, entry.data.get(CONF_PASSWORD, "")
        ),
    )
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    coordinator = JuiceGooseCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = JuiceGooseRuntimeData(api, coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: JuiceGooseConfigEntry
) -> bool:
    """Unload integration platforms."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant, entry: JuiceGooseConfigEntry
) -> None:
    """Reload the entry after its authentication options change."""
    await hass.config_entries.async_reload(entry.entry_id)