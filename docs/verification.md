# Verification record

Checked on **13 November 2026**, on macOS ARM64. This describes observed results,
not a certification of every agent version or every possible audio use.

## Engine, transport and packaging

- **19 automated tests passed** with Python 3.12: synthesis, frequency/level
  measurements, seeded repeatability, stereo timing, effects, recipe validation,
  file preservation, concurrent writes, traversal/symlink/Windows path rejection,
  malformed WAV input, CLI, configuration generation and real MCP subprocesses.
- The MCP tests call all five tools using both modern and legacy negotiation and
  verify output files and structured results. Expected invalid calls return errors.
- Every shipped plugin launch configuration rendered a WAV offline with its
  environment outside the plugin source directory.
- Independent review tested a relocated, read-only source copy. It launched
  offline and generated audio without creating a virtual environment in the source.
- The source distribution and wheel build successfully. A fresh Python 3.11
  environment installed the wheel and rendered a stereo WAV, without importing
  the development checkout.
- A dependency scan using `pip-audit` found **zero known vulnerabilities in 29
  installed third-party distributions**. The unpublished Antipode distribution
  was skipped by the vulnerability service. See the [raw result](legal/dependency-audit.json).
  An empty advisory result is not proof that no vulnerability exists.

## Native agent checks

| Host | Observed result | Remaining limit |
| --- | --- | --- |
| Codex | Catalog discovery and native app-server connection expose all five tools, with schemas and no discovery error | No full creative conversation evaluated |
| Claude Code | Strict plugin/marketplace validation passes; native MCP connection reports Connected | No full creative conversation evaluated |
| Antigravity 1.5.8 | Strict plugin validation passes; a native authenticated session calls the MCP and creates a 4,800-frame, 48 kHz WAV | Only a bounded generation smoke test, not a full creative conversation |
| OpenCode 1.19.5 | Native MCP status reports Connected; native skill discovery finds Antipode | No full creative conversation evaluated |

The Antigravity check used a temporary uniquely named registration and
removed it afterward, restoring the original configuration. The smoke session
allowed only the test server's generation tool. No authentication settings were changed. Other native
checks used isolated configuration or runtime overrides.

The repository's CI matrix targets Linux, macOS and Windows. Local checks alone
do not establish those CI results; consult the actual [Actions runs](https://github.com/mchl-schrdng/antipode-audio/actions).

## Website and sound studies

- Desktop layout checked at 1440 × 900; mobile at 390 × 844 without page overflow.
- Real WAV playback, exclusive track switching and copy-install controls verified
  in a browser. No console errors observed during those checks.
- JavaScript syntax, local asset links and audio formats checked. The site has
  no external font, animation-library or image dependency.
- Reduced-motion handling and offscreen animation suspension are implemented;
  no operating-system preference was changed for testing.
- The three recordings are reproducible from their recipes within the tested
  runtime; tests allow one PCM least-significant bit for floating-point differences.
- No independent subjective listening panel, loudness certification, LUFS/true-peak
  mastering validation or hardware playback calibration was performed.

## Open release decisions

`antipode.quest` is an intended domain, not a verified DNS attachment in this
repository. The name/logo have not received trademark clearance. The documented
[rights review](rights.md) records nearby existing audio names and the limits of
the licensing statements. No PyPI or public plugin-directory publication is claimed.
