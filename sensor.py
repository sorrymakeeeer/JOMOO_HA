"""Read-only raw seat heat level (mapping intentionally not assumed)."""

from homeassistant.components.sensor import SensorEntity

from .entity import SQ9650Entity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([SeatLevelSensor(entry.runtime_data)])


class SeatLevelSensor(SQ9650Entity, SensorEntity):
    _attr_name = "座温档位（上次查询）"
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "seat_level_raw")

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("seat_temp_level_raw")

    @property
    def extra_state_attributes(self):
        return {"last_ble_status_at": self.coordinator.last_received.isoformat() if self.coordinator.last_received else None,
                "note": "原始档位值，尚未建立 0-4 与界面温度文案的实机映射"}
