import copy
import json
from pathlib import Path
import tempfile
import unittest
import wave

import numpy as np

from antipode.engine import AudioEngine


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.engine = AudioEngine(self.directory.name)
        self.recipe = {"duration": 0.4, "seed": 12, "layers": [
            {"preset": "tone", "start": 0.1, "duration": 0.2, "frequency": 440, "pan": -1}
        ]}

    def test_offsets_pan_peak_and_file_duration(self):
        result = self.engine.render_recipe(self.recipe, "left.wav")
        samples, rate = self.engine._read("left.wav")
        self.assertEqual(samples.shape, (19200, 2))
        self.assertTrue(np.all(samples[:4800] == 0))
        self.assertTrue(np.all(samples[14400:] == 0))
        self.assertTrue(np.all(samples[:, 1] == 0))
        self.assertGreater(np.max(np.abs(samples[:, 0])), 0.7)
        self.assertEqual(result["peak_dbfs"], -3)
        self.assertEqual(result["stereo_balance"], -1.0)
        self.assertEqual(result["full_scale_samples"], 0)

    def test_layer_notes_glides_pan_motion_and_filtering(self):
        moving = {
            "duration": 0.5,
            "layers": [{
                "preset": "tone", "duration": 0.4, "note": "A3", "note_end": "A5",
                "pan": -1, "pan_end": 1, "lowpass_hz": 2000,
            }],
        }
        report = self.engine.render_recipe(moving, "moving.wav")
        samples, rate = self.engine._read("moving.wav")
        active = samples[:19200]
        self.assertAlmostEqual(report["stereo_balance"], 0.0, delta=0.03)
        first_half = active[:len(active) // 2]
        second_half = active[len(active) // 2:]
        self.assertGreater(np.sum(first_half[:, 0] ** 2), np.sum(first_half[:, 1] ** 2) * 3)
        self.assertGreater(np.sum(second_half[:, 1] ** 2), np.sum(second_half[:, 0] ** 2) * 3)
        freqs = np.fft.rfftfreq(len(first_half), 1 / rate)
        early_power = np.sum(np.abs(np.fft.rfft(first_half, axis=0)) ** 2, axis=1)
        late_power = np.sum(np.abs(np.fft.rfft(second_half, axis=0)) ** 2, axis=1)
        early_hz = float(np.sum(freqs * early_power) / np.sum(early_power))
        late_hz = float(np.sum(freqs * late_power) / np.sum(late_power))
        self.assertAlmostEqual(early_hz, 318, delta=15)
        self.assertAlmostEqual(late_hz, 628, delta=15)
        midpoint_window = np.sum(active[9600 - 480:9600 + 480], axis=1)
        mid_freqs = np.fft.rfftfreq(len(midpoint_window), 1 / rate)
        mid_hz = mid_freqs[np.argmax(np.abs(np.fft.rfft(midpoint_window)))]
        self.assertAlmostEqual(mid_hz, 440, delta=30)
        raw_noise = self.engine.render_recipe({"duration": 0.2, "layers": [{"preset": "noise", "duration": 0.2}]}, "raw.wav")
        dark_noise = self.engine.render_recipe(
            {"duration": 0.2, "layers": [{"preset": "noise", "duration": 0.2, "lowpass_hz": 600}]}, "dark.wav"
        )
        self.assertLess(dark_noise["spectral_centroid_hz"], raw_noise["spectral_centroid_hz"] * 0.2)
        balanced = self.engine.render_recipe({
            "duration": 0.4,
            "layers": [
                {"preset": "tone", "duration": 0.4, "frequency": 440, "pan": -1, "level_db": -6},
                {"preset": "drone", "duration": 0.4, "frequency": 55, "highpass_hz": 200, "pan": 1, "level_db": -6},
            ],
        }, "balanced-filter.wav")
        balanced_samples, _ = self.engine._read("balanced-filter.wav")
        self.assertGreater(balanced["spectral_centroid_hz"], 200)
        self.assertAlmostEqual(
            float(np.max(np.abs(balanced_samples[:, 0]))),
            float(np.max(np.abs(balanced_samples[:, 1]))),
            delta=0.05,
        )

    def test_effects_are_deterministic_and_extend_sound_into_tail(self):
        self.recipe["effects"] = {"highpass_hz": 80, "lowpass_hz": 4000, "drive": 2,
                                  "delay_seconds": 0.05, "delay_feedback": 0.5, "delay_mix": 0.3,
                                  "reverb_seconds": 0.3, "reverb_mix": 0.3}
        original = copy.deepcopy(self.recipe)
        first = self.engine.render_recipe(self.recipe, "a.wav")
        second = self.engine.render_recipe(self.recipe, "b.wav")
        self.assertEqual(self.recipe, original)
        self.assertEqual(first["recipe_sha256"], second["recipe_sha256"])
        self.assertEqual((self.engine.workspace / "a.wav").read_bytes(), (self.engine.workspace / "b.wav").read_bytes())
        samples, _ = self.engine._read("a.wav")
        self.assertGreater(np.max(np.abs(samples[14400:-100])), 0.001)
        self.assertGreater(np.max(np.abs(samples[:, 1])), 0.001)
        self.assertTrue(np.all(samples[-1] == 0))

    def test_bad_recipes_are_rejected_before_any_file_is_written(self):
        bad_recipes = [None, {}, {**self.recipe, "url": "https://example.com/sample.wav"},
                       {**self.recipe, "duration": float("nan")}, {**self.recipe, "duration": 31},
                       {**self.recipe, "layers": []}, {**self.recipe, "layers": self.recipe["layers"] * 17},
                       {**self.recipe, "seed": True}, {**self.recipe, "peak_db": 1},
                       {**self.recipe, "effects": {"delay_feedback": 1}},
                       {**self.recipe, "effects": {"reverb_seconds": float("inf")}},
                       {**self.recipe, "effects": {"highpass_hz": 4000, "lowpass_hz": 2000}},
                       {**self.recipe, "effects": {"missing": 1}}]
        for patch in ({"start": 0.3}, {"pan": 2}, {"pan_end": -1.5}, {"frequency": "440"}, {"seed": -1},
                      {"note": "H2"}, {"note": "D#0"}, {"frequency": 440, "note": "A4"},
                      {"frequency_end": 880, "note_end": "A5"},
                      {"preset": "kick", "note_end": "A2"}, {"preset": "noise", "frequency_end": 800},
                      {"preset": "wind", "frequency_end": 800},
                      {"highpass_hz": 3000, "lowpass_hz": 1000}, {"frequency": 55, "highpass_hz": 5000},
                      {"preset": "unknown"}, {"fade_in": 0.2, "fade_out": 0.2}, {"source": "file.wav"}):
            bad_recipes.append({**self.recipe, "layers": [{**self.recipe["layers"][0], **patch}]})
        for recipe in bad_recipes:
            with self.subTest(recipe=recipe), self.assertRaises(ValueError):
                self.engine.render_recipe(recipe, "invalid.wav")
        self.assertEqual(list(self.engine.workspace.iterdir()), [])

    def test_maximum_duration_and_layer_count_remain_bounded(self):
        recipe = {"duration": 30, "layers": [
            {"preset": "tone", "start": index, "duration": 0.02, "frequency": 100 + index * 10}
            for index in range(16)
        ]}
        result = self.engine.render_recipe(recipe, "bounded.wav")
        self.assertEqual(result["frames"], 30 * 48000)
        self.assertEqual(result["layers"], 16)
        self.assertEqual(result["full_scale_samples"], 0)

    def test_demo_recipes_match_published_audio(self):
        root = Path(__file__).resolve().parents[1]
        for recipe_file in sorted((root / "examples/recipes").glob("*.json")):
            with self.subTest(recipe=recipe_file.name):
                recipe = json.loads(recipe_file.read_text())
                report = self.engine.render_recipe(recipe, recipe_file.stem + ".wav")
                self.assertEqual(report["channels"], 2)
                self.assertEqual(report["full_scale_samples"], 0)
                expected = root / "examples/audio" / (recipe_file.stem + ".wav")
                with wave.open(str(expected), "rb") as wav:
                    expected_samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").reshape(-1, 2) / 32768
                    actual, _ = self.engine._read(recipe_file.stem + ".wav")
                    # FFT libraries may differ in the final quantization bit across platforms.
                    np.testing.assert_allclose(actual, expected_samples, atol=1 / 32768, rtol=0)

if __name__ == "__main__":
    unittest.main()
