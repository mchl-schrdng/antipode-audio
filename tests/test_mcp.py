import asyncio
from pathlib import Path
import sys
import tempfile
import unittest
import wave

from mcp import Client
from mcp.client.stdio import StdioServerParameters


class McpTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_stdio_in_modern_and_legacy_modes(self):
        for mode in ("auto", "legacy"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                parameters = StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "antipode.mcp_server", "--workspace", directory],
                )
                async with asyncio.timeout(30), Client(parameters, mode=mode) as client:
                    catalog = await client.list_tools()
                    names = {tool.name for tool in catalog.tools}
                    self.assertEqual(names, {"list_presets", "generate_sound", "render_recipe", "process_audio", "analyze_audio"})
                    presets = await client.call_tool("list_presets", {})
                    self.assertFalse(presets.is_error)
                    self.assertIn("tone", presets.structured_content)
                    generated = await client.call_tool("generate_sound", {"output": "mcp.wav", "duration": 0.1})
                    self.assertFalse(generated.is_error, generated.content)
                    self.assertEqual(generated.structured_content["frames"], 4800)
                    with wave.open(str(Path(directory) / "mcp.wav")) as wav:
                        self.assertEqual(wav.getnframes(), 4800)
                    original = (Path(directory) / "mcp.wav").read_bytes()
                    for invalid in (
                        {"output": "mcp.wav"},
                        {"output": "../escape.wav"},
                        {"output": "invalid.wav", "duration": -1},
                        {"output": "unknown.wav", "preset": "not-a-preset"},
                    ):
                        failure = await client.call_tool("generate_sound", invalid)
                        self.assertTrue(failure.is_error, failure)
                    self.assertEqual((Path(directory) / "mcp.wav").read_bytes(), original)
                    rendered = await client.call_tool("render_recipe", {
                        "output": "layered.wav",
                        "recipe": {"duration": 0.3, "layers": [{"preset": "tone", "duration": 0.1}]},
                    })
                    self.assertFalse(rendered.is_error, rendered.content)
                    self.assertEqual(rendered.structured_content["channels"], 2)
                    analyzed = await client.call_tool("analyze_audio", {"source": "layered.wav"})
                    self.assertFalse(analyzed.is_error)
                    self.assertEqual(analyzed.structured_content["full_scale_samples"], 0)
                    process = await client.call_tool("process_audio", {"source": "mcp.wav", "output": "reversed.wav", "reverse": True})
                    self.assertFalse(process.is_error, process.content)
                    for tool in catalog.tools:
                        self.assertTrue(tool.annotations.title)
                        self.assertFalse(tool.annotations.destructive_hint)
                        self.assertFalse(tool.annotations.open_world_hint)
                        self.assertEqual(tool.annotations.read_only_hint, tool.name in {"list_presets", "analyze_audio"})


if __name__ == "__main__":
    unittest.main()
