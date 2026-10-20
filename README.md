# <img src="https://raw.githubusercontent.com/benethos-hub/agent-skills/main/assets/brand/icon.svg" alt="" width="40" height="40"> Agent Skills

[![CI](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/benethos-hub/agent-skills/badges/coverage.json&logo=githubactions&logoColor=white)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/benethos-hub/agent-skills?logo=opensourceinitiative&logoColor=white)](https://github.com/benethos-hub/agent-skills/blob/main/LICENSE)

[![Release](https://img.shields.io/github/v/release/benethos-hub/agent-skills?label=Release&logo=github&logoColor=white)](https://github.com/benethos-hub/agent-skills/releases/latest)

[![Sponsor](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/sponsor.svg)](https://github.com/sponsors/BeneODev)
[![PayPal](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/paypal.svg)](https://paypal.me/BeneODev)

Skills for AI agents, written to the open [Agent Skills](https://agentskills.io)
standard: one folder per skill with a `SKILL.md`, a header with `name` and
`description`, and the instructions in Markdown below it. An agent reads only
the header first and loads the instructions when a task fits.

The skills are written in English and answer in the language of the user.

**Contents**

- [Categories](#categories)
- [Installing](#installing)
  - [Claude Code](#claude-code)
  - [Claude in the browser and in Claude Desktop](#claude-in-the-browser-and-in-claude-desktop)
  - [Other agents](#other-agents)
  - [Updates](#updates)
- [Maintaining](#maintaining)
  - [Releases](#releases)
  - [How Claude Code finds the marketplace](#how-claude-code-finds-the-marketplace)
  - [Tests](#tests)
  - [Layout](#layout)
  - [Rules for a new skill](#rules-for-a-new-skill)
- [Disclaimer](#disclaimer)
- [License](#license)

## Categories

The skills live in [skills/](skills/), ordered by category. Each category has
its own README with its skills, what they need and how to set it up.

| Category | What for | Skills |
|---|---|---|
| [finance](skills/finance/README.md) | Securities and portfolios, calculated from current market data | [asset-analysis](skills/finance/asset-analysis/SKILL.md), [dividend-calendar](skills/finance/dividend-calendar/SKILL.md) |
| [workflow](skills/workflow/README.md) | Long working sessions with an agent, kept safe across a context compaction | [prepare-for-compaction](skills/workflow/prepare-for-compaction/SKILL.md) |

Some skills only give a useful answer when the agent can reach the right MCP
server. The category's README says which one and how to connect it.

## Installing

The shortest way depends on the client:

| Client | Shortest way |
|---|---|
| Claude Code | Add the marketplace, then install the bundle of a category. Two commands, MCP servers included. |
| claude.ai and Claude Desktop | Download the skill's ZIP and upload it under Settings, Skills. |
| Other agents | Unpack the skill's ZIP into the agent's skills directory. |

Every release carries each skill as a ZIP of its own. The README of each
category or subcategory links them directly. The newest one is always
reachable under the same link:

```
https://github.com/benethos-hub/agent-skills/releases/latest/download/<skill-name>.zip
```

For a fixed version, every release on the
[releases page](https://github.com/benethos-hub/agent-skills/releases) also
carries each ZIP under a name with its version, `<skill-name>-X.Y.Z.zip`.

### Claude Code

1. Add this repository as a plugin marketplace. This is needed once:

   ```bash
   claude plugin marketplace add benethos-hub/agent-skills
   ```

2. Install the bundle of a category. It brings every skill of the category
   and the MCP servers they work with:

   ```bash
   claude plugin install finance@benethos-agent-skills
   ```

   A category with subcategories also has a bundle per subcategory, named
   `<category>-<subcategory>`. To pick single skills instead, install each as
   a plugin of its own:

   ```bash
   claude plugin install dividend-calendar@benethos-agent-skills
   ```

Take one of these for a category: its bundle, the bundles of its
subcategories, or single skills. A skill that comes from two of them is
loaded twice.

Claude Code installs the state of the newest release, the same the ZIPs carry.
Changes on `main` that are not released yet do not reach it.

Without the marketplace, unpack a skill's ZIP into `~/.claude/skills/` to use
it in every project, or into `.claude/skills/` inside one project. MCP servers
are then set up by hand, as the category's README describes.

### Claude in the browser and in Claude Desktop

1. Download the skill's ZIP. The category's README has a direct link for each
   skill.
2. Upload it in the settings under Skills. The skill is then available in your
   account and is used when a task fits.
3. Connect the MCP server the skill needs, as the category's README
   describes.

### Other agents

Unpack the skill's ZIP into the agent's skills directory. The ZIP holds the
skill's folder, ready to use. Agents look for a skill's folder directly in
that directory, not inside a category. Where the directory lies differs from
agent to agent and has changed over time, so check the agent's documentation.

### Updates

In Claude Code, fetch the newest state of the marketplace, then update what
you installed:

```bash
claude plugin marketplace update benethos-agent-skills
claude plugin update finance@benethos-agent-skills
```

A skill from a ZIP is a copy and does not update itself. Download the ZIP of
the newest release again and replace the old one.

## Maintaining

This part is for whoever changes the repository. Everything here runs with
[uv](https://docs.astral.sh/uv/getting-started/installation/). The test tools
are locked in `uv.lock`, and `.github/scripts/skills.py` needs the standard
library only.

### Releases

The version lives in [CHANGELOG.md](CHANGELOG.md). Its newest heading of the
form `## [X.Y.Z] - YYYY-MM-DD` is the version the next release carries. A
release takes five steps:

1. Move the entries under `[Unreleased]` into a new version section.
2. Regenerate the marketplace file, which points Claude Code to the new tag:
   `uv run .github/scripts/skills.py marketplace`.
3. Run the tests. They name every `vX.Y.Z` in a Markdown file that does not
   match the new version. Update those lines.
4. Merge into `main` through a pull request.
5. Publish the release right after the merge. Until then the marketplace on
   `main` names a tag that does not exist yet, and installs in Claude Code
   fail. The tag and the release notes both come from the changelog:

   ```bash
   gh release create "v$(uv run .github/scripts/skills.py version)" --target main \
     --notes "$(uv run .github/scripts/skills.py version --notes)"
   ```

The release workflow then checks, through the organisation's gate, that CI
passed on the release commit on `main`, and that the tag is the version in
the changelog. Only then does it attach two files per skill with the same
bytes. `<skill-name>.zip` carries no version and gives the stable link to the
newest release. `<skill-name>-X.Y.Z.zip` shows on disk which version it is.
Next to them goes `skills.json`, an index with each skill's name, category,
description, links, size and SHA-256. GitHub keeps the files of every release
under its tag, so a fixed version stays reachable:

```
https://github.com/benethos-hub/agent-skills/releases/download/vX.Y.Z/<skill-name>-X.Y.Z.zip
```

Releases up to 0.2.0 carry only `<skill-name>.zip`. Their fixed link is
`releases/download/vX.Y.Z/<skill-name>.zip`.

The archives are build results and are never checked in.

### How Claude Code finds the marketplace

Claude Code looks for the marketplace in one fixed place,
`.claude-plugin/marketplace.json`. Adding the marketplace clones the
repository and reads that file. Its `name` field, `benethos-agent-skills`, is
the part after the `@` in every install command. The repository's name plays
no part there.

The file is read from `main`. Each plugin in it takes its files from the
release tag it names. That is why the file has to name the new tag before a
release, and why the release follows the merge right away.

The file is generated from the skills and never edited by hand. It holds one
plugin per skill, one bundle per category, one bundle per subcategory named
`<category>-<subcategory>` and each MCP server on its own. A bundle carries
every skill of its category or subcategory and the MCP servers listed for
that category in `MCP_PLUGINS` in `.github/scripts/skills.py`. CI fails when
the file no longer matches the skills.

### Tests

CI runs the shared checks of the organisation on every push and pull
request, from `benethos-hub/.github`: lint, the tests on Python 3.11 to 3.15,
an audit of `uv.lock` and the brand check. Next to them it packs every skill.
Locally the same runs with:

```bash
uv run pytest                                 # the tests
uv run ruff check . && uv run ruff format --check . && uv run mypy   # lint
```

The newest Python version also measures the coverage of
`.github/scripts/skills.py`, with a floor of 80 percent. The tests check:

- **Layout.** `skills/` holds only categories, and every `SKILL.md` lies in
  one of them. Every category holds either skill folders or subcategories,
  never both, and every category and subcategory has a README. Every skill
  folder holds only what the standard allows.
- **Headers.** Name, description and the other fields follow the Agent Skills
  specification. Names are unique in the whole repository.
- **Consistency.** The READMEs list every category and skill with its download
  link and install command. The marketplace file matches the skills.
- **Markdown.** Every relative link and every anchor resolves. Each
  **Contents** list names the headings in order. No semicolons, no em or en
  dashes, no emojis in the text.
- **Version.** The changelog is in order, and every `vX.Y.Z` in a Markdown file
  is its newest version.
- **Delivery.** The ZIPs hold one folder each and leave out test material, the
  index matches them, and the same content gives the same bytes on every
  machine. The workflows run Python through uv and pin every action to a
  commit, except the shared workflows of the organisation, which follow its
  `main`.
- **Command line.** `skills.py` packs, writes and checks the marketplace file
  and names the version as the workflows and this README call it.

External links are only fetched on request, because that needs the network:

```bash
LINKS_ONLINE=1 uv run pytest
```

### Layout

```
agent-skills/
  README.md
  CHANGELOG.md        # the version and what changed
  LICENSE
  pyproject.toml      # the test tools and their settings, no package
  uv.lock             # the locked test tools, kept current by Dependabot
  assets/
    brand/            # icon.svg, icon.png 512x512, social-preview.png 1280x640
    render_brand.py   # draws both PNGs from icon.svg: uv run assets/render_brand.py
  .claude-plugin/
    marketplace.json  # generated, for Claude Code: one plugin per skill, bundle and MCP server
  .github/
    scripts/skills.py # checks the skills, packs the ZIPs, writes both JSON files
    workflows/        # CI on every push, the release assets on every release
  tests/              # the checks above, run with uv run pytest
  skills/
    <category>/
      README.md       # the category's skills, what they need, the setup
      <skill-name>/
        SKILL.md      # required: header with name and description, then the instructions
        references/   # optional: longer reference texts the instructions point to
        scripts/      # optional: helper scripts
    <category>/       # a category with subcategories instead of skills
      README.md       # its subcategories, what they need, the setup
      <subcategory>/
        README.md     # its skills, their downloads and install commands
        <skill-name>/
          SKILL.md
```

### Rules for a new skill

- It goes into the category under `skills/` that fits, or into a new one with
  a short English name in lower case. A new category gets its own README.md
  and a row in the table above. The first paragraph of that README becomes
  the description of the category's bundle in Claude Code.
- A category can order its skills into subcategories, such as
  `development/git/`, when it holds many of them. It then holds only
  subcategories, no skill folders beside them. Each subcategory gets a
  README.md whose first paragraph describes its bundle, and the category's
  README links it.
- The folder name equals `name` in the header: lower-case letters, digits and
  single hyphens, at most 64 characters. A name is used only once in the whole
  repository, because the ZIPs and plugins carry it without the category.
- `description` says what the skill does and when an agent should use it, in at
  most 1,024 characters. It is the only part an agent reads up front.
- The README of the category or subcategory the skill lies in lists it with
  its download link and install command, and names what it needs to give a
  useful answer.
- After adding, renaming or changing the header of a skill, regenerate the
  marketplace file with `uv run .github/scripts/skills.py marketplace`.
- English, no semicolons, no emojis. The answer follows the user's language.
- Gaps in the data are named, not covered up. The skill says what it does not
  do, and the category's README carries the disclaimer for its field.

## Disclaimer

The skills are provided as they are, without warranty. A result can contain
errors, so check it before relying on it. Each category's README adds what
applies to its field.

## License

[MIT](LICENSE)
