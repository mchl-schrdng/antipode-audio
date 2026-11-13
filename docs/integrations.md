# Connect your agent

Antipode is one local audio engine, one MCP server and one sound-design skill. Codex, Claude Code and Antigravity load the plugin bundle. OpenCode connects the same server and skill through its project configuration.

## Install uv once

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and make sure it is on your agent application's PATH. Antipode's first launch automatically prepares Python 3.12 and locked dependencies. No `uv sync` step, GPU, model download or Antipode account is required.

The first launch needs internet access. Later launches can use the prepared runtime offline. The audio engine itself never uses the network. Your host agent may use a cloud model for conversation. If a slow first download exceeds the host's startup timeout, let the download complete where possible and reconnect the MCP server. For environments with no network at all, prepare the runtime before disconnecting.

Claude Code uses uv's isolated script cache; the other plugin hosts use their writable plugin-data directory. Both keep environments outside the installed source. Plugin audio goes to `~/.antipode/audio` and survives plugin replacement. The server expands `~` itself. Agents can only address relative WAV paths within that workspace; existing files are never replaced. Use different output names or subdirectories for different agents.

## Claude Code

Run in your terminal:

```sh
claude plugin install antipode --marketplace mchl-schrdng/antipode-audio
```

Or run inside Claude Code:

```text
/plugin install antipode --marketplace mchl-schrdng/antipode-audio
```

