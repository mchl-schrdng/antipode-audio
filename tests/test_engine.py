from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import struct
import tempfile
import unittest
import wave

import numpy as np

from antipode.engine import AudioEngine, PRESETS


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.engine = AudioEngine(self.root / "audio")

    def test_every_preset_produces_finite_faded_audio_at_requested_peak(self):
        for preset in PRESETS:
            with self.subTest(preset=preset):
                result = self.engine.generate_sound(f"{preset}.wav", preset=preset, duration=0.1)
                samples, rate = self.engine._read(f"{preset}.wav")
                self.assertEqual(samples.shape, (4800, 1))
                self.assertEqual(rate, 48000)
                self.assertTrue(np.isfinite(samples).all())
                self.assertEqual(samples[0, 0], 0)
                self.assertEqual(samples[-1, 0], 0)
                self.assertAlmostEqual(result["peak_dbfs"], -12, places=2)
                self.assertEqual(result["full_scale_samples"], 0)

    def test_tone_frequency_and_seeded_noise_are_reproducible(self):
        self.engine.generate_sound("tone.wav", preset="tone", duration=1, frequency=440)
        samples, rate = self.engine._read("tone.wav")
        frequency = np.fft.rfftfreq(len(samples), 1 / rate)[np.argmax(np.abs(np.fft.rfft(samples[:, 0])))]
        self.assertEqual(frequency, 440)
        for name, seed in (("a", 42), ("b", 42), ("c", 43)):
            self.engine.generate_sound(name + ".wav", preset="noise", duration=0.02, seed=seed)
        self.assertEqual((self.engine.workspace / "a.wav").read_bytes(), (self.engine.workspace / "b.wav").read_bytes())
        self.assertNotEqual((self.engine.workspace / "a.wav").read_bytes(), (self.engine.workspace / "c.wav").read_bytes())

    def test_invalid_generation_creates_no_files(self):
        for options in ({"duration": float("nan")}, {"frequency": float("inf")}, {"duration": 31},
                        {"seed": True}, {"seed": -1}, {"level_db": 0}, {"preset": "missing"}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.engine.generate_sound("bad.wav", **options)
        self.assertEqual(list(self.engine.workspace.iterdir()), [])

    def test_paths_and_symlinks_do_not_escape_workspace(self):
        for name in ("../outside.wav", str(self.root / "outside.wav"), "sound.mp3", "bad\0.wav"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.engine.generate_sound(name)
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (self.engine.workspace / "link").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks is unavailable on this host.")
        with self.assertRaises(ValueError):
            self.engine.generate_sound("link/escape.wav")
        self.assertEqual(list(outside.iterdir()), [])

    def test_windows_drive_paths_and_alternate_streams_are_rejected_on_every_host(self):
        for name in ("C:outside.wav", "D:outside.wav", "C:/outside.wav", "sample.wav:stream.wav",
                     "folder:stream/sound.wav", r"\outside.wav", r"\\server\share\outside.wav",
                     r"..\outside.wav", r"folder\sound.wav"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.engine.generate_sound(name)
        self.assertEqual(list(self.engine.workspace.iterdir()), [])
        self.engine.generate_sound("nested/sound.wav", duration=0.02)
        self.assertTrue((self.engine.workspace / "nested/sound.wav").is_file())

    def test_concurrent_writers_publish_once_without_replacing_output(self):
        def generate(seed):
            try:
                self.engine.generate_sound("shared.wav", preset="noise", duration=0.1, seed=seed)
                return True
            except ValueError as error:
                self.assertIn("already exists", str(error))
                return False

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(generate, [1, 2]))
        self.assertEqual(sum(results), 1)
        self.assertEqual(self.engine.analyze_audio("shared.wav")["frames"], 4800)
        self.assertEqual([file.name for file in self.engine.workspace.iterdir()], ["shared.wav"])

    def test_processing_preserves_source_and_handles_silence(self):
        original = np.array([[1000, -2000], [3000, -4000], [5000, -6000]], dtype="<i2")
        source = self.engine.workspace / "stereo.wav"
        with wave.open(str(source), "wb") as wav:
            wav.setparams((2, 2, 44100, 3, "NONE", "not compressed"))
            wav.writeframes(original.tobytes())
        before = source.read_bytes()
        self.engine.process_audio("stereo.wav", "reverse.wav", reverse=True)
        samples, rate = self.engine._read("reverse.wav")
        np.testing.assert_array_equal(samples * 32768, original[::-1])
        self.assertEqual(rate, 44100)
        self.assertEqual(source.read_bytes(), before)
        with self.assertRaises(ValueError):
            self.engine.process_audio("stereo.wav", "stereo.wav")
        with self.assertRaises(ValueError):
            self.engine.process_audio("stereo.wav", "clipped.wav", gain_db=24)
        self.assertFalse((self.engine.workspace / "clipped.wav").exists())
        with wave.open(str(self.engine.workspace / "silent.wav"), "wb") as wav:
            wav.setparams((1, 2, 48000, 480, "NONE", "not compressed"))
            wav.writeframes(bytes(960))
        report = self.engine.process_audio("silent.wav", "silent-normalized.wav", normalize_db=-1)
        self.assertIsNone(report["rms_dbfs"])
        self.assertIsNone(report["peak_dbfs"])

    def test_truncated_and_unsupported_wav_are_rejected(self):
        self.engine.generate_sound("cut.wav", duration=0.02)
        source = self.engine.workspace / "cut.wav"
        source.write_bytes(source.read_bytes()[:-3])
        with self.assertRaisesRegex(ValueError, "truncated"):
            self.engine.analyze_audio("cut.wav")
        source.write_bytes(b"not a wave")
        with self.assertRaisesRegex(ValueError, "Invalid PCM WAV"):
            self.engine.analyze_audio("cut.wav")

    def test_malformed_riff_chunks_are_reported_as_format_errors(self):
        source = self.engine.workspace / "corrupt.wav"
        corrupt_files = (
            b"RIFF" + struct.pack("<I", 12) + b"WAVEJUNK" + struct.pack("<I", 0xFFFFFFFF),
            b"RIFF" + struct.pack("<I", 36) + b"WAVEfmt " + struct.pack("<I", 16) + b"\x01\x00",
            b"RIFF" + struct.pack("<I", 12) + b"WAVEdata" + struct.pack("<I", 0),
        )
        for blob in corrupt_files:
            with self.subTest(blob=blob):
                source.write_bytes(blob)
                with self.assertRaisesRegex(ValueError, "Invalid PCM WAV"):
                    self.engine.analyze_audio("corrupt.wav")
        self.engine.generate_sound("valid.wav", duration=0.02)
        original = (self.engine.workspace / "valid.wav").read_bytes()
        extra_chunk = b"JUNK" + struct.pack("<I", 4) + b"test"
        source.write_bytes(b"RIFF" + struct.pack("<I", len(original) - 8 + len(extra_chunk))
                           + b"WAVE" + extra_chunk + original[12:])
        self.assertEqual(self.engine.analyze_audio("corrupt.wav")["frames"], 960)


if __name__ == "__main__":
    unittest.main()
