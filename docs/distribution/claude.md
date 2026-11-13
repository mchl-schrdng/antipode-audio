# Claude directory submission dossier

**Submitted for review on 2026-11-13:** Antipode 0.1.2, from
[commit ad2a6a3](https://github.com/mchl-schrdng/antipode-audio/commit/ad2a6a37d46352fe7e26b3aa25da0c582c621bf6),
for **Claude Code only**. The portal confirms submission and shows the security
scan in progress. Human review has not started; approval and public listing
remain pending. Automatic publication is disabled.

## Route and source

The plugin was submitted through the [developer portal](https://claude.ai/directory/manage)
using the GitHub source below. The portal requires an eligible paid
plan/role and a connected GitHub account with push access. Its validation applies
to a specific commit and goes beyond the local CLI validator. A passing version
still has a separate publication step. See the official
[submission instructions](https://claude.com/docs/plugins/submit) and
[publishing guide](https://code.claude.com/docs/en/plugins/publish).

| Portal field | Submitted value |
| --- | --- |
| Repository | `https://github.com/mchl-schrdng/antipode-audio` |
| Plugin path | Empty: `.claude-plugin/plugin.json` is at the repository root |
| Source revision | Commit `ad2a6a3`, also tagged [v0.1.2](https://github.com/mchl-schrdng/antipode-audio/releases/tag/v0.1.2) |
| Name / display name | `antipode` / Antipode |
| Version | `0.1.2` |
| Surface | Claude Code only |
| Automatic publication | Disabled |
| Listing, links and examples | [Shared distribution kit](README.md) and repository README |
| Icon | Bundled square SVG, declared in the Claude manifest |

The portable ZIP is useful for local review. The public directory's submission
source is the repository, not a Python wheel or a pull request to Anthropic's
marketplace repository. Do not submit a remote connector: this project provides
a local stdio MCP process, with no remote server URL.

## Local reviewer steps

From the extracted portable archive, with `uv` available on PATH:

```sh
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
claude --plugin-dir .
```

The first check discovers the repository's marketplace; the second explicitly
checks the plugin manifest.

In the new Claude Code session, use `/antipode:antipode`, check the MCP connection,
and run the three prompts in the [shared review procedure](README.md#reviewer-walkthrough).
The `.claude-plugin/plugin.json` manifest names `integrations/claude.mcp.json`;
the process runs `uv run --locked ${CLAUDE_PLUGIN_ROOT}/scripts/claude_mcp.py`.
The bundled PEP 723 script declares Python 3.12 and its dependencies; the adjacent
lockfile fixes their versions. uv stores the isolated environment in its cache,
outside the installed plugin. The launcher disables bytecode writes and declares
no server environment overrides. First startup can download Python and dependencies.
This package targets local Claude Code execution. Do not advertise working audio
tools in Claude.ai chat or Cowork without separate compatible-surface evidence.

## Material review disclosures

- The engine synthesizes audio procedurally; it contains no AI audio, voice or
  music-generation model. A general coding agent creates the recipe. The
  [directory policy](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy)
  excludes certain AI audio-model software. This distinction should be presented
  transparently for Anthropic to assess; it is not a claimed policy clearance.
- Earlier portal validation at `ad98569` passed with zero blocking findings,
  eight warnings and four policy holds for human review of pinned dependencies,
  bundled WAV demos, Python code and local MCP execution. These remain review
  items; submission does not establish approval. Claude's
  [pre-submission checklist](https://claude.com/docs/plugins/pre-submission-checklist)
  flags these execution/file categories for reviewer inspection. Local strict
  validation is not proof of directory acceptance. Keep the source and downloads
  disclosed instead of hiding these components.
- The [shared data description](README.md#access-data-and-limitations) covers
  local WAV writes, possible personal data in user audio, file-path metadata
  returned to the host, software downloads and retention. No Antipode-operated
  service receives user content. Do not answer a portal question about personal
  data with an unconditional “none”: users can choose personal audio and paths.
- The software has no child-specific audience or age-verification feature. The
  publisher must answer audience, data-handling and compliance questions based on
  the actual intended distribution, rather than inferring an age certification.
- The working name is not trademark-cleared. Licenses and provenance are
  documented; no legal opinion, exclusivity guarantee or platform certification
  is supplied.

## Review status

Submission is confirmed and the security scan is in progress. Await its result
and any subsequent human-review requests. No approval or public listing is
recorded. Automatic publication remains disabled.

The v0.1.2 release files remain fixed to their release commit. This status update
on `main` does not replace those published assets.

Use the verification record's actual limits: native Claude Code connection and
strict manifests were checked; a complete logged-in creative conversation across
all target products has not been established. The three example recipes are
executable review material, not evidence of an unperformed Anthropic evaluation.
