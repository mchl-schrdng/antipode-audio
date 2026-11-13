---
name: antipode
description: Create original sound effects, sonic identities, layered atmospheres and short musical textures using Antipode's local synthesis engine. Use for audio creation, iteration, WAV processing and level analysis; not speech synthesis or audio transcription.
---

# Antipode

Turn the user's description into a concrete sound, then refine by listening and measuring. The available engine is procedural DSP, with no pretrained model or sample library.

Use the connected Antipode MCP tools. Start with `list_presets` to see the actual sources. Choose `generate_sound` for a single source and `render_recipe` for layered stereo design. Tool names may carry the host's plugin/server prefix. If the server is unavailable, explain that Antipode needs its local dependencies installed and refer to the repository's `docs/integrations.md`; do not install a guessed package from a registry.

For layered work, read [the recipe reference](references/recipes.md). Describe the intended duration, register, texture, motion and space in one short sentence, then render a small number of purposeful variants. Pick contrasting layers with distinct roles: body, motion, detail. Leave headroom and space; adding layers is not automatically an improvement.

Save the exact recipe JSON next to the project deliverables using the host's file tool so the user can reproduce or edit it. Preserve seeds while comparing changes. Change one or two relevant parameters per iteration. Render new output names; Antipode never overwrites files. Parallel agents should use distinct subdirectories or filename prefixes.

Use `process_audio` for gain, fades, reversal and peak normalization of supported existing WAVs. Only work with material the user is authorized to use. Generated audio stays in the configured workspace (default plugin location: `~/.antipode/audio`). Returned `path` values identify the actual files. Offer a playable file when the host supports it; never claim to have heard audio without listening.

Check `analyze_audio` before delivery. Its peak and RMS measurements are sample-level dBFS, not LUFS, true peak, or a mastering certificate. Explain any clipping/full-scale warning and correct it. Final delivery includes the WAV, the recipe for composed sounds, and a concise description of what changed.

Create original designs. Do not import samples, imitate a recognizable protected melody, or promise exclusivity, copyright ownership or legal clearance. The project's license covers its software; a sound's rights depend on the material and creative work involved. Consult the repository's rights documentation for the project's specific scope.
