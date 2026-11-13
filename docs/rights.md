# Rights, provenance and release boundaries

Review date: **13 November 2026**. This records the project's technical choices
and license terms. It is not a legal clearance opinion or a guarantee of
non-infringement in every jurisdiction.

## What is in the instrument

Antipode synthesizes waveforms and seeded noise using mathematical DSP. The
repository contains no sample pack, recording scraped from the internet, model
weights, training dataset, voice clone, or artist-specific model. The bundled
sound studies are rendered from the included JSON recipes. The orbital logo was
supplied by the project owner as an editable SVG; the bundled mark, icon and cover
adapt its first animation frame. The site graphics remain editable vectors/code,
and no downloaded font is required. Code and creative decisions were developed
with AI coding assistance. This provenance record does not establish trademark
clearance.

The host agent interprets the user's brief and chooses parameters. Antipode itself
does not call a generative audio service. This removes sample/model licensing
dependencies from the supplied synthesis path; it does not establish that any
possible user composition is legally exclusive or free of third-party rights.

## Software and sounds have different terms

| Material | Terms |
| --- | --- |
| Original code, docs, site and vector artwork | [Apache-2.0](../LICENSE) |
| Bundled example recordings and recipes | [CC0-1.0](../examples/LICENSE), only to the extent the contributors hold rights |
| Python dependencies and bundled native libraries | Their own notices, listed in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) |
| User-created output | Antipode claims no ownership or royalty and requires no attribution for the audio alone |
| User-supplied recordings, compositions, lyrics, brands or likenesses | Rights remain the user's responsibility; processing does not grant permission |
| Antipode and third-party brand names | No trademark license or clearance is implied |

Commercial use of the software is permitted subject to Apache-2.0. Redistributing
the software requires preserving its applicable license and notices; modifying
it requires identifying changes. These software obligations are not automatically
attached to a WAV merely because the tool rendered it. See the
[Apache license](https://www.apache.org/licenses/LICENSE-2.0).

CC0 does not clear other people's trademarks, privacy or publicity rights. Its
dedication and fallback license operate only over rights held by the person making
it. See the [CC0 deed and legal code](https://creativecommons.org/publicdomain/zero/1.0/).

Do not treat this tool as permission to reproduce a recognizable protected melody,
recording or third-party sonic logo. No voice cloning is included. A deterministic
recipe can also produce the same audio for multiple people; uniqueness is not
promised. Copyright protection itself depends on the work, human contribution and
jurisdiction. The [US Copyright Office's AI materials](https://www.copyright.gov/ai/)
address human authorship in the United States, not a worldwide guarantee.

## Name and domain: unresolved clearance

**Antipode is a working product name, not a cleared or registered trademark.**
Preliminary public-source research found nearby existing uses:

- [Antipodes Audio](https://antipodes.audio/) markets digital audio hardware and software.
- Aion FX documents an [Antipode Vintage Fuzz](https://aionfx.com/app/files/docs/antipode_documentation.pdf) audio effect.
- The developer already has a separate repository named `antipode`; this project
  lives in `antipode-audio` and does not replace it.

These findings are not a conclusion about infringement or registration. No complete
search of pending, registered, unregistered, phonetic or visual marks has been
performed. Before treating the name/logo as legally cleared, have a qualified
trademark professional review relevant territories, similar marks, and goods and
services (including software, audio tools and associated services). The
[INPI availability guidance](https://www.inpi.fr/disponibilite-dune-marque-dun-logo-dun-nom-de-societe-dun-nom-de-domaine)
and [WIPO availability guidance](https://www.wipo.int/en/web/madrid-system/check-availability)
explain why an identical-name lookup alone is insufficient.

The project owner's Vercel account controls `antipode.quest`. The domain was
connected to the production listening room and verified over HTTPS on the review
date. Domain control does not grant trademark rights. No domain purchase or
trademark filing is part of this release.

## Reproducibility and dependency review

The repository includes the sound recipes and a locked dependency graph. Record
the Git revision, recipe, seed and runtime when exporting material for a release.
DSP changes, NumPy versions and hardware floating-point behavior can affect exact
sample bytes; do not promise byte-identical results across arbitrary environments.

Installed runtime dependencies were inventoried on the review date; their license
metadata is in THIRD_PARTY_NOTICES.md. A dependency vulnerability scan is recorded
in [verification.md](verification.md). Such checks do not replace a license audit,
patent analysis, a trademark search or review of material supplied by a user.
