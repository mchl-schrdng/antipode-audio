"""Command-line entry point. Successful audio commands return JSON."""

import argparse
import json
from pathlib import Path
import sys

from antipode.engine import AudioEngine, PRESETS


def main() -> None:
    parser = argparse.ArgumentParser(prog="antipode", description="Local sound creation for AI coding agents.")
    parser.add_argument("--workspace", default="audio", help="Audio directory (default: ./audio).")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("presets", help="List available synthesis presets.")
    generate = commands.add_parser("generate", help="Generate a new mono 48 kHz WAV.")
    generate.add_argument("output", help="New .wav path relative to the workspace.")
    generate.add_argument("--preset", choices=PRESETS, default="chime")
    generate.add_argument("--duration", type=float, default=1.0, help="Seconds, 0.02–30.")
    generate.add_argument("--frequency", type=float, default=660.0, help="Hz, 20–8000; ignored for noise.")
    generate.add_argument("--level-db", type=float, default=-12.0, help="Peak dBFS, -60 to -1.")
    generate.add_argument("--seed", type=int, default=0, help="Noise seed, 0–4294967295.")
    process = commands.add_parser("process", help="Process a WAV into a new file.")
    process.add_argument("source")
    process.add_argument("output")
    process.add_argument("--gain-db", type=float, default=0.0)
    process.add_argument("--fade-in", type=float, default=0.0, help="Seconds.")
    process.add_argument("--fade-out", type=float, default=0.0, help="Seconds.")
    process.add_argument("--reverse", action="store_true")
    process.add_argument("--normalize-db", type=float, help="Optional final peak target, -60 to -1 dBFS.")
    analyze = commands.add_parser("analyze", help="Measure a PCM16 WAV.")
    analyze.add_argument("source")
    render = commands.add_parser("render", help="Render a layered sound recipe into a stereo WAV.")
    render.add_argument("recipe", help="Path to a JSON recipe (outside or inside the audio workspace).")
    render.add_argument("output", help="New .wav path relative to the audio workspace.")
    commands.add_parser("mcp", help="Serve MCP over stdio until the client disconnects.")
    arguments = vars(parser.parse_args())
    command = arguments.pop("command")
    workspace = arguments.pop("workspace")
    try:
        if command == "mcp":
            from antipode.mcp_server import serve

            serve(workspace)
            return
        engine = AudioEngine(workspace)
        if command == "render":
            recipe_path = Path(arguments["recipe"])
            if recipe_path.stat().st_size > 64 * 1024:
                raise ValueError("Recipe must not exceed 64 KiB.")
            arguments["recipe"] = json.loads(recipe_path.read_text(encoding="utf-8"))
        operation = {
            "presets": engine.list_presets,
            "generate": engine.generate_sound,
            "process": engine.process_audio,
            "analyze": engine.analyze_audio,
            "render": engine.render_recipe,
        }[command]
        print(json.dumps(operation(**arguments), indent=2, allow_nan=False))
    except (ValueError, OSError) as error:
        print(f"antipode: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
