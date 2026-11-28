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

from antipode.materials import synthesize_material, validate_material
from antipode.motion import curve_values, swept_lowpass, validate_automation
from antipode.recipes import RECIPE_FIELDS, check_fields, checked_seed, layer_seed, resolve_member
from antipode.synthesis import PRESETS, SAMPLE_RATE, effects, fade as _fade, spectral_filter, synthesize

MAX_DURATION = 30
Preset = Literal[
    "tone", "chime", "kick", "noise", "sweep", "drone", "pad", "metal",
    "riser", "pulse", "glass", "wind", "pluck", "bell", "wood", "choir",
]
_NOTES = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def _bounded(name: str, value: float, minimum: float, maximum: float) -> None:
    if type(value) not in (int, float) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be finite and between {minimum} and {maximum}.")


def _note_hz(note: str) -> float:
    if not isinstance(note, str) or not 2 <= len(note) <= 3 or note[0].upper() not in _NOTES or note[-1] not in "012345678":
        raise ValueError("note must be E0–B8 (20–8000 Hz) with optional # or b (for example, A4, F#3, Eb2).")
    semitones = _NOTES[note[0].upper()] + (int(note[-1]) - 4) * 12
    if len(note) == 3:
        if note[1] not in ("#", "b"):
            raise ValueError("note accidental must be # or b.")
        semitones += 1 if note[1] == "#" else -1
    frequency = 440.0 * 2 ** (semitones / 12)
    if not 20 <= frequency <= 8_000:
        raise ValueError("note must be between E0 and B8 (20–8000 Hz).")
    return frequency


def _pitch(source: dict, hz_key: str, note_key: str, default: float | None = None) -> float | None:
    if hz_key in source and note_key in source:
        raise ValueError(f"Specify either {hz_key} or {note_key}, not both.")
    if note_key in source:
        return _note_hz(source[note_key])
    if hz_key in source or default is not None:
        value = source.get(hz_key, default)
        _bounded(hz_key, value, 20, 8_000)
        return value
    return None


def _db(value: float) -> float | None:
    return round(20 * math.log10(value), 3) if value > 0 else None


_LAYER_FIELDS = {
    "preset", "start", "duration", "frequency", "note", "frequency_end", "note_end",
    "level_db", "pan", "pan_end", "fade_in", "fade_out", "highpass_hz", "lowpass_hz", "seed",
    "material", "gesture", "damping", "automation",
}


def _prepare_layer(layer: dict, index: int, duration: float, seed: int) -> dict:
    check_fields(layer, _LAYER_FIELDS, "layer")
    preset = layer.get("preset")
    if ("material" in layer) == ("preset" in layer):
        raise ValueError("Choose exactly one layer source: preset or material.")
    if "material" in layer:
        source = {"material": layer["material"], "gesture": layer.get("gesture", "strike"),
                  "damping": layer.get("damping", 0.2)}
        validate_material(**source)
    else:
        if "gesture" in layer or "damping" in layer:
            raise ValueError("gesture and damping require a material layer.")
        if not isinstance(preset, str) or preset not in PRESETS:
            raise ValueError(f"Unknown layer preset. Choose from: {', '.join(PRESETS)}.")
        source = {"preset": preset}
    length = layer.get("duration")
    _bounded("layer duration", length, 0.02, duration)
    pan = layer.get("pan", 0)
    values = {
        "start": layer.get("start", 0), "duration": length,
        "frequency": _pitch(layer, "frequency", "note", 220),
        "frequency_end": _pitch(layer, "frequency_end", "note_end"),
        "level_db": layer.get("level_db", -12),
        "pan": pan, "pan_end": layer.get("pan_end", pan),
        "fade_in": layer.get("fade_in", min(0.005, length / 4)),
        "fade_out": layer.get("fade_out", min(0.02, length / 4)),
        "highpass_hz": layer.get("highpass_hz", 0),
        "lowpass_hz": layer.get("lowpass_hz", 20000),
        "seed": layer_seed(layer, seed, index), **source,
    }
    if values["frequency_end"] is not None:
        if "material" in source:
            raise ValueError("Material resonances use a fixed note or frequency.")
        if preset in ("kick", "noise", "wind"):
            raise ValueError(f"preset '{preset}' does not support frequency_end or note_end.")
    for key, limits in {
        "start": (0, duration), "level_db": (-60, 0),
        "pan": (-1, 1), "pan_end": (-1, 1), "fade_in": (0, length), "fade_out": (0, length),
        "highpass_hz": (0, 10000), "lowpass_hz": (20, 20000),
    }.items():
        _bounded(key, values[key], *limits)
    if values["highpass_hz"] >= values["lowpass_hz"]:
        raise ValueError("highpass_hz must be below lowpass_hz.")
    values["automation"] = validate_automation(layer, length)
    layer_frames = round(length * SAMPLE_RATE)
    if round(values["start"] * SAMPLE_RATE) + layer_frames > round(duration * SAMPLE_RATE):
        raise ValueError("Every layer must fit inside the recipe duration.")
    if round(values["fade_in"] * SAMPLE_RATE) + round(values["fade_out"] * SAMPLE_RATE) > layer_frames:
        raise ValueError("Combined layer fades must fit inside the layer duration.")
    return values


