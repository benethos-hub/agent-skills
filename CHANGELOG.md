# Changelog

All notable changes to this repository are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The newest version below is the one the next release must carry. Every
`vX.Y.Z` in the other Markdown files has to name it, and the tests check that.

## [Unreleased]

### Added

- The icon next to the title of the README, as `assets/brand/icon.svg` and
  a 512x512 `icon.png` that `assets/render_icon.py` draws from it.
- CI runs the brand check of the organisation, which tests both files.

### Changed

- The categories moved into `skills/`, so a skill now lies in
  `skills/<category>/<skill-name>/`. The ZIPs keep their content, they never
  carried the category. In Claude Code the marketplace on `main` already names
  the new paths, which v0.1.0 does not have, so installs through it work again
  with the next release.
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
