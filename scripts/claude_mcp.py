# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["mcp>=2,<3", "numpy>=2,<3"]
# ///
"""Launch the bundled MCP engine in uv's locked, cached script environment."""

from pathlib import Path
import sys

# Installed plugin files are immutable; keep bytecode and environments out of them.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from antipode.mcp_server import main


if __name__ == "__main__":
    main()