def _render_layer(layer: dict) -> np.ndarray:
    """Render a validated layer, with automation measured from its own start."""
    if "material" in layer:
        voice = synthesize_material(layer["material"], layer["gesture"], layer["damping"],
                                    layer["duration"], layer["frequency"], layer["seed"])
    else:
        voice = synthesize(layer["preset"], layer["duration"], layer["frequency"],
                           layer["seed"], layer["frequency_end"])
    automation = layer["automation"]
    static_filter = layer["highpass_hz"] != 0 or layer["lowpass_hz"] != 20000
    if static_filter:
        voice = spectral_filter(voice, layer["highpass_hz"], layer["lowpass_hz"])
    if "lowpass_hz" in automation:
        voice = swept_lowpass(voice, automation["lowpass_hz"])
    if static_filter or "lowpass_hz" in automation:
        voice_peak = float(np.max(np.abs(voice)))
        if voice_peak < 0.01:
            raise ValueError("Layer filter removes almost all signal; adjust highpass_hz or lowpass_hz.")
        voice /= voice_peak
    _fade(voice, SAMPLE_RATE, layer["fade_in"], layer["fade_out"])
    if "pan" in automation:
        pan = curve_values(automation["pan"], len(voice))
    elif layer["pan"] != layer["pan_end"]:
        pan = np.linspace(layer["pan"], layer["pan_end"], len(voice))
    else:
        pan = layer["pan"]
    angle = (pan + 1) * (np.pi / 4)
    pan_weights = np.stack((np.cos(angle), np.sin(angle)), axis=-1)
    level = layer["level_db"]
    if "level_db" in automation:
        level = curve_values(automation["level_db"], len(voice))[:, None]
    return voice * pan_weights * 10 ** (level / 20)


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
        frequency: float | None = None,
        level_db: float = -12.0,
        seed: int = 0,
        note: str | None = None,
    ) -> dict[str, object]:
        """Create a 48 kHz mono PCM16 WAV. Output is a new relative workspace path.

        Duration: 0.02–30 seconds. Frequency: 20–8000 Hz or note E0–B8 (default 660 Hz;
        ignored for noise; specify frequency or note, not both). Level_db: peak target
        from -60 to -1 dBFS. Seed: 0–4294967295, used for noise.
        Returns measured file metadata; never overwrites an existing file.
        """
        self._path(output)
        if not isinstance(preset, str) or preset not in PRESETS:
            raise ValueError(f"Unknown preset. Choose from: {', '.join(PRESETS)}.")
        _bounded("duration", duration, 0.02, MAX_DURATION)
        pitch = {key: value for key, value in (("frequency", frequency), ("note", note)) if value is not None}
        resolved_hz = _pitch(pitch, "frequency", "note", 660.0)
        _bounded("level_db", level_db, -60, -1)
        checked_seed(seed)
        samples = synthesize(preset, duration, resolved_hz, seed) * 10 ** (level_db / 20)
        return {**self._write(output, samples, SAMPLE_RATE), "preset": preset, "seed": seed}

    def render_recipe(self, recipe: dict, output: str, member: str | None = None) -> dict[str, object]:
        """Render a layered sound-design recipe to a new stereo 48 kHz PCM16 WAV.

        Recipe requires duration (0.02–30 seconds) and layers (1–16 objects).
        Optional seed (0–4294967295), peak_db (-60 to -1, default -3), effects object.
        For a family, pass {"base": recipe, "members": {name: arrangement}} and choose a member.
        Its optional events list selects base layers by zero-based index, e.g. {"layer": 0, "start": 0.2}.
        Each layer requires duration and either preset or material (metal, wood, glass).
        Material layers accept gesture ("strike" or "rub") and damping (0 free to 1 held).
        Layers support automation of pan, level_db and lowpass_hz with [seconds, value]
        points relative to the layer, starting at zero. Optional start, frequency (20–8000) or
        note (E0–B8), frequency_end or note_end (not supported for kick, noise or wind),
        level_db (-60 to 0, applied after layer filtering and re-normalization),
        pan/pan_end (-1 left to 1 right), fade_in/fade_out seconds, highpass_hz/lowpass_hz, seed.
        Effects: highpass_hz (0–10000, default0), lowpass_hz (20–20000, default20000),
        drive (1–12, default1), delay_seconds (.01–2, default.375), delay_feedback
        (0–.85, default.35), delay_mix (0–1, default0), reverb_seconds (.1–5,
        default1.8), reverb_mix (0–1, default0). Duration includes effect tails.
        Example: {"duration": 4, "layers": [{"preset": "drone", "duration": 3,
        "note": "A1"}], "effects": {"reverb_mix": 0.3}}.
        Unknown fields are rejected. This synthesizes original oscillators/noise;
        it does not load recordings, models, or URLs. Existing files are preserved.
        """
        self._path(output)
        if member is not None:
            recipe = resolve_member(recipe, member)
        elif isinstance(recipe, dict) and "members" in recipe:
            raise ValueError("Choose a member to render from this sound family.")

        check_fields(recipe, RECIPE_FIELDS, "recipe")
        duration = recipe.get("duration")
        _bounded("duration", duration, 0.02, MAX_DURATION)
        seed = checked_seed(recipe.get("seed", 0))
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
        check_fields(options, set(bounds), "effects")
        for key, value in options.items():
            _bounded(key, value, *bounds[key])
        if options.get("highpass_hz", 0) >= options.get("lowpass_hz", 20000):
            raise ValueError("highpass_hz must be below lowpass_hz.")
        frames = round(duration * SAMPLE_RATE)
        prepared = [_prepare_layer(layer, index, duration, seed) for index, layer in enumerate(layers)]
        mix = np.zeros((frames, 2))
        for layer in prepared:
            stereo = _render_layer(layer)
            start = round(layer["start"] * SAMPLE_RATE)
            mix[start:start + len(stereo)] += stereo
        mix = effects(mix, options, seed)
        _fade(mix, SAMPLE_RATE, min(0.005, duration / 4), min(0.08, duration / 4))
        peak = float(np.max(np.abs(mix)))
        if peak:
            mix *= 10 ** (target / 20) / peak
        digest = hashlib.sha256(json.dumps(recipe, sort_keys=True, allow_nan=False).encode()).hexdigest()
        report = {**self._write(output, mix, SAMPLE_RATE), "layers": len(layers), "seed": seed, "recipe_sha256": digest}
        if member is not None:
            report["member"] = member
        return report

    def process_audio(
        self,
        source: str,
        output: str,
        gain_db: float = 0.0,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
        reverse: bool = False,
        normalize_db: float | None = None,
        highpass_hz: float = 0.0,
        lowpass_hz: float = 20000.0,
    ) -> dict[str, object]:
        """Process a PCM16 WAV into a new relative workspace path; keep rate and channels.

        Order: reverse, spectral filter (highpass_hz 0–10000, lowpass_hz 20–20000),
        gain (-60 to 24 dB), fades in seconds, optional peak normalization (-60 to -1 dBFS).
        Fades must fit within the file. Clipping is rejected.
        Source is preserved; output is never overwritten. Silence stays silent.
        """
        self._path(output)
        _bounded("gain_db", gain_db, -60, 24)
        _bounded("fade_in", fade_in, 0, MAX_DURATION)
        _bounded("fade_out", fade_out, 0, MAX_DURATION)
        _bounded("highpass_hz", highpass_hz, 0, 10000)
        _bounded("lowpass_hz", lowpass_hz, 20, 20000)
        if highpass_hz >= lowpass_hz:
            raise ValueError("highpass_hz must be below lowpass_hz.")
        if normalize_db is not None:
            _bounded("normalize_db", normalize_db, -60, -1)
        samples, rate = self._read(source)
        if round(fade_in * rate) + round(fade_out * rate) > len(samples):
            raise ValueError("Combined fades must not exceed the audio duration.")
        if reverse:
            samples = samples[::-1].copy()
        if highpass_hz or lowpass_hz != 20000:
            samples = spectral_filter(samples, highpass_hz, lowpass_hz, rate)
        samples *= 10 ** (gain_db / 20)
        _fade(samples, rate, fade_in, fade_out)
        peak = float(np.max(np.abs(samples)))
        if normalize_db is not None and peak > 0:
            samples *= 10 ** (normalize_db / 20) / peak
        return self._write(output, samples, rate)

    def analyze_audio(self, source: str) -> dict[str, object]:
        """Measure a workspace PCM16 WAV: duration, rate, channels, peak/RMS dBFS,
        peak time, AC spectral centroid, stereo balance and full-scale sample count.
        Null dBFS/metrics mean silence. RMS is not LUFS; stereo_balance is RMS ratio.
        """
        samples, rate = self._read(source)
        peak = float(np.max(np.abs(samples)))
        power = np.sum(np.abs(np.fft.rfft(samples, axis=0)) ** 2, axis=1)
        power[0] = 0
        total_power = float(np.sum(power))
        frequencies = np.fft.rfftfreq(len(samples), 1 / rate)
        channel_rms = np.sqrt(np.mean(samples**2, axis=0))
        rms_sum = float(np.sum(channel_rms))
        return {
            "path": str(self._path(source)),
            "duration_seconds": len(samples) / rate,
            "sample_rate": rate,
            "channels": samples.shape[1],
            "frames": len(samples),
            "peak_dbfs": _db(peak),
            "rms_dbfs": _db(float(np.sqrt(np.mean(samples**2)))),
            "peak_time_seconds": round(int(np.argmax(np.max(np.abs(samples), axis=1))) / rate, 4) if peak else None,
            "spectral_centroid_hz": round(float(np.sum(frequencies * power) / total_power), 1) if total_power else None,
            "stereo_balance": (
                round(float((channel_rms[1] - channel_rms[0]) / rms_sum), 3)
                if samples.shape[1] == 2 and rms_sum
                else (0.0 if peak else None)
            ),
            "full_scale_samples": int(np.count_nonzero((samples <= -1) | (samples >= 32767 / 32768))),
        }
