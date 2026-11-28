---
name: antipode
description: Create original sound effects, sonic identities, layered atmospheres and short musical textures using Antipode's local synthesis engine. Use for audio creation, iteration, WAV processing and level analysis; not speech synthesis or audio transcription.
---

# Antipode

Turn the user's description into a concrete sound, then refine by listening and measuring. The available engine is procedural DSP, with no pretrained model or sample library.

Use the connected Antipode MCP tools. Start with `list_presets` for the 16 preset voices. Choose `generate_sound` for one preset and `render_recipe` for stereo layers, materials, automation or families. Tool names may carry the host's plugin/server prefix. If the server is unavailable, explain that Antipode needs its local dependencies installed and refer to the repository's `docs/integrations.md`; do not install a guessed package from a registry.

For layered work, read [the recipe reference](references/recipes.md). Describe the intended duration, register, texture, motion and space in one short sentence, then render a small number of purposeful variants. Pick contrasting layers with distinct roles: body, motion, detail. Leave headroom and space; adding layers is not automatically an improvement.

- For a physical object, choose a `material` layer. To compare a hanging plate with the same plate held in a hand, keep its metal body, pitch, seed and strike, then raise `damping` for the held version. Use `gesture: "rub"` for sustained contact.
- For “three waves,” decide what moves. Write three peaks between troughs in `automation.lowpass_hz` for brightness or `automation.level_db` for loudness. Time the points in seconds from the start of that layer. To slow down the last wave, move its points and extend the layer and recipe durations if needed.
- For “three signals from the same object,” save one family JSON with a shared `base` recipe and named `members`. Give each cue its own event timing, attack or pitch. Render each with `render_recipe(recipe=family, output="confirm.wav", member="confirm")`, using its own name and output path. Edit the base to change the timbre of the whole set.

Save the exact recipe JSON next to the project deliverables using the host's file tool so the user can reproduce or edit it. Preserve seeds while comparing changes. Change one or two relevant parameters per iteration. Render new output names; Antipode never overwrites files. Parallel agents should use distinct subdirectories or filename prefixes.

Use `process_audio` for spectral filtering, gain, fades, reversal and peak normalization of supported existing WAVs. Only work with material the user is authorized to use. Generated audio stays in the configured workspace (default plugin location: `~/.antipode/audio`). Returned `path` values identify the actual files. Offer a playable file when the host supports it; never claim to have heard audio without listening.

Check `analyze_audio` before delivery. Its measurements are sample-level (not LUFS, true peak, or a mastering certificate): `peak_time_seconds` locates the loudest transient; `spectral_centroid_hz` is the whole-file AC power-weighted mean frequency (dark `< 250 Hz`, warm `250–1500 Hz`, bright `> 1500 Hz`); `stereo_balance` is `(right_rms - left_rms) / (right_rms + left_rms)` from `-1` (left) to `1` (right), where constant-power `pan: 0.5` yields `~0.414`. Explain any clipping/full-scale warning and correct it. Final delivery includes the WAV, the recipe for composed sounds, and a concise description of what changed.

Create original designs. Do not import samples, imitate a recognizable protected melody, or promise exclusivity, copyright ownership or legal clearance. The project's license covers its software; a sound's rights depend on the material and creative work involved. Consult the repository's rights documentation for the project's specific scope.
