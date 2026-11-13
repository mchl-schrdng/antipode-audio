"""Local stdio transport; the audio engine owns all audio behavior."""

import argparse
from functools import wraps
import sys

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp_types import ToolAnnotations

from antipode.engine import AudioEngine


def _tool_errors(function):
    @wraps(function)
    def call(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (ValueError, OSError) as error:
            raise ToolError(str(error)) from error

    return call


def serve(workspace: str) -> None:
    engine = AudioEngine(workspace)
    server = MCPServer(
        "antipode-mcp",
        version="0.1.0",
        instructions=(
            "Create and process local sounds with deterministic DSP. Call list_presets first. "
            "All paths are relative to the configured audio workspace. Choose unique .wav "
            "output names for each variation or agent; files are never overwritten. "
            "Use render_recipe for layered stereo sound design; generate_sound for a single source. "
            "Use analyze_audio to check levels. No neural audio generation or playback is provided."
        ),
    )
    for function in (
        engine.list_presets, engine.generate_sound, engine.render_recipe,
        engine.process_audio, engine.analyze_audio,
    ):
        read_only = function.__name__ in ("list_presets", "analyze_audio")
        server.add_tool(
            _tool_errors(function),
            annotations=ToolAnnotations(
                readOnlyHint=read_only,
                destructiveHint=False,
                idempotentHint=read_only,
                openWorldHint=False,
            ),
        )
    server.run(transport="stdio")


def main() -> None:
    parser = argparse.ArgumentParser(prog="antipode-mcp", description="Antipode local MCP server (stdio).")
    parser.add_argument("--workspace", required=True, help="Audio directory accessible to the server.")
    arguments = parser.parse_args()
    try:
        serve(arguments.workspace)
    except (ValueError, OSError) as error:
        print(f"antipode-mcp: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
