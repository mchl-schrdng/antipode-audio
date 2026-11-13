# Antigravity Marketplace submission dossier

Prepared 2026-11-13 for Antipode 0.1.1. This is a ready-to-review package and listing
draft, not a claim of Marketplace acceptance or publication.

## Route and package

Google's [plugin authoring guide](https://antigravity.google/docs/build-plugins)
directs publishers to its [Marketplace partner intake form](https://forms.gle/2EX5RFYPoJe1UgxR9).
It calls for a complete manifest, README, bundled square logo, suggested prompts
and local strict validation. Submission and acceptance are separate from local
installation.

| Field | Proposed value |
| --- | --- |
| Product / identifier | Antipode / `antipode` |
| Version | `0.1.1` |
| Website | `https://antipode.quest` |
| Public source | `https://github.com/mchl-schrdng/antipode-audio` |
| Native artifact | `antipode-antigravity-0.1.1.zip`, with its SHA-256 sidecar |
| Native manifest source | `integrations/antigravity.plugin.json` |
| Description and suggested prompts | [Shared distribution kit](README.md) |
| Logo | Bundled square SVG, declared in the native manifest |
| Publisher/contact | Verified account-owner details; not invented by this draft |

Use the Google-specific archive for review. Its root `plugin.json` is the native
Google manifest and its server configuration is `mcp_config.json`. The source
repository's root manifest follows the portable Agent Plugins schema; the build
script makes the provider-specific projection explicitly. It does not change the
engine, license, skill or dependency lock.

## Local reviewer steps

Verify the artifact's checksum and extract it to an empty folder. With `uv` on the
application's PATH, run from the parent directory:

```sh
agy plugin validate --strict ./antipode
agy plugin install ./antipode
agy plugin list --json
```

Start a new agent session, invoke the Antipode skill, confirm the five MCP tools,
and run the three [demo prompts](README.md#three-reproducible-studies). The launcher
may download Python 3.12 and locked dependencies on first use; the environment
resides in the host's writable plugin-data directory. Rendered WAVs go to
`~/.antipode/audio`, outside the installed plugin, with no overwrites.

## Reviewer notes

Antipode is local procedural sound design. The coding agent creates a recipe;
oscillators, seeded noise and digital signal processing produce the audio. There
is no hosted service, neural audio model, model weight download, sample library,
voice cloning or Antipode account. The plugin works after local dependency
preparation without an audio-generation API or GPU.

The [shared data description](README.md#access-data-and-limitations) discloses
file access, local persistence, host-visible metadata and first-run downloads.
The project has no telemetry. Host conversation and attachment behavior remains
separate. Tool-level read-only/destructive annotations describe effects but do
not replace the host's permission decisions.

The [verification record](../verification.md) describes an actual bounded native
Antigravity session that generated a WAV, along with independent MCP/CLI tests.
That is not a claim of completed Google review or every possible creative
workflow. Audio is capped at 30 seconds and 16 layers, with PCM16 WAV input/output
support as documented in the shared kit.

Source and artwork are Apache-2.0; bundled studies are CC0-1.0 to the extent of
contributor rights. No trademark clearance or exclusivity is promised. Preserve
the bundled licenses and [rights disclosures](../rights.md) in distribution.

## Remaining portal work

The publisher must supply an authorized email and publisher identity, review the
actual intake fields and terms presented in their authenticated session, attach
or link the exact reviewed native artifact if requested, and record the resulting
submission confirmation. The form's later fields have not been assumed here.
If a public artifact URL is requested, publish the reviewed ZIP and checksum as
release assets first; a local `dist/` path is not a download URL.

No fictitious representative, certification, approval, response time, submission
receipt or Marketplace listing URL is supplied by this dossier.
