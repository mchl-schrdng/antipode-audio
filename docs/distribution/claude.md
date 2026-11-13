# Claude directory submission dossier

Updated 2026-11-13 for Antipode 0.1.2. Portal validation passed at
[commit ad98569](https://github.com/mchl-schrdng/antipode-audio/commit/ad985696c5878a0a0830bbcd12c5b03a903ad2f4):
**zero blocking findings, eight warnings and four policy holds**. The GitHub
connection and publisher checks passed. Legal acknowledgements and the final
submission remain pending. No submission confirmation, approval or public listing
is recorded.

## Route and source

Use the [developer portal](https://claude.ai/directory/manage), choose a plugin
bundle, and submit the GitHub source below. The portal requires an eligible paid
plan/role and a connected GitHub account with push access. Its validation applies
to a specific commit and goes beyond the local CLI validator. A passing version
still has a separate publication step. See the official
[submission instructions](https://claude.com/docs/plugins/submit) and
[publishing guide](https://code.claude.com/docs/en/plugins/publish).

| Portal field | Proposed value |
| --- | --- |
| Repository | `https://github.com/mchl-schrdng/antipode-audio` |
| Plugin path | Empty: `.claude-plugin/plugin.json` is at the repository root |
| Branch or tag | Release tag [v0.1.2](https://github.com/mchl-schrdng/antipode-audio/releases/tag/v0.1.2); revalidate the final revision before submission |
| Name / display name | `antipode` / Antipode |
| Version | `0.1.2` |
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
- The portal recorded four policy holds for human review of pinned dependencies,
  bundled WAV demos, Python code and local MCP execution. These remain review
  items even though there are no blocking validation findings. Claude's
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

## Remaining portal work

Revalidate the final v0.1.2 revision after the approved brand assets and release
metadata are included. Review the remaining findings and confirm the completed
contact, data-handling and audience answers. The publisher must then confirm the
legal acknowledgements and send the submission.
Review the [directory terms](https://support.claude.com/en/articles/13145338-anthropic-software-directory-terms)
and policy before accepting the portal acknowledgements. No terms acceptance,
submission identifier, approval or listing URL is recorded by this dossier.

Use the verification record's actual limits: native Claude Code connection and
strict manifests were checked; a complete logged-in creative conversation across
all target products has not been established. The three example recipes are
executable review material, not evidence of an unperformed Anthropic evaluation.
