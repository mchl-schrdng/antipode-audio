# Sound recipes

Call `render_recipe(recipe, output)` with a JSON object and a new relative `.wav` output name. The output is stereo 48 kHz PCM16. Durations include effect tails; leave room after the last event. Unknown keys are rejected.

```json
{
  "duration": 8,
  "seed": 73,
  "peak_db": -6,
  "layers": [
    {"preset": "drone", "duration": 7, "note": "A1", "level_db": -16, "fade_in": 1, "fade_out": 2, "lowpass_hz": 1200},
    {"preset": "glass", "start": 2, "duration": 4, "note": "A4", "level_db": -22, "pan": -0.4, "pan_end": 0.4}
  ],
  "effects": {"lowpass_hz": 6000, "reverb_mix": 0.3, "reverb_seconds": 2.4}
}
```

| Recipe field | Range / default |
| --- | --- |
| `duration` | 0.02–30 seconds |
| `seed` | Integer 0–4294967295 |
| `peak_db` | -60 to -1 dBFS; default -3 |
| `layers` | 1–16 layer objects |
| `effects` | Optional master effects object |

Each layer uses a `preset` from `list_presets`: `tone`, `chime`, `kick`, `noise`, `sweep`, `drone`, `pad`, `metal`, `riser`, `pulse`, `glass`, or `wind`.

| Layer field | Range / default |
| --- | --- |
| `start` | Seconds, at least 0; default 0 |
| `duration` | At least 0.02 seconds; must fit the recipe |
| `frequency` / `note` | 20–8000 Hz or scientific pitch `C0`–`B8` (for example `A2`, `F#4`, `Eb3`); default 220 Hz |
| `frequency_end` / `note_end` | Optional ending pitch for linear pitch glides |
| `level_db` | -60 to 0; default -12 |
| `pan`, `pan_end` | -1 left, 0 center, 1 right; `pan` defaults to 0, `pan_end` defaults to `pan` |
| `fade_in`, `fade_out` | Seconds; defaults 0.005 / 0.02, fitted to the layer |
| `highpass_hz`, `lowpass_hz` | Optional per-layer filter (0–10000 Hz and 20–20000 Hz; defaults 0 and 20000) |
| `seed` | Optional integer override |

| Effect field | Range / default |
| --- | --- |
| `highpass_hz` | 0–10000 Hz (0 bypass); default 0, must stay below lowpass |
| `lowpass_hz` | 20–20000 Hz; default 20000 |
| `drive` | 1–12; default 1 |
| `delay_seconds` | 0.01–2; default 0.375 |
| `delay_feedback` | 0–0.85; default 0.35 |
| `delay_mix` | 0–1; default 0 |
| `reverb_seconds` | 0.1–5; default 1.8 |
| `reverb_mix` | 0–1; default 0 |

The final mix is peak-normalized to `peak_db`; adjust relative layer levels for balance. For independent alternatives, keep the recipe and seed and change a deliberate parameter. Export each variant under a fresh filename.
