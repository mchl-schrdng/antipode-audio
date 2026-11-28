"""Damped modal bodies excited by an impact or by sustained sliding contact."""

import numpy as np

from antipode.synthesis import SAMPLE_RATE, fade


# (Free decay rate per second, (relative frequency, amplitude) modes).
# These are procedural approximations of a plate, a hollow glass and a wood block.
_BODIES = {
    "metal": (1.5, ((1., 1.), (1.51, .74), (2.24, .52), (3.18, .37), (4.61, .29), (6.87, .17))),
    "glass": (1.15, ((1., 1.), (2.68, .56), (4.83, .28), (7.51, .16), (9.42, .09))),
    "wood": (12., ((1., 1.), (2.57, .62), (4.64, .34), (6.31, .17))),
}


def validate_material(material: str, gesture: str, damping: float) -> None:
    if not isinstance(material, str) or material not in _BODIES:
        raise ValueError(f"material must be one of: {', '.join(_BODIES)}.")
    if gesture not in ("strike", "rub"):
        raise ValueError("gesture must be strike or rub.")
    if type(damping) not in (int, float) or not 0 <= damping <= 1:
        raise ValueError("damping must be finite and between 0 and 1.")


def synthesize_material(
    material: str, gesture: str, damping: float, duration: float, frequency: float, seed: int
) -> np.ndarray:
    """Return a peak-normalized mono voice from validated layer parameters.

    Frequency sets the lowest mode. Damping adds contact loss to the same
    modes, increasingly attenuating the upper resonances when held.
    """
    frames = round(duration * SAMPLE_RATE)
    random = np.random.default_rng(seed)
    free_loss, modes = _BODIES[material]
    loss = free_loss + 24 * damping**1.5
    # End the impulse once even the longest mode has decayed by over 80 dB.
    impulse_frames = min(frames, int(np.ceil(10 * SAMPLE_RATE / loss)))
    time = np.arange(impulse_frames) / SAMPLE_RATE
    impulse = np.zeros(impulse_frames)
    for ratio, amplitude in modes:
        mode_hz = ratio * frequency
        if mode_hz < .45 * SAMPLE_RATE:
            mode_loss = loss * (1 + (.2 + .4 * damping) * (ratio - 1))
            # The point of contact changes how strongly each mode is excited.
            strength = amplitude * random.uniform(.82, 1.18)
            impulse += strength * np.exp(-mode_loss * time) * np.sin(2 * np.pi * mode_hz * time)

    if gesture == "strike":
        signal = np.zeros(frames)
        signal[:impulse_frames] = impulse
        # Brief skin/surface contact precedes the freely decaying resonance.
        contact_frames = min(frames, round(.025 * SAMPLE_RATE))
        contact_time = np.arange(contact_frames) / SAMPLE_RATE
        contact = random.uniform(-1, 1, contact_frames) * np.exp(-260 * contact_time)
        signal[:contact_frames] += .23 * np.convolve(contact, [.25, .5, .25], mode="same")
    else:
        # A moving contact supplies irregular pulses of friction. Changes in
        # pressure affect the noise and the vibration it drives in the body.
        time = np.arange(frames) / SAMPLE_RATE
        knots = np.arange(0, duration + .075, .075)
        pressure = np.interp(time, knots, random.uniform(.35, 1., len(knots)))
        slip_phase = np.cumsum(2 * np.pi * (35 + 95 * pressure) / SAMPLE_RATE)
        grain = .25 + .75 * (.5 + .5 * np.cos(slip_phase))**4
        excitation = random.standard_normal(frames) * pressure * grain
        rise = min(.1, duration / 3)
        release = min(.14, duration / 3)
        excitation *= np.minimum(time / rise, 1) * np.minimum((duration - time) / release, 1)
        fft_size = 1 << (frames + impulse_frames - 2).bit_length()
        spectrum = np.fft.rfft(excitation, n=fft_size)
        spectrum *= np.fft.rfft(impulse, n=fft_size)
        signal = np.fft.irfft(spectrum, n=fft_size)[:frames] / np.sqrt(.03 * SAMPLE_RATE)
        signal += .18 * np.convolve(excitation, [.25, .5, .25], mode="same")

    samples = signal[:, None]
    fade(samples, SAMPLE_RATE, min(.001, duration / 4), min(.012, duration / 4))
    peak = np.max(np.abs(samples))
    return samples / peak if peak else samples
