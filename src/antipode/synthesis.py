"""Procedural oscillators and bounded effects; no recordings or model weights."""

import numpy as np

SAMPLE_RATE = 48_000
PRESETS = {
    "tone": "Pure sine; frequency sets pitch. Useful for sub layers and clean UI tones.",
    "chime": "Three decaying harmonic partials; frequency sets the fundamental.",
    "kick": "A deep sine falling to a quarter of the starting frequency. Try 180 Hz.",
    "noise": "Seeded white noise; frequency is ignored.",
    "sweep": "A sine rising from half frequency to frequency.",
    "drone": "Slowly beating subharmonics, detuned overtones and gentle FM. Try 55–110 Hz.",
    "pad": "Soft evolving detuned harmonics with a slow bloom. Try 110–440 Hz.",
    "metal": "Inharmonic struck resonators and a noisy attack. Try 90–500 Hz.",
    "riser": "An accelerating tonal rise through filtered air. Try 220–2000 Hz.",
    "pulse": "Warm breathing harmonic pulses at 2.5 Hz. Try 55–220 Hz.",
    "glass": "Delicate inharmonic glass resonances with a long decaying shimmer. Try 440–1200 Hz.",
    "wind": "Slowly swelling dark filtered noise. Frequency sets the spectral centre.",
}


def fade(samples: np.ndarray, rate: int, fade_in: float, fade_out: float) -> None:
    for seconds, at_end in ((fade_in, False), (fade_out, True)):
        count = round(seconds * rate)
        if count:
            ramp = np.linspace(0, 1, count)[:, None]
            if at_end:
                samples[-count:] *= ramp[::-1]
            else:
                samples[:count] *= ramp


def synthesize(preset: str, duration: float, frequency: float, seed: int) -> np.ndarray:
    """Return a peak-normalized mono voice. Caller validates the public parameters."""
    time = np.arange(round(duration * SAMPLE_RATE)) / SAMPLE_RATE
    position = time / duration
    phase = 2 * np.pi * frequency * time
    random = np.random.default_rng(seed)

    def partial(ratio: float, offset: float = 0) -> np.ndarray:
        if frequency * ratio >= SAMPLE_RATE * 0.45:
            return np.zeros_like(time)
        return np.sin(phase * ratio + offset)

    if preset == "tone":
        signal = np.sin(phase)
    elif preset == "chime":
        signal = sum(
            amplitude * partial(ratio) * np.exp(-decay * position)
            for ratio, amplitude, decay in ((1, 1, 5), (1.5, 0.4, 7), (2.01, 0.2, 10))
        )
    elif preset == "kick":
        decay = 25 / duration
        kick_phase = 2 * np.pi * frequency * (
            0.25 * time + 0.75 * (1 - np.exp(-decay * time)) / decay
        )
        signal = np.sin(kick_phase) * np.exp(-8 * position)
    elif preset == "noise":
        signal = random.uniform(-1, 1, len(time))
    elif preset == "sweep":
        signal = np.sin(2 * np.pi * (frequency / 2 * time + frequency / (4 * duration) * time**2))
    elif preset == "drone":
        signal = 0.65 * partial(0.5) + 0.3 * np.sin(phase + 0.7 * np.sin(2 * np.pi * 0.13 * time))
        for ratio, amplitude in ((1.003, 0.22), (1.5, 0.15), (2.002, 0.08), (3, 0.04)):
            signal += amplitude * partial(ratio, random.uniform(0, 2 * np.pi))
        signal *= (0.8 + 0.2 * np.sin(2 * np.pi * 0.17 * time)) * np.sin(np.pi * position)**0.35
    elif preset in ("pad", "pulse"):
        signal = np.zeros_like(time)
        for harmonic in range(1, 9):
            brightness = 0.65 + 0.35 * np.sin(2 * np.pi * 0.09 * time + harmonic / 3)
            signal += brightness / harmonic**1.7 * (
                partial(harmonic * 0.9983, random.uniform(0, 2 * np.pi))
                + partial(harmonic * 1.0017, random.uniform(0, 2 * np.pi))
            )
        if preset == "pulse":
            signal *= (0.5 - 0.5 * np.cos(2 * np.pi * 2.5 * time))**2
        else:
            signal *= np.sin(np.pi * position)**0.5
    elif preset in ("metal", "glass"):
        signal = np.zeros_like(time)
        ratios = (1, 1.414, 2.371, 3.817, 5.193, 7.011)
        for index, ratio in enumerate(ratios):
            decay = (2.5 if preset == "glass" else 6) + index * 1.4
            signal += partial(ratio) / (index + 1)**1.1 * np.exp(-decay * position)
        if preset == "metal":
            signal += random.uniform(-1, 1, len(time)) * np.exp(-100 * time) * 0.12
    elif preset == "riser":
        sweep_phase = 2 * np.pi * frequency * duration * (0.125 * position + 0.875 / 3 * position**3)
        air = random.uniform(-1, 1, len(time))
        air = spectral_filter(air[:, None], 500, 9000)[:, 0]
        signal = (0.55 * np.sin(sweep_phase) + 0.3 * np.sin(1.003 * sweep_phase) + 0.45 * air)
        signal *= position**1.5
    elif preset == "wind":
        signal = spectral_filter(random.uniform(-1, 1, len(time))[:, None], 40, min(12000, frequency * 4))[:, 0]
        signal *= (0.65 + 0.35 * np.sin(2 * np.pi * 0.21 * time)) * np.sin(np.pi * position)**0.6
    else:
        raise ValueError(f"Unknown preset: {preset}.")
    samples = signal[:, None]
    fade(samples, SAMPLE_RATE, min(0.005, duration / 4), min(0.02, duration / 4))
    peak = np.max(np.abs(samples))
    return samples / peak if peak else samples


