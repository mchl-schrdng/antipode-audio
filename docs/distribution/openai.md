# OpenAI public directory readiness

**Not submitted.** Checked on 2026-11-13. The maintainer confirms no OpenAI
partner contact or local MCP allowlisting. Organization access and verified
publisher identity remain unconfirmed. No OpenAI approval or directory listing
is claimed.

This dossier uses [v0.1.2](https://github.com/mchl-schrdng/antipode-audio/releases/tag/v0.1.2),
at [commit ad2a6a3](https://github.com/mchl-schrdng/antipode-audio/commit/ad2a6a37d46352fe7e26b3aa25da0c582c621bf6),
as the released baseline. Its assets remain unchanged. The
[portable ZIP](https://github.com/mchl-schrdng/antipode-audio/releases/download/v0.1.2/antipode-portable-0.1.2.zip)
is available for existing local installations; it is **not a submission-ready
OpenAI archive**.

## Applicable route

Antipode requires a local stdio MCP process. OpenAI's
[desktop-only guide](https://developers.openai.com/plugins/deploy/desktop-only)
limits this submission route to approved partners and requires the submitting
organization to be allowlisted first. Approved local MCP packages use the
portal's **Skills only** ZIP route while retaining their MCP configuration. That
label does not mean removing the server. Directory installation is described for
the ChatGPT desktop app and locally executing threads.

An organization owner or member with **Apps Management Write** must submit under
a verified identity, which determines the displayed publisher. The GitHub handle
and manifest text do not establish verification. See
[submission access and identity](https://developers.openai.com/plugins/deploy/submission#confirm-access-and-publishing-identity).

No public local-MCP application form or eligibility email was found in the
reviewed documentation. The separate
[getting-help guidance](https://developers.openai.com/plugins/deploy/app-review#getting-help)
directs unanswered questions to OpenAI support. Ask how an independent publisher
obtains the appropriate contact; this is not a guaranteed application route.
No inquiry has been sent.

## Concrete readiness gaps

| Area | Observed state | Remaining work |
| --- | --- | --- |
| Local MCP eligibility | No partner contact or allowlisting | Obtain an eligibility decision for the submitting organization. |
| Publisher account | Organization, role and identity unconfirmed | Check Platform settings; keep account identifiers private. |
| Bundled execution | Source and lockfiles included; dependency payload absent | Agree runtime/platform requirements, then build a separate candidate. |
| Clean desktop behavior | Native Codex discovers five tools | Test actual ChatGPT desktop installation on every advertised platform/architecture. |
| Review materials | Draft scenarios below; no OpenAI walkthrough recording | Confirm applicable materials, execute cases and record evidence. |
| Portal checks | No upload or scan performed | Complete required scans, attestations and review after prerequisites are met. |

The [desktop-only packaging requirement](https://developers.openai.com/plugins/deploy/desktop-only#configure-a-local-mcp-server)
explicitly includes the server's dependencies. Inspection of the current portable
ZIP found 48 entries, 6,000,130 bytes, and no dependency payload. Its `mcp.json`
runs external `uv`, requests Python 3.12, and prepares packages from `uv.lock` in
`${PLUGIN_DATA}/venv`. An offline restart after a previous download does not
demonstrate a self-contained clean installation.

The dependency closure includes native components such as NumPy, pydantic-core
and cryptography. Confirm supported platforms, interpreter prerequisites,
writable data paths and permitted bootstrap downloads with OpenAI. Bundle the
agreed runtime and libraries with their licenses, then test without a development
checkout or prepared cache. A copied development virtual environment is not
evidence of a relocatable bundle.

The existing ZIP has the portable `plugin.json`, local `mcp.json`, skill,
relative branding paths and no lifecycle hooks or registered-app references.
Its listing lengths and category fit the published limits. Its square
320-by-320 SVG icon is an accepted format under the current
[submission error reference](https://developers.openai.com/plugins/deploy/submission-errors).
This is not portal validation. Recheck the future bundle against archive limits:
100 MB ZIP, 512 MiB extracted,
5,000 entries and 100 MiB per entry.

## Listing draft

| Field | Proposed value |
| --- | --- |
| Package identifier / display name | `antipode` / Antipode |
| Short description | Original sound, made locally. |
| Category | Developer Tools |
| Developer | The publisher name accepted by identity verification; not yet confirmed |
| Website | https://antipode.quest |
| Support | https://antipode.quest/support |
| Privacy | https://antipode.quest/privacy |
| Terms | https://antipode.quest/terms |
| Source | https://github.com/mchl-schrdng/antipode-audio |
| Logo and composer icon | `assets/brand/icon.svg` |
| Release baseline | `0.1.2`; choose a new candidate version when packaging changes are reviewed |

Proposed long description:

> Turn a sound idea into an editable recipe and a WAV. Antipode gives your agent
> twelve procedural voices, layered stereo synthesis, filters, saturation,
> delay, reverb and level analysis. Design notifications, impacts, glass textures
> and short atmospheres on your computer. The agent writes the recipe; Antipode
> calculates the sound with oscillators and seeded noise. No neural audio model,
> sample library or audio API is used. Renders are limited to 30 seconds and
> sixteen layers. Files stay in the configured local audio workspace, and
> existing outputs are never overwritten. Antipode does not provide voice
> cloning, transcription, streaming playback or a DAW. Your host agent may still
> send conversation and tool-result metadata to its provider.

Starter prompts, each under 128 characters:

- Create a deep breathing drone with glass accents.
- Design a short, warm notification sound.
- Turn a metallic hit into a spacious cinematic impact.

Add any prerequisites or downloads retained in the accepted candidate. Claim
offline first-run operation only after testing that exact artifact.

## Execution, data and tool declarations

Audio reads/writes stay in `~/.antipode/audio` by default, with no overwrites or
outside/symlinked audio paths. The host separately saves recipe JSON using its
own permissions. The engine has no network calls, telemetry or authentication;
current setup downloads come from `uv`. Paths and measurements reach the host,
and user-selected audio may contain personal data. Uninstallation preserves the
audio workspace. See the [full data boundaries](README.md#access-data-and-limitations).

All tools already declare titles and explicit MCP hints. Their justifications:

| Tool | Read-only | Destructive | Open-world | Reason |
| --- | --- | --- | --- | --- |
| `list_presets` | true | false | false | Returns the built-in voice catalog; no file changes or external access. |
| `generate_sound` | false | false | false | Creates a new WAV in the bounded workspace; existing files are preserved. |
| `render_recipe` | false | false | false | Creates a new stereo WAV from validated procedural layers; no external material is fetched. |
| `process_audio` | false | false | false | Reads a workspace WAV and creates a different output; preserves the input and any existing output. |
| `analyze_audio` | true | false | false | Reads one supported workspace WAV and returns measurements without changing it. |

Read-only tools declare `idempotentHint: true`; creation tools declare `false`.
OpenAI has not accepted these declarations. The [rights record](../rights.md)
documents licensing without promising trademark clearance or copyright rights.

## Draft reviewer scenarios

These five positive and three negative cases have **not** been run as a complete
directory-installed desktop session. The documentation specifies this case count
for MCP review, with the error reference describing remote-MCP requirements.
Confirm applicability to the approved local route. See
[review information](https://developers.openai.com/plugins/deploy/submission#automatically-provide-submission-and-review-information).

Use a fresh review workspace, or a new filename prefix for every run. Cases 4
and 5 depend on case 2. Host-prefixed tool names are acceptable. Record actual
calls and inspect the resulting files; an agent's success statement is not
sufficient.

| Positive case | Prompt | Expected tools and result |
| --- | --- | --- |
| Discover the instrument | Use Antipode to list its actual synthesis voices and explain which would suit a glass notification. Do not render yet. | `list_presets`; twelve named voices including `glass` and `chime`; no audio file created. |
| Render a source | Generate `review/openai/chime-01.wav` with preset `chime`, duration 1 second, frequency 660 Hz, level -12 dBFS and seed 13. Analyze it. | `generate_sound`, `analyze_audio`; a new 48,000-frame, mono, 48 kHz PCM16 WAV with no full-scale samples. |
| Render layered stereo | Read the bundled `examples/recipes/glass-orbit.json`, pass its JSON unchanged to Antipode, render `review/openai/glass-orbit-01.wav`, and analyze it. Save the recipe beside my deliverables. | Host file access, `render_recipe`, `analyze_audio`; eight-second stereo 48 kHz PCM16 WAV and the unchanged recipe saved by the host. |
| Refine without replacing | Reverse `review/openai/chime-01.wav`, add 0.02-second fade-in and 0.15-second fade-out, normalize to -6 dBFS, and save `review/openai/chime-reversed-01.wav`. Analyze the result. | `process_audio`, `analyze_audio`; input bytes unchanged, a separate mono WAV retaining rate/duration, peak approximately -6 dBFS within PCM16 rounding. |
| Measure without writing | Analyze `review/openai/chime-01.wav` and report duration, channels, peak and RMS dBFS. Do not change or create files. | `analyze_audio`; correct sample-level measurements; no file changes and no LUFS/true-peak claims. |

| Negative case | Prompt | Expected refusal, clarification or safe fallback |
| --- | --- | --- |
| Existing output | Overwrite `review/openai/chime-01.wav` with a different sound, using Antipode. | Explain that Antipode preserves existing files and request or offer a new filename. If attempted, the engine returns an error and original bytes stay unchanged. |
| Outside the workspace | Use Antipode to analyze `../../outside.wav` and save the result outside its audio workspace. | Reject the path or explain the workspace boundary; no outside file access and no attempt to bypass it with another tool. |
| Unsupported speech | Use Antipode to clone my voice from a recording and read this paragraph aloud. | Explain that Antipode has no voice-cloning or speech-synthesis capability; do not claim completion or invoke an unrelated audio render as speech. |

The [verification record](../verification.md) distinguishes native Codex tool
discovery from untested ChatGPT desktop installation and creative conversations.

## Next actions

1. Confirm the publisher account and request eligibility guidance through the
   documented support route; supply the organization ID privately.
2. Obtain allowlisting and clarify runtime/platform/review requirements.
3. Prepare and test a complete candidate without changing published v0.1.2 assets.
4. Upload, resolve findings and complete review. Approval and publication remain
   separate later steps.
