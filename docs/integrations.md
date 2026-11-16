# Connect your agent

Antipode is one local audio engine, one MCP server and one sound-design skill. Codex, Claude Code and Antigravity load the plugin bundle. Gemini CLI loads its root extension manifest. OpenCode connects the same server and skill through its project configuration.

## Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) once and keep it on your agent application's `PATH`. Antipode's first launch automatically prepares Python 3.12 and locked dependencies. No manual `uv sync`, GPU, model download or Antipode account is required.

- **Offline operation:** the first launch requires internet access so `uv` can cache Python and dependencies. Subsequent launches work offline; the audio engine itself never calls the network.
- **Audio workspace:** plugin renders default to `~/.antipode/audio`. Agents can only address relative `.wav` paths within that workspace, and existing files are never overwritten.

---

## Claude Code

```sh
claude plugin install antipode --marketplace mchl-schrdng/antipode-audio
```

Or run `/plugin install antipode --marketplace mchl-schrdng/antipode-audio` inside Claude Code, start a new session, and invoke `/antipode:antipode`.

For older Claude Code versions:

```sh
claude plugin marketplace add mchl-schrdng/antipode-audio
claude plugin install antipode@antipode-local
```

Claude launches `scripts/claude_mcp.py` via `uv run --locked` using the adjacent `scripts/claude_mcp.py.lock` lockfile and keeps its isolated environment in `uv`'s cache outside the plugin directory.

---

## Codex

```sh
codex plugin marketplace add mchl-schrdng/antipode-audio
codex plugin add antipode@antipode-local
```

Start a new Codex session and use the Antipode skill. `plugin.json` and `mcp.json` follow the portable Agent Plugins format, and `.agents/plugins/marketplace.json` supplies the repository catalog.

---

## Gemini CLI

```sh
gemini extensions install https://github.com/mchl-schrdng/antipode-audio
gemini extensions list
gemini mcp list
```

Restart Gemini CLI after installation. The root `gemini-extension.json` manifest discovers `skills/antipode/SKILL.md` and connects the local stdio MCP server (`gemini mcp list` should report **Connected**).

---

## Antigravity

Build or download the native Antigravity plugin bundle (`python3 scripts/build_plugin.py --client antigravity`), extract it into an `antipode` folder, and run:

```sh
agy plugin install ./antipode
```

Restart the session and invoke Antipode. The Antigravity bundle uses `integrations/antigravity.plugin.json` as its root `plugin.json` and `mcp_config.json` for its MCP server configuration.

---

## OpenCode

Clone the repository and print the project configuration:

```sh
git clone https://github.com/mchl-schrdng/antipode-audio.git
cd antipode-audio
uv run --locked python scripts/client_config.py opencode
```

Merge the printed `mcp.servers.antipode` entry and `skills` path into your project's `opencode.json`, then verify with `opencode mcp list`.

---

## Direct MCP configuration & local development

To generate a standalone MCP configuration for any client from a local checkout:

```sh
uv run --locked python scripts/client_config.py codex
uv run --locked python scripts/client_config.py claude
uv run --locked python scripts/client_config.py antigravity
```

Pass `--workspace /absolute/path/to/audio` to customize the output directory. To run the cold-install integration check explicitly:

```sh
ANTIPODE_TEST_COLD_INSTALL=1 uv run --locked python -m unittest discover -s tests -p test_integrations.py -v
```
