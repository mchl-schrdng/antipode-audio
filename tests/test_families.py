from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

import numpy as np

from antipode.engine import AudioEngine
from antipode.recipes import resolve_member


class SoundFamilyTests(unittest.TestCase):
    def setUp(self):
        self.family = {
            "base": {
                "duration": 0.8, "seed": 12,
                "layers": [{"preset": "chime", "duration": 0.1, "frequency": 300}],
            },
            "members": {
                "ouverture": {},
                "alerte": {"events": [
                    {"layer": 0, "start": 0.1}, {"layer": 0, "start": 0.5, "note": "C5"},
                ]},
            },
        }

    def test_shared_edits_and_independent_returned_recipes(self):
        base = self.family["base"]
        self.assertEqual(resolve_member(self.family, "ouverture"), base)
        base["layers"][0]["preset"] = "glass"
        base["effects"] = {"reverb_mix": 0.1}
        before = deepcopy(self.family)
        alert = resolve_member(self.family, "alerte")
        self.assertEqual([layer["preset"] for layer in alert["layers"]], ["glass", "glass"])
        self.assertEqual(alert["effects"], base["effects"])
        self.assertEqual(alert["layers"][0]["frequency"], 300)
        self.assertEqual(alert["layers"][1]["note"], "C5")
        self.assertNotIn("frequency", alert["layers"][1])
        self.assertEqual(alert, resolve_member(self.family, "alerte"))
        alert["effects"]["reverb_mix"] = 0.9
        alert["layers"][0]["preset"] = "wind"
        self.assertEqual(self.family, before)
        self.assertEqual(resolve_member(self.family, "ouverture"), base)

    def test_rhythm_duration_and_repeatable_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = AudioEngine(directory)
            self.family["members"]["alerte"]["duration"] = 0.75
            opening = resolve_member(self.family, "ouverture")
            alert = resolve_member(self.family, "alerte")
            first = engine.render_recipe(opening, "opening.wav")
            second = engine.render_recipe(alert, "alert.wav")
            self.assertEqual(first["duration_seconds"], 0.8)
            self.assertEqual(second["duration_seconds"], 0.75)
            audio, rate = engine._read("alert.wav")
            for start, end, audible in ((0, .1, False), (.1, .2, True), (.2, .5, False), (.5, .6, True)):
                peak = np.max(np.abs(audio[round(start * rate):round(end * rate)]))
                self.assertEqual(peak > 0.01, audible)
            engine.render_recipe(resolve_member(self.family, "alerte"), "again.wav")
            self.assertEqual((Path(directory) / "alert.wav").read_bytes(), (Path(directory) / "again.wav").read_bytes())

    def test_reordering_preserves_the_source_voice(self):
        base = self.family["base"]
        base["seed"] = 2**32 - 1
        base["layers"] = [
            {"preset": "noise", "duration": 0.2},
            {"preset": "noise", "start": 0.4, "duration": 0.2},
            {"preset": "noise", "start": 0.7, "duration": 0.05, "seed": 123},
        ]
        self.family["members"]["inverse"] = {"events": [{"layer": i} for i in (2, 1, 0)]}
        inverse = resolve_member(self.family, "inverse")
        self.assertEqual([layer["seed"] for layer in inverse["layers"]], [123, 0, 2**32 - 1])
        with tempfile.TemporaryDirectory() as directory:
            engine = AudioEngine(directory)
            engine.render_recipe(base, "base.wav")
            engine.render_recipe(inverse, "inverse.wav")
            self.assertEqual((Path(directory) / "base.wav").read_bytes(), (Path(directory) / "inverse.wav").read_bytes())

    def test_performance_edits_preserve_the_shared_material(self):
        layer = {"material": "metal", "gesture": "strike", "duration": 0.3, "damping": 0.2,
                 "note": "A4", "automation": {"pan": [[0, -0.5], [0.3, 0.5]]}}
        self.family["base"]["layers"] = [layer]
        self.family["members"]["contact"] = {"events": [
            {"layer": 0, "gesture": "rub", "frequency": 420},
        ]}
        layer["material"] = "glass"
        free = resolve_member(self.family, "ouverture")["layers"][0]
        contact = resolve_member(self.family, "contact")["layers"][0]
        self.assertEqual((free["material"], contact["material"]), ("glass", "glass"))
        self.assertEqual((free["gesture"], contact["gesture"]), ("strike", "rub"))
        self.assertEqual(contact["damping"], free["damping"])
        self.assertNotIn("note", contact)
        self.assertEqual(contact["automation"], free["automation"])
        with tempfile.TemporaryDirectory() as directory:
            engine = AudioEngine(directory)
            selected = engine.render_recipe(self.family, "contact.wav", member="contact")
            resolved = engine.render_recipe(resolve_member(self.family, "contact"), "resolved.wav")
            self.assertEqual(selected["recipe_sha256"], resolved["recipe_sha256"])
            self.assertEqual((Path(directory) / "contact.wav").read_bytes(),
                             (Path(directory) / "resolved.wav").read_bytes())

    def test_event_takes_over_only_its_own_automated_controls(self):
        curves = {"pan": [[0, -0.8], [0.1, 0.6]], "level_db": [[0, -30], [0.1, -6]]}
        self.family["base"]["layers"][0]["automation"] = deepcopy(curves)
        self.family["members"]["edit"] = {"events": [
            {"layer": 0, "pan_end": 0.5},
            {"layer": 0, "start": 0.2, "pan": 0, "level_db": -9},
        ]}
        first, second = resolve_member(self.family, "edit")["layers"]
        self.assertEqual((first["pan"], first["pan_end"]), (-0.8, 0.5))
        self.assertEqual(first["automation"], {"level_db": curves["level_db"]})
        self.assertNotIn("automation", second)
        self.assertEqual(self.family["base"]["layers"][0]["automation"], curves)
        with tempfile.TemporaryDirectory() as directory:
            AudioEngine(directory).render_recipe(self.family, "edit.wav", member="edit")

    def test_invalid_family_fields_and_events(self):
        failures = [
            (None, "ouverture"), ({**self.family, "event": 1}, "ouverture"),
            (self.family, "other"), (self.family, []),
            ({"base": self.family["base"], "members": {"": {}}}, ""),
            ({"base": {"duration": 1, "layers": []}, "members": {"x": {}}}, "x"),
        ]
        for arrangement in (None, {"peak_db": -4}, {"events": []}, {"events": [{"layer": 0}] * 17}):
            failures.append(({**self.family, "members": {"x": arrangement}}, "x"))
        for event in ({}, {"layer": True}, {"layer": 1}, {"layer": -1}, {"layer": 0, "preset": "noise"},
                      {"layer": 0, "frequency": 330, "note": "A4"}, {"layer": 0, "note_end": "C5", "frequency_end": 500}):
            failures.append(({**self.family, "members": {"x": {"events": [event]}}}, "x"))
        for family, member in failures:
            with self.subTest(family=family, member=member), self.assertRaises(ValueError):
                resolve_member(family, member)


if __name__ == "__main__":
    unittest.main()
