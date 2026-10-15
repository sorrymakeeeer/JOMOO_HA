"""Explicit on-demand state query button."""

from homeassistant.components.button import ButtonEntity

from .entity import SQ9650Entity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([QueryButton(entry.runtime_data)])


class QueryButton(SQ9650Entity, ButtonEntity):
    _attr_name = "查询状态"
    _attr_icon = "mdi:bluetooth-connect"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "query")

    async def async_press(self) -> None:
        await self.coordinator.async_query()
