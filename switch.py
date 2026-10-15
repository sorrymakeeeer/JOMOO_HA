"""First tested actuator is night light only (no mechanical movement)."""

from homeassistant.components.switch import SwitchEntity

from .entity import SQ9650Entity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([NightLightSwitch(entry.runtime_data)])


class NightLightSwitch(SQ9650Entity, SwitchEntity):
    _attr_name = "夜灯（上次查询）"
    _attr_icon = "mdi:lightbulb-night"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "night_light")

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("night_light")

    @property
    def extra_state_attributes(self):
        return {"last_ble_status_at": self.coordinator.last_received.isoformat() if self.coordinator.last_received else None,
                "note": "仅表示上次成功查询结果，不保证实时同步"}

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_light(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_light(False)
