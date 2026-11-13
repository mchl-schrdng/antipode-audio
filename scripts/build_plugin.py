#!/usr/bin/env python3
"""Build a reproducible plugin ZIP from an explicit, Git-tracked source allowlist."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
    ".python-version",
    "CONTRIBUTING.md",
    "LICENSE",
    "NOTICE",
    "README.md",
    "SECURITY.md",
    "THIRD_PARTY_NOTICES.md",
    "assets/brand/github-cover.svg",
    "assets/brand/icon.svg",
    "assets/brand/mark-dark.svg",
    "assets/brand/mark.svg",
    "assets/brand/wordmark.svg",
    "docs/distribution/README.md",
    "docs/distribution/antigravity.md",
    "docs/distribution/claude.md",
    "docs/integrations.md",
    "docs/legal/CC0-1.0.txt",
    "docs/legal/dependency-audit.json",
    "docs/rights.md",
    "docs/verification.md",
    "examples/LICENSE",
    "examples/audio/afterimage.wav",
    "examples/audio/event-horizon.wav",
    "examples/audio/glass-orbit.wav",
    "examples/recipes/afterimage.json",
    "examples/recipes/event-horizon.json",
    "examples/recipes/glass-orbit.json",
    "integrations/antigravity.plugin.json",
    "integrations/claude.mcp.json",
    "mcp.json",
    "mcp_config.json",
    "plugin.json",
    "pyproject.toml",
    "scripts/build_plugin.py",
    "scripts/client_config.py",
    "scripts/claude_mcp.py",
    "scripts/claude_mcp.py.lock",
    "skills/antipode/SKILL.md",
    "skills/antipode/references/recipes.md",
    "src/antipode/__init__.py",
    "src/antipode/cli.py",
    "src/antipode/engine.py",
    "src/antipode/mcp_server.py",
    "src/antipode/synthesis.py",
    "uv.lock",
)


def build(root: Path, output: Path, client: str = "portable") -> dict:
    if client not in ("portable", "antigravity"):
        raise ValueError("client must be portable or antigravity")
    tracked = set(subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode("utf-8").split("\0"))
    missing = sorted(set(FILES) - tracked)
    if missing:
        raise ValueError("Required files are not Git-tracked; review and stage them first: " + ", ".join(missing))
    contents = {}
    for name in FILES:
        path = root / name
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != root and root in parent.parents):
            raise ValueError(f"Symlinks are not allowed in a plugin bundle: {name}")
        if not path.is_file():
            raise ValueError(f"Required regular file is missing: {name}")
        contents[name] = path.read_bytes()
    version = tomllib.loads(contents["pyproject.toml"].decode("utf-8"))["project"]["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Release version must be MAJOR.MINOR.PATCH")
    for name in ("plugin.json", ".claude-plugin/plugin.json", "integrations/antigravity.plugin.json"):
        manifest = json.loads(contents[name])
        if manifest.get("name") != "antipode" or manifest.get("version") != version:
            raise ValueError(f"Plugin name or version differs from pyproject.toml: {name}")
    if client == "antigravity":
        contents["plugin.json"] = contents["integrations/antigravity.plugin.json"]
        del contents["mcp.json"]  # Native Antigravity reads mcp_config.json instead.

    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"antipode-{client}-{version}.zip"
    # Stored entries avoid compressor-version differences; fixed metadata ignores checkout mtimes and umask.
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as bundle:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            mode = 0o755 if name.startswith("scripts/") and name.endswith(".py") else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            bundle.writestr(info, data)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8", newline="\n")
    return {"archive": str(archive), "sha256": digest, "files": len(contents), "bytes": archive.stat().st_size}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=("portable", "antigravity"), default="portable")
    args = parser.parse_args()
    try:
        print(json.dumps(build(ROOT, ROOT / "dist", args.client), indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"build_plugin: {error}\n")
