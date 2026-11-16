# Third-party notices

Runtime inventory from the locked macOS ARM64 / Python 3.12 installation on 13 November 2026.

Antipode does not vendor these packages in its source or wheel. Installers obtain them separately; their own copyright notices and license terms remain in the installed distributions. This table reports package metadata, not a substitute for the full licenses or a worldwide legal opinion.

| Distribution | Version checked | Declared license |
| --- | --- | --- |
| `annotated-types` | `0.8.0` | MIT |
| `anyio` | `4.16.0` | MIT |
| `attrs` | `26.1.0` | MIT |
| `cffi` | `2.1.1` | MIT-0 |
| `click` | `8.5.1` | BSD-3-Clause |
| `cryptography` | `50.0.2` | Apache-2.0 OR BSD-3-Clause |
| `h11` | `0.16.0` | MIT |
| `httpcore2` | `2.16.0` | BSD-3-Clause |
| `httpx2` | `2.16.0` | BSD-3-Clause |
| `idna` | `3.20` | BSD-3-Clause |
| `jsonschema` | `4.26.0` | MIT |
| `jsonschema-specifications` | `2025.9.1` | MIT |
| `mcp` | `2.3.0` | MIT |
| `mcp-types` | `2.3.0` | MIT |
| `numpy` | `2.5.4` | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| `opentelemetry-api` | `1.45.2` | Apache-2.0 |
| `pycparser` | `3.12` | BSD-3-Clause |
| `pydantic` | `2.14.3` | MIT |
| `pydantic_core` | `2.50.4` | MIT |
| `PyJWT` | `2.15.1` | MIT |
| `python-multipart` | `0.0.33` | Apache-2.0 |
| `referencing` | `0.37.0` | MIT |
| `rpds-py` | `2026.9.1` | MIT |
| `sse-starlette` | `3.7.0` | BSD-3-Clause |
| `starlette` | `1.10.0` | BSD-3-Clause |
| `truststore` | `0.10.5` | MIT |
| `typing-inspection` | `0.4.5` | MIT |
| `typing_extensions` | `4.16.0` | PSF-2.0 |
| `uvicorn` | `0.54.0` | BSD-3-Clause |

## Direct dependencies

- **NumPy:** vectorized synthesis, mixing and DSP. Its checked macOS wheel also identifies OpenBLAS (BSD-3-Clause), LAPACK (BSD-3-Clause-Open-MPI), the GCC runtime (GPL-3.0-or-later WITH GCC-exception-3.1), and libquadmath (LGPL-2.1-or-later). These are not all captured by the top-level metadata expression. Preserve the complete `numpy-*.dist-info/licenses/` directory and review the actual bundle's obligations when redistributing that wheel or a bundled application. The current Antipode source/wheel does not contain these native libraries.
- **MCP Python SDK:** standard stdio server and client protocol. The SDK and `mcp-types` use MIT; the installed SDK pulls its own transport, schema and cryptographic dependencies.

## Distribution boundaries

The `uv.lock` file pins exact versions and artifacts. Python itself, uv, Git, the host coding agents and build tools are separately licensed products; they are not relicensed by Antipode. The plugin does not bundle third-party fonts, images, recordings or neural model weights.

If distributing a frozen executable, container, wheelhouse or copied environment in future, collect all platform-specific notices and any source/offer obligations from that actual bundle. Do not treat this source-only inventory as clearance for a different distribution.

The repository contains Apache-2.0 and CC0-1.0 legal texts for its own materials. See [rights.md](docs/rights.md) for scope and exclusions.
