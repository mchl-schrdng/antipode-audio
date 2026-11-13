# Contributing

Use English for code, documentation, issues and pull requests.

1. Install Python 3.12 and uv, then run `uv sync --locked`.
2. Make the smallest complete change and add a test for new audio or safety behavior.
3. Run `uv run python -m unittest discover -s tests -v` and `uv build`.
4. Describe the audible or observable change, checks, and limitations in your PR.

Keep audio synthesis local and deterministic for a supplied recipe and seed. New
dependencies need a concrete purpose and a license review. Do not contribute
samples, model weights, copied melodies, artist imitation presets, third-party
logos or material you cannot license. Include provenance for new sound studies.

Contributions to code/documentation use Apache-2.0. Contributions to the bundled
example recordings/recipes use their stated CC0 dedication; do not submit them
without the authority to do so. Read [rights.md](docs/rights.md).
