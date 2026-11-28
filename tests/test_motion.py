import copy
import tempfile
import unittest

import numpy as np

from antipode.engine import AudioEngine
from antipode.motion import curve_values, swept_lowpass
from antipode.synthesis import SAMPLE_RATE


class MotionTests(unittest.TestCase):
    def test_interpolation_uses_local_seconds_and_holds_last_point(self):
        level = [[0, -24], [0.25, 0], [0.5, -48]]
        np.testing.assert_array_equal(curve_values(level, 8, rate=8), [-24, -12, 0, -24, -48, -48, -48, -48])
        cutoff = curve_values([[0, 200], [1, 20000]], 4, logarithmic=True, rate=2)
        np.testing.assert_allclose(cutoff, [200, 2000, 20000, 20000])

    def test_invalid_automation_rejected_before_render(self):
        pan = {"pan": [[0, -1], [1, 1]]}
        invalid = [
            {"automation": value} for value in (
                None, {}, [], {"width": [[0, 1], [1, 2]]}, {"pan": [[0, 1]]},
                {"pan": [[0, 0]] * 65}, {"pan": [{"time": 0, "value": 0}, [1, 1]]},
                {"pan": [[0.1, 0], [1, 1]]}, {"pan": [[0, 0], [0, 1]]},
                {"pan": [[0, 0], [0.8, 1], [0.4, -1]]}, {"pan": [[0, 0], [2, 1]]},
                {"level_db": [[0, 0], [1, True]]}, {"level_db": [[0, -61], [1, 0]]},
                {"pan": [[False, 0], [1, 0]]}, {"pan": [[0, 0], [float("nan"), 0]]},
                {"pan": [[0, 0], [1, float("inf")]]}, {"lowpass_hz": [[0, 19], [1, 200]]},
            )
        ] + [
            {"automation": pan, "pan": -1}, {"automation": pan, "pan_end": 0},
            {"automation": {"level_db": [[0, 0], [1, -6]]}, "level_db": -6},
            {"automation": {"lowpass_hz": [[0, 200], [1, 500]]}, "lowpass_hz": 300},
            {"automation": {"lowpass_hz": [[0, 900], [0.5, 300], [1, 500]]}, "highpass_hz": 300},
        ]
        with tempfile.TemporaryDirectory() as directory:
            engine = AudioEngine(directory)
            for patch in invalid:
                with self.subTest(patch=patch), self.assertRaisesRegex(ValueError, "automation"):
                    engine.render_recipe({"duration": 1, "layers": [{"duration": 1, "preset": "tone", **patch}]}, "bad.wav")
            self.assertEqual(list(engine.workspace.iterdir()), [])

    def test_filter_retains_state_across_blocks_and_reaches_specified_cutoff(self):
        # Include an abrupt change, both cutoff extremes and a partial last block.
        source = np.random.default_rng(10).normal(size=2057)
        points = [[0, 20], [0.015, 20], [0.0151, 20000], [0.022, 800], [0.04, 20]]
        cutoffs = curve_values(points, len(source), logarithmic=True)
        expected = []
        first = second = 0.
        for sample, cutoff in zip(source, cutoffs):
            difference = (1 - np.cos(2 * np.pi * cutoff / SAMPLE_RATE)) / (np.sqrt(2) - 1)
            pole = 1 / (1 + difference + np.sqrt(difference * (difference + 2)))
            first += (1 - pole) * (sample - first)
            second += (1 - pole) * (first - second)
            expected.append(second)
        filtered = swept_lowpass(source[:, None], points)
        np.testing.assert_allclose(filtered[:, 0], expected, atol=1e-10, rtol=1e-10)
        tone = np.sin(2 * np.pi * 1000 * np.arange(4800) / SAMPLE_RATE)
        response = swept_lowpass(tone[:, None], [[0, 1000], [0.1, 1000]])
        transfer = np.std(response[2400:]) / np.std(tone[2400:])
        self.assertAlmostEqual(transfer, 1 / np.sqrt(2), places=6)

    def test_layer_uses_absolute_gain_and_equal_power_pan_from_its_start(self):
        layer = {"preset": "tone", "frequency": 1000, "duration": 1, "start": 0.1, "automation": {
            "level_db": [[0, -18], [0.2, -18], [0.3, -6], [0.7, -6]],
            "pan": [[0, -1], [0.2, -1], [0.3, 0], [0.5, 0], [0.6, 1]],
        }}
        recipe = {"duration": 1.3, "layers": [layer]}
        original = copy.deepcopy(recipe)
        with tempfile.TemporaryDirectory() as directory:
            engine = AudioEngine(directory)
            engine.render_recipe(recipe, "motion.wav")
            samples, rate = engine._read("motion.wav")
        self.assertEqual(recipe, original)
        self.assertTrue(np.all(samples[:round(0.1 * rate)] == 0))
        early, center, late = (samples[round(t * rate):round((t + 0.05) * rate)] for t in (0.2, 0.45, 0.85))
        self.assertTrue(np.all(early[:, 1] == 0))
        self.assertTrue(np.all(late[:, 0] == 0))
        np.testing.assert_allclose(center[:, 0], center[:, 1], atol=1 / 32768)
        self.assertAlmostEqual(np.linalg.norm(late) / np.linalg.norm(early), 10**(12 / 20), places=3)
        self.assertAlmostEqual(np.linalg.norm(center) / np.linalg.norm(late), 1, places=3)

    def test_cutoff_opens_and_closes_three_times_on_sustained_noise(self):
        points = [[0, 200]]
        for t in (0.2, 0.6, 1.0):
            points.extend([[t - 0.09, 200], [t, 8000], [t + 0.08, 8000], [t + 0.14, 200]])
        layer = {"preset": "noise", "duration": 1.35, "automation": {"lowpass_hz": points}}
        with tempfile.TemporaryDirectory() as directory:
            engine = AudioEngine(directory)
            recipe = {"duration": 1.4, "layers": [layer], "seed": 41}
            engine.render_recipe(recipe, "motion.wav")
            samples, rate = engine._read("motion.wav")
            engine.render_recipe(recipe, "repeat.wav")
            repeat, _ = engine._read("repeat.wav")
            np.testing.assert_array_equal(samples, repeat)

        def brightness(at):
            window = samples[round(at * rate):round((at + 0.055) * rate), 0]
            power = np.abs(np.fft.rfft(window * np.hanning(len(window))))**2
            return power[np.fft.rfftfreq(len(window), 1 / rate) > 4000].sum() / power.sum()

        for t in (0.2, 0.6, 1.0):
            self.assertGreater(brightness(t + 0.01), 100 * brightness(t + 0.145))
