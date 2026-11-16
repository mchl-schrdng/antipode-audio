"""Print a source-checkout MCP configuration. Never modify an agent's settings."""

import argparse
import json
import os
from pathlib import Path
import sys


def configuration(client: str, root: Path, workspace: str) -> dict:
    python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    command = [str(python), "-m", "antipode.mcp_server", "--workspace", workspace]
    if client == "opencode":
        return {
            "$schema": "https://opencode.ai/config.json",
            "mcp": {"servers": {"antipode": {"type": "local", "command": command}}},
            "skills": [str(root / "skills")],
        }
    return {"mcpServers": {"antipode": {"command": command[0], "args": command[1:]}}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client", choices=("codex", "claude", "antigravity", "opencode"))
    parser.add_argument("--workspace", default="~/.antipode/audio")
    arguments = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parents[1]
    value = configuration(arguments.client, root, arguments.workspace)
    if arguments.client == "codex":
        server = value["mcpServers"]["antipode"]
        print("[mcp_servers.antipode]")
        print(f"command = {json.dumps(server['command'], ensure_ascii=False)}")
        print(f"args = {json.dumps(server['args'], ensure_ascii=False)}")
    else:
        print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
