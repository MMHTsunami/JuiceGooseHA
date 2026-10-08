"""Sequence controls for Juice Goose controllers."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import JuiceGooseRuntimeData
from .api import JuiceGooseApiError
from .const import (
    DEFAULT_SEQUENCE_DELAY_SECONDS,
    DOMAIN,
    SEQUENCE_DOWN,
    SEQUENCE_UP,
)
from .coordinator import JuiceGooseCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[JuiceGooseRuntimeData],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UP and DOWN sequence buttons."""
    coordinator = entry.runtime_data.coordinator
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
        manufacturer="Juice Goose",
        model="IP 15-15",
        name=f"Juice Goose ({entry.data['host']})",
    )
    async_add_entities(
        [
            JuiceGooseSequenceButton(
                coordinator,
                entry.entry_id,
                device_info,
                SEQUENCE_UP,
                "Start UP sequence",
                "mdi:chevron-up",
            ),
            JuiceGooseSequenceButton(
                coordinator,
                entry.entry_id,
                device_info,
                SEQUENCE_DOWN,
                "Start DOWN sequence",
                "mdi:chevron-down",
            ),
        ]
    )


class JuiceGooseSequenceButton(
    CoordinatorEntity[JuiceGooseCoordinator], ButtonEntity
):
    """Start a controller sequence with the configured default delay."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: JuiceGooseCoordinator,
        entry_id: str,
        device_info: DeviceInfo,
        sequence: int,
        name: str,
        icon: str,
    ) -> None:
        """Initialize a sequence button."""
        super().__init__(coordinator)
        self._sequence = sequence
        self._attr_name = name
        self._attr_icon = icon
        direction = "up" if sequence == SEQUENCE_UP else "down"
        self._attr_unique_id = f"{entry_id}_sequence_{direction}"
        self._attr_device_info = device_info

    async def async_press(self) -> None:
        """Start the selected sequence and refresh the controller state."""
        try:
            await self.coordinator.api.async_start_sequence(
                self._sequence, DEFAULT_SEQUENCE_DELAY_SECONDS
            )
            await self.coordinator.async_request_refresh()
        except JuiceGooseApiError as err:
            raise HomeAssistantError("Unable to start Juice Goose sequence") from err
