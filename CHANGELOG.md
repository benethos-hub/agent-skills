# Changelog

All notable changes to this repository are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The newest version below is the one the next release must carry. Every
`vX.Y.Z` in the other Markdown files has to name it, and the tests check that.

## [Unreleased]

### Changed

- CI runs the shared checks of the organisation: lint with Ruff and Mypy, the
  tests on Python 3.11 to 3.15 with a coverage floor of 80 percent, and an
  audit of the locked tools. The release uploads nothing unless CI passed on
  its commit on `main`, checked by the organisation's gate.
- Python runs through uv everywhere. `pyproject.toml` and `uv.lock` hold the
  test tools, Dependabot keeps them current, and `skills.py` declares in its
  header that it needs the standard library only. The tests run with
  `uv run pytest` and cover the command line of `skills.py` as well.

## [0.2.0] - 2026-10-13

A bundle per category for Claude Code, the skills under `skills/`, the
brand assets, and READMEs that lead with the shortest way.

### Added

- The icon next to the title of the README, as `assets/brand/icon.svg` and
  a 512x512 `icon.png` drawn from it.
- A 1280x640 `assets/brand/social-preview.png`, the image GitHub shows when
  the repository link is shared. `assets/render_brand.py` draws both PNGs
  from the SVG.
- CI runs the brand check of the organisation, which tests both files.
- A bundle per category in the Claude Code marketplace. `finance` installs
  both finance skills and the market-data server with one command. The
  single plugins stay.

### Changed

- The READMEs start with the shortest way for each client and give the
  steps as numbered lists. The finance README has a quick start. The main
  README keeps what concerns maintainers under its own heading and explains
  how Claude Code finds the marketplace.
- The categories moved into `skills/`, so a skill now lies in
  `skills/<category>/<skill-name>/`. The ZIPs keep their content, they never
  carried the category. Installs through the Claude Code marketplace, which
  failed between the move and this release, work again.
- The ZIPs store their files without compression. Deflate output depends on
  the zlib build, so the same content gave other bytes and another SHA-256 on
  another Python version or platform. Stored, it gives the same bytes
  everywhere.

## [0.1.0] - 2026-10-13

The first release, with two finance skills and a delivery for every client.

### Added

- `finance/asset-analysis`: an analysis of a single security from current
  market data, with own calculations, data traps checked and an assessment by
  horizon.
- `finance/dividend-calendar`: a dividend calendar for a portfolio by fixed
  rules, paid and forecast kept apart, with a list of gaps.
- One ZIP per skill and an index `skills.json` on every release, for upload
  to claude.ai and Claude Desktop.
- A Claude Code marketplace with one plugin per skill, each taken from the
  release tag, and the plugin `benethos-yahoo-finance-mcp` for the market
  data.
- Tests for the layout, the skill headers, links, tables of contents, the text
  rules, the packaging and the workflows.
