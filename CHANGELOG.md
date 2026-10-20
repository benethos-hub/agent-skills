# Changelog

All notable changes to this repository are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The newest version below is the one the next release must carry. Every
`vX.Y.Z` in the other Markdown files has to name it, and the tests check that.

## [Unreleased]

### Added

- `dividend-calendar` brings a script that calculates the calendar by the
  skill's fixed rules. The agent passes the fetched data as JSON and takes the
  numbers over unchanged, instead of calculating by hand or writing code of
  its own each time. Without code execution the agent still calculates by the
  rules in the skill. The script needs Python 3.11 or newer and nothing else.

### Changed

- The release runs the dependency audit of `uv.lock` once more before it
  uploads anything, for a vulnerability that became known between the merge
  and the release.

## [0.3.0] - 2026-10-20

Two new categories with a skill each, subcategories with their own bundles,
two ZIP names per skill, and CI on the shared checks of the organisation.

### Added

- A new category `workflow` with the skill `prepare-for-compaction`. It moves
  what only the conversation holds into the agent's memory before a context
  compaction, tidies what the new state replaces and changes no file of the
  project. Claude Code installs it as the bundle `workflow` or as a plugin of
  its own.
- A new category `development` with the subcategory `git` and the skill
  `commit`. It commits in small steps, each passing the project's own checks,
  on the branch the change belongs to, for any language. Push, pull request
  and merge wait for the user's word. Claude Code installs it as the bundle
  `development`, the bundle `development-git` or a plugin of its own.
- A category can order its skills into subcategories. Each subcategory has a
  README and a bundle `<category>-<subcategory>` in Claude Code, and
  `skills.json` names the subcategory of every skill.
- The README opens with the badge rows of the organisation: CI, coverage and
  licence, the latest release, and the sponsor links. CI writes the coverage
  badge on every push to `main`, to the branch `badges`. The README of each
  category opens with the icon and the same badge rows.

### Changed

- A release carries each skill twice, with the same bytes:
  `<skill-name>.zip` for the stable link to the newest release and
  `<skill-name>-X.Y.Z.zip`, which shows on disk which version it is.
  `skills.json` links the versioned name as the fixed one.
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
