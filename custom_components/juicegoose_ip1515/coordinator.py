"""Polling coordinator for Juice Goose controller state."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import JuiceGooseApi, JuiceGooseApiError, JuiceGooseStatus
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class JuiceGooseCoordinator(DataUpdateCoordinator[JuiceGooseStatus]):
    """Fetch device state on a regular interval."""

    def __init__(self, hass: HomeAssistant, api: JuiceGooseApi) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> JuiceGooseStatus:
        """Retrieve the latest controller state."""
        try:
            return await self.api.async_get_status()
        except JuiceGooseApiError as err:
            raise UpdateFailed("Unable to retrieve Juice Goose status") from err