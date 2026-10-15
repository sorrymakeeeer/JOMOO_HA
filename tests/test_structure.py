"""Basic structural consistency checks for the HA custom component."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]

class IntegrationStructureTest(unittest.TestCase):
    def test_manifest_domain(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["domain"], "jomoo_ha")
        self.assertTrue(manifest["config_flow"])
        self.assertIn("bluetooth", manifest["dependencies"])

    def test_domain_constant(self):
        from ast import parse, Assign, Constant
        tree = parse((ROOT / "const.py").read_text(encoding="utf-8"))
        values = [n.value.value for n in tree.body if isinstance(n, Assign) and any(getattr(t, 'id', '') == 'DOMAIN' for t in n.targets) and isinstance(n.value, Constant)]
        self.assertEqual(values, ["jomoo_ha"])

    def test_config_flow_domain_binding(self):
        content = (ROOT / "config_flow.py").read_text(encoding="utf-8")
        self.assertIn("domain=DOMAIN", content)
        self.assertIn("from .const import CONF_ADDRESS, DOMAIN", content)

    def test_no_old_domain_in_source(self):
        old_domain = 'jomoo_' + 'sq9650'
        for item in ROOT.rglob("*"):
            if item.is_file() and item.suffix in ('.py', '.json', '.md'):
                self.assertNotIn(old_domain, item.read_text(encoding="utf-8"), str(item))
