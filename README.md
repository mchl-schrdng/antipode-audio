<p align="center">
  <img src="assets/brand/github-cover.svg" alt="Antipode — sound, on the other side of words" width="100%">
</p>

<p align="center">
  <strong>Sound creation for AI coding agents.</strong><br>
  An instrument inside your agent. A sound on your disk.
</p>

<p align="center">
  <a href="https://antipode.quest">Listening room</a> ·
  <a href="#get-started">Install</a> ·
  <a href="docs/integrations.md">Connect your agent</a> ·
  <a href="docs/rights.md">Rights & provenance</a>
</p>

<p align="center">
  <a href="https://github.com/mchl-schrdng/antipode-audio/actions/workflows/check.yml"><img src="https://github.com/mchl-schrdng/antipode-audio/actions/workflows/check.yml/badge.svg" alt="Linux, macOS and Windows checks"></a>
</p>

---

Describe a texture, a gesture, an atmosphere. Your agent turns it into a recipe;
Antipode synthesizes it locally and exports a WAV you can keep refining.

> A low, slowly breathing drone. Brittle glass moving left to right.
> A distant metallic impact that dissolves into space. Ten seconds.

**Local DSP. Open source. No sample library. No model weights.**

Antipode is a Python CLI and an MCP instrument with agent skills and installation
configurations for **Codex, Claude Code, Antigravity and OpenCode**. It is an early
release; see the [verification record](docs/verification.md) for what has actually
been tested in each host. It is not a VST/AU instrument or a neural text-to-music
model.

## Start listening

Three original studies, made entirely by the included engine. Each has an editable
recipe; no recording was sampled.

| Study | Sound | Recipe |
| --- | --- | --- |
| **Event Horizon** | [Listen / download WAV](examples/audio/event-horizon.wav) | [Rebuild it](examples/recipes/event-horizon.json) |
| **Glass Orbit** | [Listen / download WAV](examples/audio/glass-orbit.wav) | [Rebuild it](examples/recipes/glass-orbit.json) |
| **Afterimage** | [Listen / download WAV](examples/audio/afterimage.wav) | [Rebuild it](examples/recipes/afterimage.json) |

Visit the live listening room at [antipode.quest](https://antipode.quest).
Its deployment source is maintained separately from this public instrument repository.

## Get started

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Git, then:

```sh
git clone https://github.com/mchl-schrdng/antipode-audio.git
cd antipode-audio
uv sync --locked --python 3.12
uv run antipode generate first-light.wav --preset chime --duration 2
```

The command writes `audio/first-light.wav` and prints measurements as JSON. Choose
a new filename for each render; existing files are never replaced. `--workspace`
selects a different audio directory and goes before the subcommand.

```sh
uv run antipode --workspace ./my-sounds presets
uv run antipode --workspace ./my-sounds generate soft-glass.wav --preset glass --frequency 440
uv run antipode --workspace ./my-sounds process soft-glass.wav soft-glass-reversed.wav --reverse --fade-out 0.4
uv run antipode --workspace ./my-sounds analyze soft-glass-reversed.wav
uv run antipode --workspace ./my-sounds render examples/recipes/event-horizon.json event-horizon.wav
```

There is no published PyPI installation assumed by these instructions. Install
from this source checkout. After dependencies are prepared, the audio engine works
offline. Your host agent may still use a cloud model for conversation.

## Give your agent an instrument

Use the [integration guide](docs/integrations.md) for the appropriate plugin or
MCP-plus-skill installation. Antipode exposes one shared toolset:

| Tool | What it does |
| --- | --- |
| `list_presets` | Discover the available synthesis voices |
| `generate_sound` | Render one source with a controlled pitch, duration and level |
| `render_recipe` | Arrange layered stereo sound with effects |
| `process_audio` | Refine a local WAV while preserving the source |
| `analyze_audio` | Measure duration, sample rate, peak and RMS levels |

The client starts `antipode-mcp` as a local stdio process. No hosted MCP server,
account, API key or always-on daemon is needed by Antipode. Use separate output
names when several agents work in the same workspace.

## The instrument

Twelve procedural voices: tone, chime, kick, noise, sweep, drone, pad, metal, riser,
pulse, glass and wind. Combine them with offsets, stereo positioning, envelopes,
filters, saturation, delay and reverb. Recipes are plain JSON, reviewable alongside
your code.

Generated files use 48 kHz, 16-bit PCM WAV. Rendering is bounded to 30 seconds and
16 layers per recipe. Existing WAV processing accepts supported mono/stereo PCM16
files. No MP3 conversion, voice cloning or model download is included. See CLI help
and the integration skill for exact parameters.

```text
Your brief → coding agent → local MCP → DSP recipe → WAV
```

## Rights, without hand-waving

Code and original artwork: **Apache-2.0**. Bundled demo recordings and recipes:
**CC0-1.0**, to the extent the contributors hold rights. Antipode claims no royalty
or ownership over your rendered audio. User-provided material remains subject to
its existing rights.

No universal copyright or trademark clearance is promised. In particular, the
working name **Antipode has not been legally cleared**; the preliminary review
records similar names already used in audio. Read [rights and provenance](docs/rights.md)
and [third-party notices](THIRD_PARTY_NOTICES.md) before commercial distribution.

## Develop

```sh
uv run python -m unittest discover -s tests -v
uv build
```

[`src/antipode`](src/antipode) holds the shared engine and transports;
[`skills/antipode`](skills/antipode) teaches the creative workflow;
[`tests`](tests) exercises audio behavior, file boundaries, CLI and MCP.

See [contributing](CONTRIBUTING.md), [security](SECURITY.md) and
[the verification record](docs/verification.md). English throughout.
