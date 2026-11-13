import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest
import wave

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
        cache_directory = subprocess.check_output([shutil.which("uv"), "cache", "dir"], text=True).strip()
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
                env = {key: substitute(value) for key, value in spec.get("env", {}).items()}
                if filename == "integrations/claude.mcp.json":
                    self.assertEqual(args[:2], ["run", "--locked"])
                    self.assertEqual(Path(args[2]), ROOT / "scripts/claude_mcp.py")
                    self.assertNotIn("env", spec)
                    env["UV_PYTHON"] = "3.12"
                else:
                    self.assertEqual(args[args.index("--python") + 1], "3.12")
                    # Exercise the CI matrix interpreter; the cold test checks automatic selection.
                    args[args.index("--python") + 1] = sys.executable
                    self.assertTrue(Path(env["UV_PROJECT_ENVIRONMENT"]).is_relative_to(directory))
                env["UV_OFFLINE"] = "1"
                # MCP filters inherited variables; reuse the cache populated by installation.
                env["UV_CACHE_DIR"] = cache_directory
                if "UV_PYTHON_INSTALL_DIR" in os.environ:
                    env["UV_PYTHON_INSTALL_DIR"] = os.environ["UV_PYTHON_INSTALL_DIR"]
                self.assertNotIn("--offline", args)
                self.assertIn("--locked", args)
                async with asyncio.timeout(60), Client(StdioServerParameters(command=shutil.which("uv"), args=args, env=env)) as client:
                    rendered = await client.call_tool("generate_sound", {"output": "connected.wav", "duration": 0.02})
                    self.assertFalse(rendered.is_error, rendered.content)
                    self.assertTrue((Path(directory) / "audio/connected.wav").is_file())


    @unittest.skipUnless(os.environ.get("ANTIPODE_TEST_COLD_INSTALL") == "1", "opt-in test downloads a fresh Python and dependencies")
    async def test_cold_install_from_read_only_source_then_restart_offline(self):
        for filename in ("mcp.json", "integrations/claude.mcp.json"):
            with self.subTest(manifest=filename), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                source = base / "plugin with spaces"
                source.mkdir()
                for required in ("pyproject.toml", "uv.lock", ".python-version", "README.md", "LICENSE", "NOTICE"):
                    shutil.copyfile(ROOT / required, source / required)
                shutil.copytree(ROOT / "src", source / "src", ignore=shutil.ignore_patterns("__pycache__"))
                (source / "scripts").mkdir()
                for name in ("claude_mcp.py", "claude_mcp.py.lock"):
                    shutil.copyfile(ROOT / "scripts" / name, source / "scripts" / name)
                original_files = {str(path.relative_to(source)) for path in source.rglob("*")}
                for path in source.rglob("*"):
                    path.chmod(0o555 if path.is_dir() else 0o444)
                source.chmod(0o555)
                try:
                    spec = json.loads((ROOT / filename).read_text())["mcpServers"]["antipode"]
                    data = base / "data"
                    args = [value.replace("${PLUGIN_ROOT}", str(source)).replace("${CLAUDE_PLUGIN_ROOT}", str(source)) for value in spec["args"]]
                    args[-1] = str(base / "audio")
                    env = {
                        "UV_CACHE_DIR": str(base / "empty-cache"),
                        "UV_PYTHON_INSTALL_DIR": str(base / "empty-python"),
                        "UV_PYTHON_PREFERENCE": "only-managed",
                    }
                    if filename == "mcp.json":
                        env["UV_PROJECT_ENVIRONMENT"] = str(data / "venv")
                    self.assertFalse(Path(env["UV_CACHE_DIR"]).exists())
                    self.assertFalse(Path(env["UV_PYTHON_INSTALL_DIR"]).exists())
                    for mode in ("cold", "offline"):
                        started = time.monotonic()
                        if mode == "offline":
                            env["UV_OFFLINE"] = "1"
                            env["UV_PYTHON_DOWNLOADS"] = "never"
                        async with asyncio.timeout(180), Client(StdioServerParameters(command=shutil.which("uv"), args=args, env=env)) as client:
                            print(f"{filename} {mode} MCP connection: {time.monotonic() - started:.2f}s", flush=True)
                            tools = await client.list_tools()
                            self.assertEqual(len(tools.tools), 5)
                            rendered = await client.call_tool("generate_sound", {"output": mode + ".wav", "duration": 0.1})
                            self.assertFalse(rendered.is_error, rendered.content)
                        with wave.open(str(base / "audio" / (mode + ".wav"))) as audio:
                            self.assertEqual(audio.getnframes(), 4800)
                            self.assertEqual(audio.getframerate(), 48000)
                    self.assertFalse((source / ".venv").exists())
                    self.assertEqual(original_files, {str(path.relative_to(source)) for path in source.rglob("*")})
                    self.assertTrue(any(Path(env["UV_PYTHON_INSTALL_DIR"]).iterdir()))
                finally:
                    source.chmod(0o755)
                    for path in source.rglob("*"):
                        path.chmod(0o755 if path.is_dir() else 0o644)

if __name__ == "__main__":
    unittest.main()