Start a new session, then use `/antipode:antipode` or ask Claude to design a sound with Antipode. This adds the project's own marketplace and installs its plugin; it does not imply approval in Anthropic's public directory. The terminal one-step command requires Claude Code 2.1.292 or later; the in-session `/plugin` form requires 2.1.275 or later. [Official installation commands](https://code.claude.com/docs/en/plugins/cli-reference), [plugin manifest reference](https://code.claude.com/docs/en/plugins-reference).

Claude launches the bundled `scripts/claude_mcp.py` with `uv run --locked`. Its PEP 723 metadata declares Python 3.12 and the same dependencies as the project; `scripts/claude_mcp.py.lock` fixes their versions. The short launcher imports the bundled engine, disables bytecode writes, and declares no server environment overrides. uv does not automatically read a working-directory `.env` file; loading one requires an explicit uv option or user environment setting. [uv script documentation](https://docs.astral.sh/uv/guides/scripts/).

For an older client, add the marketplace first:

```sh
claude plugin marketplace add mchl-schrdng/antipode-audio
claude plugin install antipode@antipode-local
```

## Codex

```sh
codex plugin marketplace add mchl-schrdng/antipode-audio
codex plugin add antipode@antipode-local
```

Start a new Codex session and use the Antipode skill. `plugin.json` and `mcp.json` use the portable Agent Plugins format; `.agents/plugins/marketplace.json` supplies the repository catalog. This is a local desktop/CLI plugin. [Official packaging documentation](https://developers.openai.com/plugins/build/plugins), [local MCP guidance](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

## Antigravity

Download `antipode-antigravity-0.1.1.zip` from [GitHub Releases](https://github.com/mchl-schrdng/antipode-audio/releases). Extract it into a new `antipode` folder, then:

```sh
agy plugin install ./antipode
```

Restart the agent session and invoke Antipode. The app can also install the extracted local folder from its plugin interface. Its Google-specific package includes the square logo, starter prompts and native `mcp_config.json`. [Official plugin installation](https://antigravity.google/docs/plugins), [packaging reference](https://antigravity.google/docs/build-plugins).

The repository's portable `plugin.json` and Google's native listing schema differ. The Google archive uses `integrations/antigravity.plugin.json` as its root manifest and omits portable `mcp.json`; the engine and skill are identical. Both formats pass their strict native validators. See [distribution](distribution/README.md) for reproducible packaging and submission status.

## OpenCode

With Git installed, clone this repository and print its configuration:

```sh
git clone https://github.com/mchl-schrdng/antipode-audio.git
cd antipode-audio
uv run --locked python scripts/client_config.py opencode
```

Merge the printed `mcp.servers.antipode` entry and `skills` path into your project's `opencode.json`, preserving existing settings. Then run:

```sh
opencode mcp list
```

The server should be connected; `opencode debug skill` should include `antipode`. Start a fresh session and ask for a sound. This uses OpenCode's MCP and skill extension points. [Official MCP configuration](https://opencode.ai/docs/mcp-servers), [skill configuration](https://opencode.ai/docs/skills).

## Direct MCP configuration and local development

From a source checkout, print a configuration for a host that does not support plugin bundles:

```sh
uv run --locked python scripts/client_config.py codex
uv run --locked python scripts/client_config.py claude
uv run --locked python scripts/client_config.py antigravity
```

The generator prints TOML for Codex and JSON for the others. It never edits settings. The first command prepares the checkout's `.venv`; generated configurations use that interpreter's absolute path. Keep the checkout in place. Copy `skills/antipode` to the host's project skill directory to add the creative workflow. A direct MCP connection alone exposes the tools and their descriptions.

Use `--workspace /absolute/path/to/project/audio` on the generator to choose another audio directory. If a desktop host cannot find `uv`, this absolute-interpreter configuration also avoids depending on the desktop application's PATH.

To try Claude without installing the plugin, run `claude --plugin-dir .` from the checkout. For the CLI:

```sh
uv run --locked antipode --workspace ./audio generate chime.wav --preset glass
uv run --locked antipode --workspace ./audio render examples/recipes/event-horizon.json atmosphere.wav
uv run --locked antipode --workspace ./audio analyze atmosphere.wav
```

Once prepared, add `--offline` after `uv run` to prohibit downloads. Launching your host from a terminal with `UV_OFFLINE=1` also restricts uv to its cache; the shipped Claude server configuration declares no environment overrides. A new plugin version or deleted runtime may need network setup again. Recipe filenames are ordinary CLI inputs; tool audio paths remain confined to the configured workspace.

## Verification scope

| Surface | Verified |
| --- | --- |
| MCP protocol | Real subprocess connections with modern and legacy negotiation; all five tools, layered rendering, processing, analysis and rejected invalid calls |
| Cold installation | Empty dependency cache and empty managed-Python directory; Python 3.12 and dependencies downloaded from a read-only source copy; real WAV generated; second startup with `UV_OFFLINE=1` and Python downloads disabled also generated a WAV, without source writes; both project and Claude script launchers tested; Claude cold connection 7.81 seconds and offline reconnection 1.20 seconds on this machine |
| Plugin launch configurations | All three shipped launch configurations start with an offline prepared cache, keep their environment outside the source and write a real WAV |
| Codex | Native catalog discovery and app-server connection; all five tools discovered with schemas and no discovery error |
| Claude Code 2.1.296 | Strict manifest validation; actual 0.1.2 installation from a read-only local marketplace snapshot in an empty test profile; native MCP health check connected through the bundled script in 4.86 seconds with a fresh dependency cache |
| Antigravity 1.5.8 | Google package passed strict validation; actual 0.1.1 plugin installation discovered one skill and one MCP server; a bounded native session generated 4800 frames at 48 kHz through the installed plugin; total session 25.52 seconds with a fresh dependency cache |
| OpenCode 1.19.5 | Native MCP connection reports **Connected**; native skill discovery finds Antipode |

Native client checks ran on macOS. Timings describe this machine and connection, not a guarantee for other machines. CI exercises the Python suite on Linux, macOS and Windows; it does not drive authenticated models. A conversational sound-design session has not been exercised in every host.

The Antigravity test used an existing authenticated session, permitted only the plugin's `generate_sound` tool, wrote to a unique temporary audio workspace and removed the test plugin afterward. Claude used an isolated configuration directory. No login was performed. Marketplace review and approval are separate from these installation checks.

To repeat the cold-install test explicitly (requires network and downloads a fresh Python runtime):

```sh
ANTIPODE_TEST_COLD_INSTALL=1 uv run --locked python -m unittest discover -s tests -p test_integrations.py -v
```

On PowerShell, set `$env:ANTIPODE_TEST_COLD_INSTALL = "1"` first, then run the `uv run` command. Ordinary tests reuse the prepared dependency cache and skip this network test.
