"""Binary status entities for Juice Goose controllers."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import JuiceGooseRuntimeData
from .const import DOMAIN
from .coordinator import JuiceGooseCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[JuiceGooseRuntimeData],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up connectivity, sequence, and manual override sensors."""
    coordinator = entry.runtime_data.coordinator
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
        manufacturer="Juice Goose",
        model="IP 15-15",
        name=f"Juice Goose ({entry.data['host']})",
    )
    async_add_entities(
        [
            JuiceGooseConnectionSensor(coordinator, entry.entry_id, device_info),
            JuiceGooseSequenceSensor(coordinator, entry.entry_id, device_info),
            JuiceGooseManualOverrideSensor(coordinator, entry.entry_id, device_info),
        ]
    )


class JuiceGooseConnectionSensor(
    CoordinatorEntity[JuiceGooseCoordinator], BinarySensorEntity
):
    """Report whether the latest controller poll succeeded."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_has_entity_name = True
    _attr_name = "Connection"

    def __init__(
        self,
        coordinator: JuiceGooseCoordinator,
        entry_id: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the connection sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_connection"
        self._attr_device_info = device_info

    @property
    def available(self) -> bool:
        """Keep the sensor available so a failed poll is reported as off."""
        return True

    @property
    def is_on(self) -> bool:
        """Return whether the latest coordinator update succeeded."""
        return self.coordinator.last_update_success


class JuiceGooseSequenceSensor(
    CoordinatorEntity[JuiceGooseCoordinator], BinarySensorEntity
):
    """Report whether the controller is currently running a sequence."""

    _attr_has_entity_name = True
    _attr_name = "Sequence running"

    def __init__(
        self,
        coordinator: JuiceGooseCoordinator,
        entry_id: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the sequence sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_sequence"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool:
        """Return the latest sequence state."""
        data = self.coordinator.data
        return bool(data and data["sequence_active"])


class JuiceGooseManualOverrideSensor(
    CoordinatorEntity[JuiceGooseCoordinator], BinarySensorEntity
):
    """Report the controller's manual override switch state."""

    _attr_has_entity_name = True
    _attr_name = "Manual override switch"

    def __init__(
        self,
        coordinator: JuiceGooseCoordinator,
        entry_id: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the manual override sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_manual_override"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool:
        """Return the latest manual override state."""
        data = self.coordinator.data
        return bool(data and data["manual_override"])
