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
                        {"output": "both.wav", "frequency": 440, "note": "A4"},
                        {"output": "low-note.wav", "note": "C0"},
                    ):
                        failure = await client.call_tool("generate_sound", invalid)
                        self.assertTrue(failure.is_error, failure)
                    self.assertEqual((Path(directory) / "mcp.wav").read_bytes(), original)
                    by_note = await client.call_tool("generate_sound", {"output": "note.wav", "preset": "tone", "duration": 0.2, "note": "A4"})
                    self.assertFalse(by_note.is_error, by_note.content)
                    self.assertAlmostEqual(by_note.structured_content["spectral_centroid_hz"], 440.0, delta=2.0)
                    rendered = await client.call_tool("render_recipe", {
                        "output": "layered.wav",
                        "recipe": {
                            "duration": 0.3,
                            "layers": [{
                                "preset": "tone", "duration": 0.2, "note": "A3", "note_end": "A4",
                                "pan": -0.5, "pan_end": 0.5, "lowpass_hz": 2000,
                            }],
                        },
                    })
                    self.assertFalse(rendered.is_error, rendered.content)
                    self.assertEqual(rendered.structured_content["channels"], 2)
                    family = {
                        "base": {"duration": 0.2, "layers": [{"material": "wood", "duration": 0.1,
                                 "automation": {"lowpass_hz": [[0, 500], [0.1, 6000]]}}]},
                        "members": {"tap": {}, "brush": {"events": [{"layer": 0, "gesture": "rub"}]}},
                    }
                    selected = await client.call_tool("render_recipe", {
                        "recipe": family, "member": "brush", "output": "brush.wav",
                    })
                    self.assertFalse(selected.is_error, selected.content)
                    self.assertEqual(selected.structured_content["member"], "brush")
                    self.assertEqual(selected.structured_content["frames"], 9600)
                    bad_glide = await client.call_tool("render_recipe", {
                        "output": "bad-glide.wav",
                        "recipe": {"duration": 0.3, "layers": [{"preset": "kick", "duration": 0.2, "note_end": "A2"}]},
                    })
                    self.assertTrue(bad_glide.is_error, bad_glide)
                    analyzed = await client.call_tool("analyze_audio", {"source": "layered.wav"})
                    self.assertFalse(analyzed.is_error)
                    self.assertEqual(analyzed.structured_content["full_scale_samples"], 0)
                    self.assertIsNotNone(analyzed.structured_content["peak_time_seconds"])
                    self.assertIsNotNone(analyzed.structured_content["spectral_centroid_hz"])
                    self.assertIsNotNone(analyzed.structured_content["stereo_balance"])
                    process = await client.call_tool(
                        "process_audio",
                        {"source": "mcp.wav", "output": "reversed.wav", "reverse": True, "lowpass_hz": 2000},
                    )
                    self.assertFalse(process.is_error, process.content)
                    for tool in catalog.tools:
                        self.assertTrue(tool.annotations.title)
                        self.assertFalse(tool.annotations.destructive_hint)
                        self.assertFalse(tool.annotations.open_world_hint)
                        self.assertEqual(tool.annotations.read_only_hint, tool.name in {"list_presets", "analyze_audio"})


if __name__ == "__main__":
    unittest.main()
