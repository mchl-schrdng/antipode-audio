"""Deterministic audio operations shared by the CLI and MCP server."""

import hashlib
import json
import math
import os
from pathlib import Path
import stat
import tempfile
from typing import Literal
import wave

import numpy as np

from antipode.synthesis import PRESETS, SAMPLE_RATE, effects, fade as _fade, synthesize

MAX_DURATION = 30
Preset = Literal["tone", "chime", "kick", "noise", "sweep", "drone", "pad", "metal", "riser", "pulse", "glass", "wind"]


def _bounded(name: str, value: float, minimum: float, maximum: float) -> None:
    if type(value) not in (int, float) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be finite and between {minimum} and {maximum}.")


def _db(value: float) -> float | None:
    return round(20 * math.log10(value), 3) if value > 0 else None


class AudioEngine:
    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).expanduser().resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        if not isinstance(name, str) or any(character in name for character in ("\0", "\\", ":")):
            raise ValueError("Use a relative .wav path with forward slashes inside the audio workspace.")
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or relative.suffix.lower() != ".wav":
            raise ValueError("Use a relative .wav path inside the audio workspace.")
        candidate = self.workspace
        for part in relative.parts:
            candidate /= part
            if candidate.is_symlink():
                raise ValueError("Symbolic links are not allowed in audio paths.")
        return candidate

    def _read(self, name: str) -> tuple[np.ndarray, int]:
        source = self._path(name)
        info = source.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > 8 * 1024 * 1024:
            raise ValueError("Input must be a regular WAV file no larger than 8 MiB.")
        try:
            with wave.open(str(source), "rb") as wav:
                channels, width, rate, frames, compression, _ = wav.getparams()
                if channels not in (1, 2) or width != 2 or compression != "NONE":
                    raise ValueError("Only uncompressed 16-bit PCM mono/stereo WAV is supported.")
                if not 8_000 <= rate <= SAMPLE_RATE or not 1 <= frames <= rate * MAX_DURATION:
                    raise ValueError("WAV must be nonempty, at most 30 seconds, and 8–48 kHz.")
                raw = wav.readframes(frames)
                if len(raw) != frames * channels * width:
                    raise ValueError("WAV data is truncated.")
        # wave raises RuntimeError when a chunk seeks beyond its RIFF container.
        except (wave.Error, EOFError, RuntimeError) as error:
            raise ValueError(f"Invalid PCM WAV: {str(error) or 'malformed or truncated RIFF chunks'}") from error
        return np.frombuffer(raw, dtype="<i2").reshape(-1, channels).astype(np.float64) / 32768, rate

    def _write(self, name: str, samples: np.ndarray, rate: int) -> dict:
        destination = self._path(name)
        if not np.isfinite(samples).all() or np.max(np.abs(samples)) > 1:
            raise ValueError("Output would clip. Reduce gain or set normalize_db to -1 or lower.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        pcm = np.clip(np.rint(samples * 32768), -32768, 32767).astype("<i2")
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".tmp", delete=False) as file:
                temporary = Path(file.name)
                with wave.open(file, "wb") as wav:
                    wav.setparams((samples.shape[1], 2, rate, len(samples), "NONE", "not compressed"))
                    wav.writeframes(pcm.tobytes())
            # Publish a complete file without replacing another agent's output.
            os.link(temporary, destination)
        except FileExistsError as error:
            raise ValueError(f"{name} already exists. Choose a new output filename.") from error
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return self.analyze_audio(name)

    def list_presets(self) -> dict[str, str]:
        """List local DSP presets. No model, API key, network or GPU is required."""
        return PRESETS.copy()

    def generate_sound(
        self,
        output: str,
        preset: Preset = "chime",
        duration: float = 1.0,
        frequency: float = 660.0,
        level_db: float = -12.0,
        seed: int = 0,
    ) -> dict[str, object]:
        """Create a 48 kHz mono PCM16 WAV. Output is a new relative workspace path.

        Duration: 0.02–30 seconds. Frequency: 20–8000 Hz (ignored for noise).
        Level_db: peak target from -60 to -1 dBFS. Seed: 0–4294967295, used for noise.
        Returns measured file metadata; never overwrites an existing file.
        """
        self._path(output)
        if not isinstance(preset, str) or preset not in PRESETS:
            raise ValueError(f"Unknown preset. Choose from: {', '.join(PRESETS)}.")
        _bounded("duration", duration, 0.02, MAX_DURATION)
        _bounded("frequency", frequency, 20, 8_000)
        _bounded("level_db", level_db, -60, -1)
        if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
            raise ValueError("seed must be an integer between 0 and 4294967295.")
        samples = synthesize(preset, duration, frequency, seed) * 10 ** (level_db / 20)
        return {**self._write(output, samples, SAMPLE_RATE), "preset": preset, "seed": seed}

    def render_recipe(self, recipe: dict, output: str) -> dict[str, object]:
        """Render a layered sound-design recipe to a new stereo 48 kHz PCM16 WAV.

        Recipe requires duration (0.02–30 seconds) and layers (1–16 objects).
        Optional seed (0–4294967295), peak_db (-60 to -1, default -3), effects object.
        Each layer requires preset and duration; optional start, frequency (20–8000),
        level_db (-60 to 0), pan (-1 left to 1 right), fade_in/fade_out seconds, seed.
        Effects: highpass_hz (0–10000, default0), lowpass_hz (20–20000, default20000),
        drive (1–12, default1), delay_seconds (.01–2, default.375), delay_feedback
        (0–.85, default.35), delay_mix (0–1, default0), reverb_seconds (.1–5,
        default1.8), reverb_mix (0–1, default0). Duration includes effect tails.
        Example: {"duration": 4, "layers": [{"preset": "drone", "duration": 3,
        "frequency": 55}], "effects": {"reverb_mix": 0.3}}.
        Unknown fields are rejected. This synthesizes original oscillators/noise;
        it does not load recordings, models, or URLs. Existing files are preserved.
        """
        self._path(output)

        def fields(value: dict, allowed: set[str], label: str) -> None:
            if not isinstance(value, dict) or any(key not in allowed for key in value):
                raise ValueError(f"{label} must be an object containing only: {', '.join(sorted(allowed))}.")

        def seed_value(value: int) -> None:
            if type(value) is not int or not 0 <= value <= 2**32 - 1:
                raise ValueError("seed must be an integer between 0 and 4294967295.")

        fields(recipe, {"duration", "layers", "seed", "peak_db", "effects"}, "recipe")
        duration = recipe.get("duration")
        _bounded("duration", duration, 0.02, MAX_DURATION)
        seed = recipe.get("seed", 0)
        seed_value(seed)
        target = recipe.get("peak_db", -3)
        _bounded("peak_db", target, -60, -1)
        layers = recipe.get("layers")
        if not isinstance(layers, list) or not 1 <= len(layers) <= 16:
            raise ValueError("layers must contain 1–16 layer objects.")
        options = recipe.get("effects", {})
        bounds = {
            "highpass_hz": (0, 10000), "lowpass_hz": (20, 20000), "drive": (1, 12),
            "delay_seconds": (0.01, 2), "delay_feedback": (0, 0.85), "delay_mix": (0, 1),
            "reverb_seconds": (0.1, 5), "reverb_mix": (0, 1),
        }
        fields(options, set(bounds), "effects")
        for key, value in options.items():
            _bounded(key, value, *bounds[key])
        if options.get("highpass_hz", 0) >= options.get("lowpass_hz", 20000):
            raise ValueError("highpass_hz must be below lowpass_hz.")
        prepared = []
        frames = round(duration * SAMPLE_RATE)
        for index, layer in enumerate(layers):
            fields(layer, {"preset", "start", "duration", "frequency", "level_db", "pan", "fade_in", "fade_out", "seed"}, "layer")
            preset = layer.get("preset")
            if not isinstance(preset, str) or preset not in PRESETS:
                raise ValueError(f"Unknown layer preset. Choose from: {', '.join(PRESETS)}.")
            length = layer.get("duration")
            _bounded("layer duration", length, 0.02, duration)
            values = {
                "start": layer.get("start", 0), "duration": length,
                "frequency": layer.get("frequency", 220), "level_db": layer.get("level_db", -12),
                "pan": layer.get("pan", 0), "fade_in": layer.get("fade_in", min(0.005, length / 4)),
                "fade_out": layer.get("fade_out", min(0.02, length / 4)),
                "seed": layer.get("seed", (seed + index) % 2**32), "preset": preset,
            }
            for key, limits in {
                "start": (0, duration), "frequency": (20, 8000), "level_db": (-60, 0),
                "pan": (-1, 1), "fade_in": (0, length), "fade_out": (0, length),
            }.items():
                _bounded(key, values[key], *limits)
            seed_value(values["seed"])
            layer_frames = round(length * SAMPLE_RATE)
            if round(values["start"] * SAMPLE_RATE) + layer_frames > frames:
                raise ValueError("Every layer must fit inside the recipe duration.")
            if round(values["fade_in"] * SAMPLE_RATE) + round(values["fade_out"] * SAMPLE_RATE) > layer_frames:
                raise ValueError("Combined layer fades must fit inside the layer duration.")
            prepared.append(values)
        mix = np.zeros((frames, 2))
        for layer in prepared:
            voice = synthesize(layer["preset"], layer["duration"], layer["frequency"], layer["seed"])
            _fade(voice, SAMPLE_RATE, layer["fade_in"], layer["fade_out"])
            angle = (layer["pan"] + 1) * np.pi / 4
            stereo = voice * np.array([np.cos(angle), np.sin(angle)]) * 10 ** (layer["level_db"] / 20)
            start = round(layer["start"] * SAMPLE_RATE)
            mix[start:start + len(voice)] += stereo
        mix = effects(mix, options, seed)
        _fade(mix, SAMPLE_RATE, min(0.005, duration / 4), min(0.08, duration / 4))
        peak = float(np.max(np.abs(mix)))
        if peak:
            mix *= 10 ** (target / 20) / peak
        digest = hashlib.sha256(json.dumps(recipe, sort_keys=True, allow_nan=False).encode()).hexdigest()
        return {**self._write(output, mix, SAMPLE_RATE), "layers": len(layers), "seed": seed, "recipe_sha256": digest}

    def process_audio(
        self,
        source: str,
        output: str,
        gain_db: float = 0.0,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
        reverse: bool = False,
        normalize_db: float | None = None,
    ) -> dict[str, object]:
        """Process a PCM16 WAV into a new relative workspace path; keep rate and channels.

        Order: reverse, gain (-60 to 24 dB), fades in seconds, optional peak normalization
        (-60 to -1 dBFS). Fades must fit within the file. Clipping is rejected.
        Source is preserved; output is never overwritten. Silence stays silent.
        """
        self._path(output)
        _bounded("gain_db", gain_db, -60, 24)
        _bounded("fade_in", fade_in, 0, MAX_DURATION)
        _bounded("fade_out", fade_out, 0, MAX_DURATION)
        if normalize_db is not None:
            _bounded("normalize_db", normalize_db, -60, -1)
        samples, rate = self._read(source)
        if round(fade_in * rate) + round(fade_out * rate) > len(samples):
            raise ValueError("Combined fades must not exceed the audio duration.")
        if reverse:
            samples = samples[::-1].copy()
        samples *= 10 ** (gain_db / 20)
        _fade(samples, rate, fade_in, fade_out)
        peak = float(np.max(np.abs(samples)))
        if normalize_db is not None and peak > 0:
            samples *= 10 ** (normalize_db / 20) / peak
        return self._write(output, samples, rate)

    def analyze_audio(self, source: str) -> dict[str, object]:
        """Measure a workspace PCM16 WAV: duration, rate, channels, peak/RMS dBFS and
        full-scale sample count. Null dBFS means silence. RMS is not LUFS or true peak.
        """
        samples, rate = self._read(source)
        return {
            "path": str(self._path(source)),
            "duration_seconds": len(samples) / rate,
            "sample_rate": rate,
            "channels": samples.shape[1],
            "frames": len(samples),
            "peak_dbfs": _db(float(np.max(np.abs(samples)))),
            "rms_dbfs": _db(float(np.sqrt(np.mean(samples**2)))),
            "full_scale_samples": int(np.count_nonzero((samples <= -1) | (samples >= 32767 / 32768))),
        }
