"""Layer-local breakpoint curves and a continuously variable low-pass filter."""

import numpy as np

from antipode.synthesis import SAMPLE_RATE


_BOUNDS = {"level_db": (-60, 0), "pan": (-1, 1), "lowpass_hz": (20, 20_000)}


def validate_automation(layer: dict, duration: float) -> dict:
    """Validate JSON curves before rendering. The layer's scalar controls are already validated."""
    if "automation" not in layer:
        return {}
    curves = layer["automation"]
    if not isinstance(curves, dict) or not curves or curves.keys() - _BOUNDS.keys():
        raise ValueError("automation must contain curves for level_db, pan, or lowpass_hz.")
    for name, points in curves.items():
        if name in layer or (name == "pan" and "pan_end" in layer):
            raise ValueError(f"automation.{name} conflicts with a static control for the same parameter.")
        if not isinstance(points, list) or not 2 <= len(points) <= 64:
            raise ValueError(f"automation.{name} requires 2–64 [time, value] points.")
        low, high = _BOUNDS[name]
        previous = -1
        for index, point in enumerate(points):
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError(f"automation.{name} points must be [time, value] pairs.")
            time, value = point
            if type(time) not in (int, float) or not previous < time <= duration or (index == 0 and time != 0):
                raise ValueError(f"automation.{name} times must start at 0 and increase within the layer duration.")
            if type(value) not in (int, float) or not low <= value <= high:
                raise ValueError(f"automation.{name} values must be finite and between {low} and {high}.")
            if name == "lowpass_hz" and value <= layer.get("highpass_hz", 0):
                raise ValueError("automation.lowpass_hz must stay above the layer's highpass_hz.")
            previous = time
    return curves


def curve_values(points: list, frames: int, *, logarithmic: bool = False, rate: int = SAMPLE_RATE) -> np.ndarray:
    """Interpolate at sample times and hold the last value through the layer end."""
    times, values = np.asarray(points, dtype=np.float64).T
    positions = np.arange(frames)
    if logarithmic:
        return np.exp(np.interp(positions, times * rate, np.log(values)))
    return np.interp(positions, times * rate, values)


def swept_lowpass(voice: np.ndarray, points: list, rate: int = SAMPLE_RATE) -> np.ndarray:
    """Filter mono audio with two cascaded one-pole sections and a log-frequency cutoff curve."""
    frames = len(voice)
    cutoff = curve_values(points, frames, logarithmic=True, rate=rate)
    # Choose each digital pole so that the cascaded filter is -3 dB at the stated cutoff.
    difference = 2 * np.sin(np.pi * cutoff / rate)**2 / (np.sqrt(2) - 1)
    pole = 1 / (1 + difference + np.sqrt(difference * (difference + 2)))

    # For y[n] = (1-p[n])*x[n] + p[n]*y[n-1], division by the running product
    # of p turns the recurrence into a cumulative sum. Restart the product every
    # 64 samples to keep it representable even with the filter fully open.
    width = 64
    pad = (-frames) % width
    poles = np.pad(pole, (0, pad), mode="edge").reshape(-1, width)
    decay = np.cumprod(poles, axis=1)
    drive = (1 - poles) / decay
    output = np.pad(voice[:, 0], (0, pad)).reshape(-1, width)
    for _ in range(2):
        output *= drive
        np.cumsum(output, axis=1, out=output)
        output *= decay
        # Carry the previous block's final sample into this block for continuous state.
        ends = output[:, -1].copy()
        for block in range(1, len(ends)):
            ends[block] += decay[block, -1] * ends[block - 1]
        output[1:] += decay[1:] * ends[:-1, None]
    return output.reshape(-1, 1)[:frames]
