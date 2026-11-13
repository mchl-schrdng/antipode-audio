# Distribution kit

Current release package: [Antipode v0.1.2](https://github.com/mchl-schrdng/antipode-audio/releases/tag/v0.1.2).
This directory records listing copy, reproducible bundles and a review procedure.
On 2026-11-13, [Antipode 0.1.2 was submitted to Claude](claude.md) for Claude Code
only, then refused by the directory's automated checks at commit `cba7f25`.
The current status is **Needs changes**: the portal requires a Verified
organization for local MCP and restricts executable content and bundled file
types. There is no approval or public listing. The complete plugin remains
available through this repository's own marketplace and release downloads.
Google's [Antigravity interest form](antigravity.md) submission remains confirmed
for the historical v0.1.1 package; no marketplace approval is recorded.

The [Gemini CLI extension](gemini.md) is distributed from this repository, with
gallery discovery tracked separately. The [OpenAI readiness dossier](openai.md)
records the local-MCP partner eligibility and packaging requirements that remain
before a public-directory submission. No OpenAI submission or approval is claimed.

## Public details

| Field | Value |
| --- | --- |
| Name / identifier | Antipode / `antipode` |
| Website | https://antipode.quest |
| Source | https://github.com/mchl-schrdng/antipode-audio |
| Documentation | https://github.com/mchl-schrdng/antipode-audio/blob/main/docs/integrations.md |
| Support | https://antipode.quest/support |
| Privacy | https://antipode.quest/privacy |
| Terms | https://antipode.quest/terms |
| Code and original artwork | Apache-2.0; see the bundled LICENSE and NOTICE |
| Demo WAVs and recipes | CC0-1.0, to the extent contributors hold rights |
| Publisher in the source manifest | Antipode contributors |

### Short description

Create original sound effects and layered atmospheres locally with your coding
agent. Procedural synthesis, editable recipes, and WAV export.

### Listing description

Turn a sound brief into a file you can keep refining. Antipode gives your coding
agent a local instrument with twelve procedural voices, layered stereo recipes,
filters, saturation, delay and reverb. Make a notification, a cinematic impact, a
glass texture or a short ambient study. Keep the recipe alongside the WAV.

The coding agent writes the recipe; Antipode calculates the sound using
oscillators, envelopes, seeded noise and digital signal processing. The audio
engine contains no neural audio model, model weights, sampled recordings or
voice-cloning system. It exposes five MCP tools: discover presets, generate a
source, render a layered recipe, process a WAV, and measure its levels.

Antipode runs on your computer over MCP stdio. Install `uv` first; initial startup
may download Python 3.12 and the locked Python dependencies. There is no Antipode
account, API key, subscription, GPU requirement or hosted MCP service. Sound
creation works offline after setup, while your coding agent may still use a cloud
model. This early release creates short sounds up to 30 seconds, with up to 16
layers. It is not a DAW, a VST/AU instrument, speech synthesis or a text-to-music
model.

## Access, data and limitations

- **Local execution:** Claude and Gemini CLI start `uv run --locked` against the bundled
  `scripts/claude_mcp.py`, whose adjacent lockfile pins its script environment.
  Other hosts use the bundled Python project and `uv.lock`. `uv` prepares Python and dependencies as needed, using its
  configured download sources and cache. This first-run software download is not
  an audio upload. Antipode's engine makes no network calls and has no telemetry,
  remote MCP endpoint, authentication flow or listening HTTP port.
- **Files:** the shipped MCP configuration uses `~/.antipode/audio`. Generation
  and processing create new WAV files there, including requested subdirectories.
  They refuse to replace existing files. Analysis and processing read supported
  WAVs within that workspace. Absolute paths, traversal and symlinked audio paths
  are rejected. Use a trusted local directory; this is an application boundary,
  not an operating-system sandbox against another process changing files.
- **Other writes:** Claude and Gemini CLI dependencies and their script environments live in
  `uv`'s cache. Other hosts use their writable plugin-data virtual environment.
  uv may also create a managed Python installation. The skill asks
  the coding agent to save the recipe using its own file tool. That host action
  has the host's permissions, separately from the MCP audio workspace.
- **Data handling:** Antipode may process user-selected audio that contains
  personal data. It does not scan unrelated documents or accounts. MCP replies
  include filenames, absolute output paths and measurements; these reach the
  host agent and can reveal local path information. Audio is not transmitted by
  the MCP engine. A user can separately ask the host to attach or share a file,
  subject to that host's behavior and privacy settings.
- **Retention:** local audio remains until the user deletes it. Antipode has no
  server-side storage, automatic upload or automatic retention/deletion service.
  Uninstalling the plugin does not delete the external audio workspace. Host
  conversation retention and dependency caches are separate.
- **Formats:** new sound uses 48 kHz PCM16 WAV; layered rendering is stereo.
  Processing/analysis accept mono or stereo PCM16 WAV at 8–48 kHz, at most 30
  seconds and 8 MiB. Recipe files read by the CLI are limited to 64 KiB. No MP3,
  MIDI, streaming playback, LUFS or true-peak metering is provided.
- **Rights:** the project claims no royalty or ownership over users' renders.
  User-provided material keeps its existing rights. No exclusive rights,
  copyright eligibility, trademark clearance or provider certification is
  promised. The working name has not been legally cleared. Read the
  [rights record](../rights.md) and [third-party notices](../../THIRD_PARTY_NOTICES.md).

## Reproducible plugin archives

Release assets are fixed to their Git tag. Build from `v0.1.2` to reproduce the
current package; later documentation updates on `main` do not change those assets.
The historical Google submission continues to reference its original v0.1.1 package.

Use Python 3.11+ from a reviewed source checkout. The builder requires every
allowlisted file to be tracked in Git, including newly staged files. It reads
those files' working-tree contents; commit the reviewed changes before publishing
an artifact tied to a release. A ZIP is a plugin bundle, separate from the Python
wheel produced by `uv build`.

```sh
python3 scripts/build_plugin.py
python3 scripts/build_plugin.py --client antigravity
```

Outputs are `dist/antipode-portable-0.1.2.zip` and
`dist/antipode-antigravity-0.1.2.zip`, each with a `.zip.sha256` sidecar. Both contain
readable engine source, locked dependencies' metadata, manifests, skills,
artwork, licenses, documentation, recipes and demo WAVs. Dependencies themselves
are downloaded at setup. The explicit file list excludes Git internals, virtual
environments, caches, credentials, generated output and the separate website
source, even if an unrelated file is tracked.

Entries have a stable order, timestamp and permissions. ZIP entries are stored
without compression so identical source bytes produce identical ZIP bytes across
compression-library versions. Python scripts have mode 0755; lockfiles have mode
0644. The Google variant replaces root `plugin.json` with `integrations/antigravity.plugin.json` and omits `mcp.json`;
its native server declaration is `mcp_config.json`. Other payload files are the
same. SHA-256 identifies the bytes; it is not a signature or a vendor endorsement.

Verify a download before extracting it:

```sh
cd dist
shasum -a 256 -c antipode-portable-0.1.2.zip.sha256
shasum -a 256 -c antipode-antigravity-0.1.2.zip.sha256
```

## Reviewer walkthrough

1. Read the integration and rights documents, inspect the manifest/server
   configuration, and install `uv` on the host application's PATH.
2. Extract the appropriate archive into an empty folder. Follow its provider
   dossier to validate and load the plugin. First startup may download software;
   subsequent offline operation requires that prepared Python/dependency cache.
3. Confirm the five tools are discovered. Call `list_presets`; expect twelve
   voices. Try the prompts below and check the actual output with `analyze_audio`.
   Use fresh filenames on repeated runs.
4. Confirm generation creates a local WAV, processing preserves its input, and
   reusing an existing output name fails without replacing its bytes. The
   [verification record](../verification.md) states the tests already performed
   and the limits of native-host testing.

### Three reproducible studies

The checked-in recipe is the exact reference for each study. A free-form agent
interpretation can differ; use the recipe unchanged to reproduce the demo.

| Study | Suggested prompt | Reference recipe |
| --- | --- | --- |
| Event Horizon | Use Antipode to make a ten-second, slowly breathing low drone with glass accents and a distant metallic detail. For the reference version, read the bundled Event Horizon recipe, pass its JSON unchanged to `render_recipe`, write `review/event-horizon-01.wav`, then analyze it. | [event-horizon.json](../../examples/recipes/event-horizon.json) |
| Glass Orbit | Use Antipode to make an eight-second glass texture moving across the stereo field, with sparse bright hits and a long soft space. For the reference version, read the bundled Glass Orbit recipe, pass its JSON unchanged to `render_recipe`, write `review/glass-orbit-01.wav`, then analyze it. | [glass-orbit.json](../../examples/recipes/glass-orbit.json) |
| Afterimage | Use Antipode to make a ten-second rising tension cue that lands in a deep cinematic impact and fades into metallic air. For the reference version, read the bundled Afterimage recipe, pass its JSON unchanged to `render_recipe`, write `review/afterimage-01.wav`, then analyze it. | [afterimage.json](../../examples/recipes/afterimage.json) |

The same review is available without a model account, from the extracted folder:

```sh
uv run --locked --python 3.12 antipode --workspace ./review-audio render examples/recipes/event-horizon.json event-horizon-01.wav
uv run --locked --python 3.12 antipode --workspace ./review-audio render examples/recipes/glass-orbit.json glass-orbit-01.wav
uv run --locked --python 3.12 antipode --workspace ./review-audio render examples/recipes/afterimage.json afterimage-01.wav
uv run --locked --python 3.12 antipode --workspace ./review-audio analyze glass-orbit-01.wav
```

Expected: 10, 8 and 10 seconds respectively, stereo, 48 kHz PCM16, valid measurements
and no overwritten file. These commands use a writable review folder; host plugin
launches keep their environment outside the installed source.
