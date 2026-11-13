# Antipode

Antipode creates original sound effects and short layered atmospheres using a
local procedural DSP engine. Use its `antipode` skill for audio creation and
iteration. The connected MCP server exposes `list_presets`, `generate_sound`,
`render_recipe`, `process_audio` and `analyze_audio`; tool names may carry a
server prefix. Discover presets before choosing a voice.

Use `render_recipe` for layered stereo sound. Keep the exact recipe and seeds
with the user's deliverables, render to a new filename, then check levels with
`analyze_audio`. Audio paths must be relative to the server's workspace, normally
`~/.antipode/audio`; existing files are never replaced. The returned `path`
identifies the actual WAV. Do not claim to have listened without playing it.

The engine has no neural audio model, sample library, telemetry or hosted API.
Its first startup may download Python 3.12 and locked dependencies through uv;
later audio generation works offline. If MCP is unavailable, explain the
connection issue and refer to `docs/integrations.md`. Do not install an invented
package or replace the engine with an unrequested audio service. Use authorized
source material and do not promise exclusivity, copyright ownership or legal
clearance.
