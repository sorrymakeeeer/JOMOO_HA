"""On-demand local BLE client, using HA's shared Bluetooth device inventory."""

from __future__ import annotations

import asyncio
import logging

from bleak import BleakClient
from bleak.exc import BleakError
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import CHAR_UUID, SERVICE_UUID
from .protocol import NIGHT_LIGHT_OFF, NIGHT_LIGHT_ON, STATE_QUERY, parse_state_report

_LOGGER = logging.getLogger(__name__)


class SQ9650Client:
    """Connect only for a request; serialize BLE access to avoid contention."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        self.hass = hass
        self.address = address
        self._lock = asyncio.Lock()

    async def query(self) -> dict:
        return await self._communicate()

    async def set_night_light(self, enabled: bool) -> dict:
        return await self._communicate(
            NIGHT_LIGHT_ON if enabled else NIGHT_LIGHT_OFF,
            expected_light=enabled,
        )

    async def _communicate(
        self, command: bytes | None = None, expected_light: bool | None = None
    ) -> dict:
        async with self._lock:
            ble_device = bluetooth.async_ble_device_from_address(
                self.hass, self.address, connectable=True
            )
            if ble_device is None:
                raise HomeAssistantError(
                    "未发现 SQ9650 蓝牙广播；检查马桶距离、蓝牙适配器及设备地址，"
                    "等待扫描后再试。"
                )
            loop = asyncio.get_running_loop()
            reply: asyncio.Future[dict] = loop.create_future()

            def on_notify(_sender: object, data: bytearray) -> None:
                state = parse_state_report(bytes(data))
                if state is not None and not reply.done():
                    reply.set_result(state)

            try:
                async with BleakClient(ble_device, timeout=20) as conn:
                    # Reject devices lacking the expected GATT characteristic before writing.
                    if (
                        conn.services.get_service(SERVICE_UUID) is None
                        or conn.services.get_characteristic(CHAR_UUID) is None
                    ):
                        raise HomeAssistantError(
                            "设备没有提供 SQ9650 所需的 FFE0 / FFE1 服务特征；"
                            "请核对马桶的蓝牙地址。"
                        )
                    await conn.start_notify(CHAR_UUID, on_notify)
                    if command is not None:
                        await conn.write_gatt_char(CHAR_UUID, command, response=False)
                        # Let the device process the command before requesting status.
                        await asyncio.sleep(0.35)
                    await conn.write_gatt_char(CHAR_UUID, STATE_QUERY, response=False)
                    try:
                        state = await asyncio.wait_for(reply, timeout=5)
                    except TimeoutError as exc:
                        raise HomeAssistantError(
                            "已发送 BLE 指令，但没有收到有效状态回报，不能确认是否执行；"
                            "请现场核对，避免重复发送。"
                        ) from exc
                    finally:
                        await conn.stop_notify(CHAR_UUID)
            except HomeAssistantError:
                raise
            except (BleakError, asyncio.TimeoutError, OSError) as exc:
                _LOGGER.debug("BLE communication failed for %s: %s", self.address, exc)
                raise HomeAssistantError(
                    "SQ9650 蓝牙连接或通信失败；请检查是否正被官方微信小程序占用。"
                ) from exc

            if expected_light is not None and state["night_light"] != expected_light:
                raise HomeAssistantError(
                    "读取到的夜灯状态与请求不符，无法确认控制成功。"
                )
            return state
