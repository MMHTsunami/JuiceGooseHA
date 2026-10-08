"""POD switches for Juice Goose controllers."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import JuiceGooseRuntimeData
from .api import JuiceGooseApiError
from .const import DOMAIN, POD_NAMES
from .coordinator import JuiceGooseCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[JuiceGooseRuntimeData],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the three documented POD switches."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        JuiceGoosePodSwitch(entry, coordinator, pod) for pod in POD_NAMES
    )


class JuiceGoosePodSwitch(
    CoordinatorEntity[JuiceGooseCoordinator], SwitchEntity
):
    """Control a single power outlet division (POD)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry[JuiceGooseRuntimeData],
        coordinator: JuiceGooseCoordinator,
        pod: int,
    ) -> None:
        """Initialize a POD switch."""
        super().__init__(coordinator)
        self._pod = pod
        self._attr_name = POD_NAMES[pod]
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_pod_{pod}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            manufacturer="Juice Goose",
            model="IP 15-15",
            name=f"Juice Goose ({entry.data['host']})",
        )

    @property
    def is_on(self) -> bool:
        """Return the latest reported state of this POD."""
        data = self.coordinator.data
        return bool(data and data["pods"][self._pod])

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn this POD on and refresh the reported state."""
        await self._async_set_pod(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn this POD off and refresh the reported state."""
        await self._async_set_pod(False)

    async def _async_set_pod(self, is_on: bool) -> None:
        """Send a state command and refresh coordinator data."""
        try:
            await self.coordinator.api.async_set_pod(self._pod, is_on)
            await self.coordinator.async_request_refresh()
        except JuiceGooseApiError as err:
            raise HomeAssistantError(
                f"Unable to control Juice Goose POD {self._pod}"
            ) from err
