"""Run with `python -m unittest discover -s tests -v`."""
import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).parents[1] / 'protocol.py'
spec = importlib.util.spec_from_file_location('protocol', path)
protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol)


class ProtocolTest(unittest.TestCase):
    def test_night_light_on_frame(self):
        self.assertEqual(protocol.NIGHT_LIGHT_ON.hex(' ').upper(), 'FC 43 01 00 00 00 41 00 01 FC')

    def test_query_frame(self):
        self.assertEqual(protocol.STATE_QUERY.hex(' ').upper(), 'FC 12 01 00 00 00 11 00 FC')

    def test_reject_bad_checksum(self):
        data = bytearray([0xFC, 0x00, 1,0,0,0,0x30] + [0]*18 + [0xFC])
        self.assertIsNone(protocol.parse_state_report(bytes(data)))

    def test_parse_synthetic_state(self):
        content = bytearray([1,0,0,0,0x30] + [0]*18)
        content[5+4] |= (1 << 3)
        content[5+9] |= (1 << 6)
        content[5+10] |= (3 << 3)
        frame = bytes([0xFC, sum(content)&0xff]) + bytes(content) + bytes([0xFC])
        state = protocol.parse_state_report(frame)
        self.assertIsNotNone(state)
        self.assertTrue(state['night_light'])
        self.assertTrue(state['foot_sensor'])
        self.assertEqual(state['seat_temp_level_raw'], 3)


if __name__ == '__main__':
    unittest.main()
