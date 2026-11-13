import asyncio
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

from mcp import Client
from mcp.client.stdio import StdioServerParameters

ROOT = Path(__file__).resolve().parents[1]


class ConfigurationTests(unittest.TestCase):
    def test_codex_toml_preserves_non_bmp_unicode_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            copied_script = Path(directory) / "sound 🎵" / "scripts" / "client_config.py"
            copied_script.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "scripts/client_config.py", copied_script)
            result = subprocess.run(
                [sys.executable, str(copied_script), "codex", "--workspace", "audio 🎵"],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
            config = tomllib.loads(result.stdout)["mcp_servers"]["antipode"]
            self.assertIn("sound 🎵", config["command"])
            self.assertEqual(config["args"][-1], "audio 🎵")

    def test_generated_client_configs_launch_the_installed_interpreter(self):
        for client in ("codex", "claude", "antigravity", "opencode"):
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/client_config.py"), client, "--workspace", "audio with spaces"],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
            config = tomllib.loads(result.stdout) if client == "codex" else json.loads(result.stdout)
            if client == "codex":
                server = config["mcp_servers"]["antipode"]
                command = [server["command"], *server["args"]]
            elif client == "opencode":
                command = config["mcp"]["servers"]["antipode"]["command"]
                self.assertEqual(config["skills"], [str(ROOT / "skills")])
            else:
                server = config["mcpServers"]["antipode"]
                command = [server["command"], *server["args"]]
            self.assertTrue(Path(command[0]).is_file())
            self.assertEqual(command[-1], "audio with spaces")
            help_result = subprocess.run(command + ["--help"], capture_output=True, text=True, timeout=10)
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            self.assertIn("stdio", help_result.stdout)


class PluginLaunchTests(unittest.IsolatedAsyncioTestCase):
    @unittest.skipUnless(shutil.which("uv"), "uv is required to verify plugin launch commands")
    async def test_all_plugin_manifests_launch_offline_outside_the_plugin_root(self):
        for filename in ("mcp.json", "integrations/claude.mcp.json", "mcp_config.json"):
            with self.subTest(manifest=filename), tempfile.TemporaryDirectory() as directory:
                spec = json.loads((ROOT / filename).read_text())["mcpServers"]["antipode"]

                def substitute(value):
                    for prefix in ("PLUGIN", "CLAUDE_PLUGIN"):
                        value = value.replace("${" + prefix + "_ROOT}", str(ROOT))
                        value = value.replace("${" + prefix + "_DATA}", directory)
                    return value

                args = [substitute(value) for value in spec["args"]]
                args[-1] = str(Path(directory) / "audio")
                env = {key: substitute(value) for key, value in spec["env"].items()}
                env["UV_PYTHON"] = sys.executable
                self.assertIn("--offline", args)
                self.assertIn("--locked", args)
                self.assertTrue(Path(env["UV_PROJECT_ENVIRONMENT"]).is_relative_to(directory))
                async with asyncio.timeout(60), Client(StdioServerParameters(command=shutil.which("uv"), args=args, env=env)) as client:
                    rendered = await client.call_tool("generate_sound", {"output": "connected.wav", "duration": 0.02})
                    self.assertFalse(rendered.is_error, rendered.content)
                    self.assertTrue((Path(directory) / "audio/connected.wav").is_file())


if __name__ == "__main__":
    unittest.main()
