# Gemini CLI extension distribution

The Gemini CLI extension is prepared for a source-only `gemini-v0.1.2` release.
Gallery discovery has not yet been confirmed. It is separate from
the historical Antigravity submission; no new Antigravity form is involved.

| Field | Value |
| --- | --- |
| Extension | Antipode / `antipode` |
| Publisher | `mchl-schrdng` |
| Engine version | `0.1.2` |
| Gemini release tag | `gemini-v0.1.2` |
| Source | https://github.com/mchl-schrdng/antipode-audio |
| Website | https://antipode.quest |
| Support | https://antipode.quest/support/ |
| Contact | mchl.schrdng@gmail.com |
| Privacy | https://antipode.quest/privacy/ |

## Install and review

Install Gemini CLI, Git and uv, then:

```sh
gemini extensions install https://github.com/mchl-schrdng/antipode-audio
gemini extensions list
gemini skills list --all
gemini mcp list
```

The native installer presents the extension's permissions. Restart the session
after installation. Antipode should appear as an extension and skill, and its
MCP server should be connected. Ask for a short original sound, then check the
returned WAV and its level measurements. Full setup and troubleshooting are in
[the integration guide](../integrations.md#gemini-cli).

`gemini-extension.json` is at the repository root, alongside `GEMINI.md`. It
loads the existing skill and runs the bundled, locked Python bootstrap over
stdio. First startup may download Python and dependencies; audio generation
then works offline. No hosted MCP service, audio API, neural audio model or
Antipode account is involved. WAV access remains confined to the configured
audio workspace and existing files are never replaced.

Gemini support was added after v0.1.2 was released. That tag and its six release
assets remain unchanged and do not include the Gemini manifest. The separate
`gemini-v0.1.2` release contains the extension, with the unchanged 0.1.2 engine.
Add `--ref gemini-v0.1.2` to the install command to pin it.

## Verification

On 2026-11-13, Gemini CLI 0.64.0 installed a local source snapshot into an empty
`GEMINI_CLI_HOME`. Native commands discovered the context, skill and MCP server,
then reported **Connected**, including with uv forced offline. A separate MCP
protocol client used the installed launch command to discover all five tools and
generate a 4800-frame, 48 kHz WAV. Installed files were read-only and their hashes
did not change. The test used a temporary audio workspace, with no login or
changes to the user's Gemini settings. It did not run a Gemini model conversation
or test the public GitHub installation before publication.

## Gallery publication

Google's [official release guide](https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/releasing.md)
describes automatic discovery. After reviewing and pushing these files:

1. Keep the GitHub repository public and the manifest at its absolute root.
2. Publish `gemini-v0.1.2` from the reviewed commit as the latest GitHub release,
   with no attached assets. Gemini uses GitHub's generated source archive when
   there are no custom assets. The source archive includes the root manifest.
3. Verify the plain install command above in an empty Gemini profile. Do this
   before adding the gallery topic: the previous default installer selected
   v0.1.2, which lacks the Gemini manifest, and failed.
4. Add the repository topic `gemini-cli-extension`.
5. Allow the daily crawler to validate and index the extension, then check the
   [Gemini CLI gallery](https://geminicli.com/extensions/). A topic alone is not
   evidence of a live listing or Google endorsement.

If discovery has not happened after 24–48 hours, check GitHub Code Search:

```sh
gh api 'search/code?q=repo:mchl-schrdng/antipode-audio+filename:gemini-extension.json' --jq .total_count
```

A zero count can mean GitHub has not indexed the new manifest. The official guide
explains how to inspect indexing before waiting for the next gallery crawl. No
email or submission form is required for this route.
