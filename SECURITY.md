# Security and privacy

Antipode is a local stdio MCP server, not a public network service. Audio tools
return file paths and measurements, not uploaded audio. No telemetry or cloud
audio API is configured by this project. Installing dependencies needs network
access; the prepared runtime can operate offline. Your coding agent has its own
data and network policies and may send prompts, recipes and tool results to its
provider.

Audio operations accept relative WAV paths within the configured workspace,
reject traversal and symlinks, bound file size and render duration, and never
replace an existing output. Complete files are published atomically so two
processes cannot overwrite the same destination. Use separate filenames per
agent or variation.

These checks are not an operating-system sandbox. Use a workspace you control,
not a directory where hostile local processes can swap directories or links
during a call. The MCP process inherits the permissions of the user who runs it.
Use your host agent's permissions and OS isolation where stronger separation is
needed. Do not expose this server through an untrusted network wrapper.

Report suspected vulnerabilities through
[GitHub private vulnerability reporting](https://github.com/mchl-schrdng/antipode-audio/security/advisories/new),
which is enabled for this repository. Avoid posting sensitive audio, local paths, credentials or
exploit details in a public issue.
