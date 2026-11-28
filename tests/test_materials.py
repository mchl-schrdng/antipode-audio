import unittest

import numpy as np

from antipode.materials import synthesize_material, validate_material
from antipode.synthesis import SAMPLE_RATE


class MaterialTests(unittest.TestCase):
    def test_holding_a_struck_plate_damps_its_tail(self):
        def tail_energy(damping):
            signal = synthesize_material("metal", "strike", damping, 1.5, 280, 17)
            onset = signal[:SAMPLE_RATE // 10]
            tail = signal[3 * SAMPLE_RATE // 10:]
            return np.sum(tail**2) / np.sum(onset**2)

        free, light, held = (tail_energy(damping) for damping in (0, .35, 1))
        self.assertGreater(free, .5)
        self.assertGreater(free, light * 5)
        self.assertGreater(light, held * 20)

    def test_each_body_keeps_its_resonances_across_gestures(self):
        for material, second_mode in (("metal", 1.51), ("glass", 2.68), ("wood", 2.57)):
            for gesture in ("strike", "rub"):
                with self.subTest(material=material, gesture=gesture):
                    signal = synthesize_material(material, gesture, 0, 1.5, 280, 17)[:, 0]
                    power = np.abs(np.fft.rfft(signal * np.hanning(len(signal))))**2
                    frequencies = np.fft.rfftfreq(len(signal), 1 / SAMPLE_RATE)
                    for mode_hz in (280, 280 * second_mode):
                        distance = np.abs(frequencies - mode_hz)
                        peak_band = power[distance < 8].sum()
                        shoulders = power[(distance > 12) & (distance < 28)].sum()
                        self.assertGreater(peak_band, 3 * shoulders)

    def test_rubbing_continues_to_drive_a_held_object(self):
        for material in ("metal", "glass", "wood"):
            with self.subTest(material=material):
                strike = synthesize_material(material, "strike", .85, 1., 280, 17)
                rub = synthesize_material(material, "rub", .85, 1., 280, 17)
                middle = slice(SAMPLE_RATE // 2, 3 * SAMPLE_RATE // 4)
                self.assertLess(np.mean(strike[middle]**2), 1e-6)
                self.assertGreater(np.mean(rub[middle]**2), 1e-3)

    def test_short_contacts_are_bounded_and_reproducible_at_pitch_limits(self):
        for gesture, frequency in (("strike", 20), ("rub", 8000)):
            with self.subTest(gesture=gesture):
                def render(seed):
                    return synthesize_material("wood", gesture, 1, .02, frequency, seed)

                voice = render(0)
                self.assertEqual(voice.shape, (960, 1))
                self.assertEqual(np.max(np.abs(voice)), 1.)
                self.assertEqual(voice[0, 0], 0)
                self.assertEqual(voice[-1, 0], 0)
                np.testing.assert_array_equal(voice, render(0))
                self.assertFalse(np.array_equal(voice, render(2**32 - 1)))

    def test_invalid_contact_parameters(self):
        for parameters in (([], "strike", 0), ("stone", "strike", 0), ("glass", {}, .3),
                           ("metal", "rub", True), ("wood", "rub", float("nan")),
                           ("wood", "rub", -.1), ("glass", "strike", 1.01)):
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                validate_material(*parameters)


if __name__ == "__main__":
    unittest.main()
