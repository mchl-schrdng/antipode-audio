# Verification record

Checked on **13 November 2026**, on macOS ARM64. This describes observed results,
not a certification of every agent version or every possible audio use.

## Engine, transport and packaging

- **23 automated tests passed** with Python 3.12: synthesis, frequency/level
  measurements, seeded repeatability, stereo timing, effects, recipe validation,
  file preservation, concurrent writes, traversal/symlink/Windows path rejection,
  malformed WAV input, CLI, configuration generation and real MCP subprocesses.
- The MCP tests call all five tools using both modern and legacy negotiation and
  verify output files and structured results. Expected invalid calls return errors.
- Version 0.1.1 launches prepare their locked dependencies automatically. A clean
  test used an empty uv cache, an empty managed-Python directory and a read-only
  source copy: Python 3.12 and dependencies downloaded, then a 4,800-frame WAV was
  rendered in 8.87 seconds. A second start forced uv offline and prohibited Python
  downloads; it rendered another WAV in 0.48 seconds without source writes. These
  are observed test timings, not installation-time guarantees.
- Every shipped launch configuration also rendered a WAV with offline mode forced
  and its environment outside the plugin source directory.
- Both plugin ZIP formats use explicit tracked-file allowlists, fixed archive
  metadata and SHA-256 sidecars. Packaging tests cover reproducibility, unexpected
  file exclusion, missing files, version mismatches and symlink rejection.
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
| Claude Code | Strict plugin/marketplace validation passes; version 0.1.1 installed in a fresh Claude configuration and connected natively with an empty dependency cache in 6.35 seconds | No full creative conversation evaluated |
| Antigravity 1.5.8 | Strict native bundle validation passes; version 0.1.1 installed as a plugin and an authenticated agent session created a 4,800-frame, 48 kHz WAV | Only a bounded generation smoke test, not a full creative conversation |
| OpenCode 1.19.5 | Native MCP status reports Connected; native skill discovery finds Antipode | No full creative conversation evaluated |

The documented one-command public GitHub installation was also tested against
commit `a557a8e` with a fresh Claude configuration and empty dependency cache:
version 0.1.1 installed in 4.70 seconds and its native MCP connected from the
installed copy in 5.96 seconds. Existing global Claude settings were unchanged.

The original Antigravity check used a temporary uniquely named MCP registration.
The 0.1.1 check exercised an actual installed plugin with a temporary output
workspace and dependency cache; the test installation was removed afterward.
The bounded smoke session permitted only the generation tool. No authentication
settings or existing audio files were changed. Claude checks used an isolated
configuration; other native checks used runtime overrides.

**Version 0.1.1 passed all four GitHub Actions jobs** at commit `a557a8e`: Linux with Python
3.11 and 3.12, macOS with Python 3.12, and Windows with Python 3.12. Each job ran
the 23-test suite, built the Python distributions and packaged both plugin ZIP
formats. See the
[successful run](https://github.com/mchl-schrdng/antipode-audio/actions/runs/43381385925)
and [latest runs](https://github.com/mchl-schrdng/antipode-audio/actions).

## Website and sound studies

- Desktop layout checked at 1440 × 900; mobile at 390 × 844 without page overflow.
  The live custom domain was checked again on desktop and mobile after deployment,
  including the animated wire-ring logo, all three recordings and install controls.
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

The listening room is live at [antipode.quest](https://antipode.quest), deployed
from a separate private frontend repository on Vercel. Its domain configuration
and HTTPS page were verified on the review date. The name/logo have not received
trademark clearance. The documented
[rights review](rights.md) records nearby existing audio names and the limits of
the licensing statements. No PyPI or public plugin-directory publication is claimed.
