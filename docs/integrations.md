# Connect your agent

Antipode ships one local audio engine, one MCP server and one sound-design skill. Codex, Claude Code and Antigravity can load the plugin bundle. OpenCode connects the same MCP server and skill through its project configuration. No hosted MCP endpoint is involved.

## Prepare once

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
git clone https://github.com/mchl-schrdng/antipode-audio.git
cd antipode-audio
uv sync --locked
uv run --offline antipode presets
```

The checked-in `.python-version` selects Python 3.12. Initial setup may download Python and dependencies. The lockfile fixes dependency versions. Plugin launches then use `--locked --offline` and keep their virtual environment in the host's writable plugin-data directory, outside the plugin source. No network is used by the audio engine.

Keep `uv` on the agent application's PATH. If a desktop app cannot find it, use the source-checkout configuration below, whose command is an absolute Python path. After a dependency upgrade, run `uv sync --locked` again before using offline mode.

Plugin audio goes to `~/.antipode/audio`. This location is outside the plugin installation and survives plugin replacement. The server expands `~` itself. Agents can only address relative WAV paths inside that workspace, and existing files are never replaced. Different agents should use different output names or subdirectories.

## Codex

From the prepared checkout:

```sh
codex plugin marketplace add .
codex plugin add antipode@antipode-local
```

Start a new Codex session and use the Antipode skill. The plugin uses the portable `plugin.json` and `mcp.json` format; `.agents/plugins/marketplace.json` supplies the repository catalog. This is a local desktop/CLI plugin, not a claim of approval in OpenAI's public directory. [Official packaging documentation](https://developers.openai.com/plugins/build/plugins), [local MCP guidance](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

## Claude Code

Try the plugin in one session without installing it globally:

```sh
claude --plugin-dir .
```

Use `/antipode:antipode` or ask Claude to design a sound with Antipode. For a persistent installation:

```sh
claude plugin marketplace add .
claude plugin install antipode@antipode-local
```

The `.claude-plugin/plugin.json` manifest points at `integrations/claude.mcp.json`; paths use Claude's plugin variables. [Official plugin reference](https://code.claude.com/docs/en/plugins-reference).

Once this repository is public, Claude Code versions supporting direct marketplace installation can also use:

```text
/plugin install antipode --marketplace mchl-schrdng/antipode-audio
```

Run the preparation step first: startup deliberately stays offline and fails clearly if dependencies are missing.

## Antigravity

From the prepared checkout:

```sh
agy plugin validate --strict .
agy plugin install .
```

Restart the agent session, then invoke Antipode. The portable manifest uses `mcp.json`; the matching `mcp_config.json` supports versions whose Agent Plugins format is disabled. Both configurations launch the same server. The app can also install the local folder from its plugin interface. [Official plugin installation](https://antigravity.google/docs/plugins), [packaging reference](https://antigravity.google/docs/build-plugins).

## OpenCode

Print a configuration using absolute paths for this checkout:

```sh
uv run --offline python scripts/client_config.py opencode
```

Merge the printed `mcp.servers.antipode` entry and `skills` path into the target project's `opencode.json`. Preserve any existing settings. Then:

```sh
opencode mcp list
```

The server should be connected; `opencode debug skill` should include `antipode`. Start a fresh session and ask for a sound. This uses OpenCode's MCP and skill extension points; it does not install an unrelated JavaScript lifecycle plugin. The config shape targets current OpenCode's `mcp.servers` format. [Official MCP configuration](https://opencode.ai/docs/mcp-servers), [skill configuration](https://opencode.ai/docs/skills).

## Direct MCP configuration

If a host does not support local plugin bundles, keep the prepared checkout and print its MCP configuration:

```sh
uv run --offline python scripts/client_config.py codex
uv run --offline python scripts/client_config.py claude
uv run --offline python scripts/client_config.py antigravity
```

The generator prints TOML for Codex and JSON for the others. It never edits settings. Merge the output into the client's MCP configuration. Copy `skills/antipode` to the host's project skill directory if you also want the sound-design workflow; a direct MCP connection alone exposes the tools and their descriptions.

Use `--workspace /absolute/path/to/project/audio` on the generator to choose another audio directory. Keep the source checkout in place, because these configurations reference its `.venv` interpreter. The main commands also work directly:

```sh
uv run --offline antipode --workspace ./audio generate chime.wav --preset glass
uv run --offline antipode --workspace ./audio render examples/recipes/event-horizon.json atmosphere.wav
uv run --offline antipode --workspace ./audio analyze atmosphere.wav
```

Recipe filenames are ordinary CLI inputs; tool audio paths remain confined to the audio workspace.

## Verification scope

| Surface | Verified on the development machine |
| --- | --- |
| MCP protocol | Real subprocess connections with modern and legacy negotiation; tool discovery, generation, layered rendering, processing, analysis and rejected invalid calls |
| Plugin launch | Every shipped MCP configuration starts offline, uses a separate virtual environment and writes a real WAV; a relocated read-only package also launches from the prepared dependency cache |
| Codex | Native catalog discovery and app-server connection; all five tools discovered with schemas and no discovery error |
| Claude Code | Strict plugin and marketplace validation; native MCP connection reports **Connected** in an isolated test configuration |
| Antigravity 1.5.8 | Strict plugin validation; a bounded native agent session called `generate_sound` through MCP and created a 0.1-second WAV (4800 frames at 48 kHz) |
| OpenCode 1.19.5 | Native MCP connection reports **Connected**; native skill discovery finds Antipode |

These checks do not establish that every model will follow the skill equally well. A logged-in conversational sound-design session has not been exercised in all four products, and native client checks have only run on macOS. The automated Python suite is independent of model accounts.

Antigravity's `agy mcp list` is a catalog command, so the native smoke test used a temporary uniquely named MCP registration and an existing authenticated session. Only its `generate_sound` call was allowed; terminal, file and web actions were denied for that session. The actual WAV was checked, the test registration removed, and the original configuration restored. No login or persistent permission change was made. Installation into each host's permanent plugin cache remains separate from the verified manifest, relocated-package and native-server checks above.
