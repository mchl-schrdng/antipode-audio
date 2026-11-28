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

Give each layer exactly one source. Use `preset` for one of the 16 voices in `list_presets`. Use `material` for a resonating object excited by a gesture.

| Layer field | Range / default |
| --- | --- |
| `start` | Seconds, at least 0; default 0 |
| `duration` | At least 0.02 seconds; must fit the recipe |
| `frequency` / `note` | 20–8000 Hz or scientific pitch `E0`–`B8` (for example `A2`, `F#4`, `Eb3`); default 220 Hz; specify one |
| `frequency_end` / `note_end` | Optional ending pitch for an exponential glide on a preset other than `kick`, `noise` or `wind`. Material layers use fixed resonances |
| `level_db` | -60 to 0; default -12 (applied after layer filtering and re-normalization) |
| `pan`, `pan_end` | -1 left, 0 center, 1 right; `pan` defaults to 0, `pan_end` defaults to `pan` |
| `fade_in`, `fade_out` | Seconds; defaults 0.005 / 0.02, fitted to the layer |
| `highpass_hz`, `lowpass_hz` | Optional per-layer filter (0–10000 Hz and 20–20000 Hz; defaults 0 and 20000; filters that extinguish the voice are rejected) |
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

## Materials and gestures

A `metal` plate, `glass` vessel and `wood` block have different resonances and decay rates. Set `frequency` or `note` to choose the lowest resonance. Use `gesture: "strike"` (the default) for an impact, or `"rub"` to sustain friction over the layer. Both gestures excite the same body. Increase `damping` from 0 (freely ringing) toward 1 (firmly held) to shorten the tail, particularly its upper resonances. The default is 0.2. Both controls belong on `material` layers.

## Automation

Set `automation` on a layer to move one or more controls. Each curve takes 2–64 `[seconds, value]` pairs. Start at zero and use strictly increasing times up to the layer duration. The time origin moves with the layer's `start`. After the final point, the control holds its last value.

| Control | Values | Interpolation |
| --- | --- | --- |
| `level_db` | −60 to 0 dB | Linear in dB |
| `pan` | −1 (left) to 1 (right) | Linear in pan position with constant-power stereo gains |
| `lowpass_hz` | 20–20000 Hz, always above the layer's `highpass_hz` | Logarithmic in Hz, so equal time spans can cover equal numbers of octaves |

The automated low-pass uses a two-pole filter. At the same cutoff, its gentler roll-off lets more high frequencies through than the fixed spectral filter.

Specify a control once, either as a fixed value or as a curve. A pan curve also takes the place of `pan_end`. Fades and master effects still apply. This four-second breath opens, snaps shut, then brightens three more times.

```json
{
  "duration": 4,
  "seed": 8,
  "layers": [{
    "preset": "noise", "duration": 4, "highpass_hz": 60,
    "automation": {"lowpass_hz": [
      [0, 250], [1.4, 6800], [1.47, 320],
      [1.82, 1900], [2.1, 350], [2.48, 2600], [2.8, 400], [3.3, 3200], [3.9, 320]
    ]}
  }]
}
```

## Sound families

Save one JSON object with a complete `base` recipe and a `members` object keyed by cue name. An empty member plays the base exactly. A member can set a total `duration` and supply an `events` list to arrange a new sequence. Each of its 1–16 events plays a base layer by zero-based index. Repeat a layer for two strikes or include several at the same time.

```json
{
  "base": {"duration": 0.8, "seed": 21, "layers": [
    {"material": "glass", "gesture": "strike", "damping": 0.3, "note": "A4", "duration": 0.25}
  ]},
  "members": {
    "open": {},
    "alert": {"events": [
      {"layer": 0, "start": 0},
      {"layer": 0, "start": 0.36, "note": "C5", "fade_in": 0.02}
    ]}
  }
}
```

Each event inherits its source layer. It can override `start`, `duration`, `frequency` or `note`, `frequency_end` or `note_end` on supported presets, `level_db`, `pan`, `pan_end`, `fade_in`, `fade_out`, and `gesture` on materials. A new note replaces an inherited frequency and vice versa. Material, damping, filters, automation and master effects come from the base. A layer's explicit seed stays with it. Its default seed is the base seed plus the source index modulo 2³², so rearranging or repeating a layer preserves its random variations.

Member and event durations are measured in seconds. Changing a duration leaves the inherited event times, fade lengths and automation points at their original times. All events must fit the member duration. All points and combined fades must fit their event. Setting `level_db` or `pan` on an event replaces the corresponding inherited curve for that event. A `pan_end` override on its own starts the pan movement at the inherited curve's first value.

Pass the parsed object as `recipe` and select one name with the optional MCP argument `member`, for example `render_recipe(recipe=family, output="alert.wav", member="alert")`. The CLI accepts the same name with `--member`. Try `open`, `confirm` or `alert` from the bundled family.

```sh
uv run --locked antipode --workspace ./audio render examples/recipes/signal-box.family.json confirm.wav --member confirm
```