def spectral_filter(samples: np.ndarray, highpass: float, lowpass: float) -> np.ndarray:
    """Smooth spectral roll-off; padding prevents an end transient wrapping to the start."""
    size = 1 << (2 * len(samples) - 1).bit_length()
    frequencies = np.fft.rfftfreq(size, 1 / SAMPLE_RATE)
    response = 1 / np.sqrt(1 + (frequencies / lowpass)**8)
    if highpass:
        response *= frequencies**2 / np.sqrt(frequencies**4 + highpass**4)
    spectrum = np.fft.rfft(samples, n=size, axis=0)
    return np.fft.irfft(spectrum * response[:, None], n=size, axis=0)[:len(samples)]


def effects(samples: np.ndarray, options: dict, seed: int) -> np.ndarray:
    """Master chain: spectral shaping, drive, stereo delay, diffused reverb."""
    highpass = options.get("highpass_hz", 0)
    lowpass = options.get("lowpass_hz", 20000)
    if highpass or lowpass != 20000:
        samples = spectral_filter(samples, highpass, lowpass)
    drive = options.get("drive", 1)
    if drive > 1:
        samples = np.tanh(samples * drive) / np.tanh(drive)
    delay_mix = options.get("delay_mix", 0)
    if delay_mix:
        step = round(options.get("delay_seconds", 0.375) * SAMPLE_RATE)
        feedback = options.get("delay_feedback", 0.35)
        dry = samples.copy()
        wet = np.zeros_like(samples)
        # shortcut: 12 echoes bound render time; use a streaming delay for long-form audio.
        for repeat in range(1, min(12, (len(samples) - 1) // step) + 1):
            offset = repeat * step
            wet[offset:] += dry[:-offset, ::-1 if repeat % 2 else 1] * feedback**(repeat - 1)
        samples = (1 - delay_mix) * dry + delay_mix * wet
    reverb_mix = options.get("reverb_mix", 0)
    if reverb_mix:
        length = round(options.get("reverb_seconds", 1.8) * SAMPLE_RATE)
        time = np.arange(length) / SAMPLE_RATE
        random = np.random.default_rng(seed)
        impulse = random.normal(0, 1, (length, 2)) * np.exp(-6 * time[:, None] / (length / SAMPLE_RATE))
        impulse[:round(0.018 * SAMPLE_RATE)] = 0
        impulse = spectral_filter(impulse, 120, 6000)
        impulse /= np.sqrt(np.sum(impulse**2, axis=0))[None, :]
        size = 1 << (len(samples) + length - 2).bit_length()
        wet = np.fft.irfft(
            np.fft.rfft(samples, n=size, axis=0) * np.fft.rfft(impulse, n=size, axis=0), n=size, axis=0
        )[:len(samples)]
        samples = (1 - reverb_mix) * samples + reverb_mix * wet
    return samples
