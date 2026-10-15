"""Minimal, independent implementation of the SQ9650 BLE frame format.

Protocol facts are based on JMGatt_client (caokang1997); no C code copied.
Hardware behavior must be verified on the user's own device.
"""

from __future__ import annotations


def encode_frame(command: int, *arguments: int) -> bytes:
    """Build the FC/SUM/01.../FC frame (1 or 2 command arguments)."""
    if len(arguments) not in (1, 2):
        raise ValueError("Expected one or two command arguments")
    if not all(0 <= v <= 255 for v in (command, *arguments)):
        raise ValueError("Each command value must be a byte")
    content = bytes((0x01, 0x00, 0x00, 0x00, command, *arguments))
    return bytes((0xFC, sum(content) & 0xFF)) + content + bytes((0xFC,))


STATE_QUERY = encode_frame(0x11, 0)
NIGHT_LIGHT_ON = encode_frame(0x41, 0, 1)
NIGHT_LIGHT_OFF = encode_frame(0x41, 0, 0)


def parse_state_report(frame: bytes) -> dict | None:
    """Decode state notification (0x30). Ignore invalid or unrelated replies."""
    if (
        len(frame) < 26
        or frame[0] != 0xFC
        or frame[-1] != 0xFC
        or frame[6] != 0x30
        or (sum(frame[2:-1]) & 0xFF) != frame[1]
    ):
        return None
    t = frame[7:-1]
    return {
        "work_state": t[0] & 0x1F,
        "error_bits": (t[1], t[2], t[3]),
        "foot_sensor": bool(t[4] & (1 << 3)),
        "cover_open": bool(t[4] & (1 << 4)),
        "ring_open": bool(t[4] & (1 << 5)),
        "occupied": bool(t[4] & (1 << 7)),
        "night_light": bool(t[9] & (1 << 6)),
        "seat_temp_level_raw": (t[10] >> 3) & 0x07,
    }
