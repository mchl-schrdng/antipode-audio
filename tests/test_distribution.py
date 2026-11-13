import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile


SPEC = importlib.util.spec_from_file_location("build_plugin", Path(__file__).resolve().parents[1] / "scripts/build_plugin.py")
packaging = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packaging)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in packaging.FILES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8")
        (self.root / "pyproject.toml").write_text('[project]\nversion = "0.1.1"\n', encoding="utf-8")
        for name in ("plugin.json", ".claude-plugin/plugin.json", "integrations/antigravity.plugin.json"):
            manifest = {"name": "antipode", "version": "0.1.1"}
            if name == "integrations/antigravity.plugin.json":
                manifest["displayName"] = "Antipode"
            (self.root / name).write_text(json.dumps(manifest), encoding="utf-8")
        (self.root / "secret.env").write_text("PRIVATE_TEST_TOKEN=never-include", encoding="utf-8")
        (self.root / "site").mkdir()
        (self.root / "site/private.txt").write_text("private frontend", encoding="utf-8")
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True, capture_output=True)

    def test_reproducible_allowlist_and_native_manifest(self):
        first = packaging.build(self.root, self.root / "first")
        for name in packaging.FILES:
            os.utime(self.root / name, (1700000000, 1700000000))
        second = packaging.build(self.root, self.root / "second")
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(first["sha256"], hashlib.sha256(Path(first["archive"]).read_bytes()).hexdigest())
        with zipfile.ZipFile(first["archive"]) as archive:
            self.assertEqual(archive.namelist(), sorted(packaging.FILES))
            self.assertNotIn("secret.env", archive.namelist())
            self.assertNotIn("site/private.txt", archive.namelist())
            self.assertNotIn("displayName", json.loads(archive.read("plugin.json")))
            self.assertEqual((archive.getinfo("scripts/client_config.py").external_attr >> 16) & 0o777, 0o755)
        native = packaging.build(self.root, self.root / "native", "antigravity")
        with zipfile.ZipFile(native["archive"]) as archive:
            self.assertEqual(json.loads(archive.read("plugin.json"))["displayName"], "Antipode")
            self.assertEqual(archive.read("plugin.json"), archive.read("integrations/antigravity.plugin.json"))
            self.assertNotIn("mcp.json", archive.namelist())
            self.assertIn("mcp_config.json", archive.namelist())

    def test_untracked_required_file_and_version_mismatch_are_rejected(self):
        subprocess.run(["git", "rm", "--cached", "--quiet", "--", "uv.lock"], cwd=self.root, check=True)
        with self.assertRaisesRegex(ValueError, "not Git-tracked"):
            packaging.build(self.root, self.root / "dist")
        subprocess.run(["git", "add", "uv.lock"], cwd=self.root, check=True)
        (self.root / "plugin.json").write_text('{"name":"antipode","version":"0.1.0"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs"):
            packaging.build(self.root, self.root / "dist")

    def test_symlinked_file_is_rejected(self):
        path = self.root / "NOTICE"
        path.unlink()
        try:
            path.symlink_to(self.root / "secret.env")
        except OSError:
            self.skipTest("Creating symlinks is unavailable on this platform")
        with self.assertRaisesRegex(ValueError, "Symlinks"):
            packaging.build(self.root, self.root / "dist")


if __name__ == "__main__":
    unittest.main()
