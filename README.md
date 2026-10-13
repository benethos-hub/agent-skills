# Agent Skills

Skills for AI agents, written to the open [Agent Skills](https://agentskills.io)
standard: one folder per skill with a `SKILL.md`, a header with `name` and
`description`, and the instructions in Markdown below it. An agent reads only
the header first and loads the instructions when a task fits.

The skills are written in English and answer in the language of the user.

**Contents**

- [Categories](#categories)
- [Installing](#installing)
  - [Claude in the browser and in Claude Desktop](#claude-in-the-browser-and-in-claude-desktop)
  - [Claude Code](#claude-code)
  - [Other agents](#other-agents)
  - [Updates](#updates)
- [Releases](#releases)
- [Tests](#tests)
- [Layout](#layout)
  - [Rules for a new skill](#rules-for-a-new-skill)
- [Disclaimer](#disclaimer)
- [License](#license)

## Categories

The skills are ordered by category. Each category has its own README with its
skills, what they need and how to set it up.

| Category | What for | Skills |
|---|---|---|
| [finance](finance/README.md) | Securities and portfolios, calculated from current market data | [asset-analysis](finance/asset-analysis/SKILL.md), [dividend-calendar](finance/dividend-calendar/SKILL.md) |

Some skills only give a useful answer when the agent can reach the right MCP
server. Read the category's README before installing.

## Installing

Every skill is a folder in this repository. Each release also carries every
skill as a ZIP of its own, and the newest one is always reachable under the
same link:

```
https://github.com/benethos-hub/agent-skills/releases/latest/download/<skill-name>.zip
```

The categories only order this repository. Agents look for a skill's folder
directly in their skills directory, not inside a category.

### Claude in the browser and in Claude Desktop

Download the skill's ZIP from the link above and upload it in the settings
under Skills. The skill is then available in your account and is used when a
task fits.

### Claude Code

Add this repository as a plugin marketplace once, then install each skill you
want as a plugin of its own:

```bash
claude plugin marketplace add benethos-hub/agent-skills
claude plugin install dividend-calendar@benethos-agent-skills
```

Without the marketplace, unpack the skill's ZIP into `~/.claude/skills/` to use
it in every project, or into `.claude/skills/` inside one project.

### Other agents

Unpack the skill's ZIP into the agent's skills directory. Its location differs
from agent to agent and has changed over time, so check the agent's
documentation.

### Updates

An installed skill from a ZIP is a copy and does not update itself. Download
the ZIP of the newest release again and replace the old one. In Claude Code,
`claude plugin marketplace update benethos-agent-skills` fetches the newest
state of the marketplace, and `claude plugin update <skill-name>@benethos-agent-skills`
updates an installed skill.

## Releases

The version lives in [CHANGELOG.md](CHANGELOG.md). Its newest heading of the
form `## [X.Y.Z] - YYYY-MM-DD` is the version the next release carries. A
release takes four steps:

1. Move the entries under `[Unreleased]` into a new version section.
2. Run the tests. They name every `vX.Y.Z` in a Markdown file that does not
   match the new version yet. Update those lines.
3. Commit and push to `main`.
4. Publish the release. Its notes are the version's section of the changelog:

   ```bash
   gh release create v0.1.0 --target main \
     --notes "$(python3 .github/scripts/skills.py version --notes)"
   ```

The release workflow then checks that the tag is the version in the
changelog and runs the tests. Only then does it attach one file per skill,
`<skill-name>.zip`, and next to them `skills.json`, an index with each skill's
name, category, description, links, size and SHA-256. GitHub keeps the files
of every release under its tag, so a fixed version stays reachable:

```
https://github.com/benethos-hub/agent-skills/releases/download/v0.1.0/<skill-name>.zip
```

The archives are build results and are never checked in.

`.claude-plugin/marketplace.json` is generated from the skills and checked in,
because Claude Code reads it from the repository. Besides the skills it offers
MCP servers a category needs, each as a plugin of its own. They are listed in
`MCP_PLUGINS` in `.github/scripts/skills.py`.

## Tests

The tests use only the Python standard library and run on every push:

```bash
python3 -m unittest discover -s tests -v
```

They check:

- **Layout.** Every category has a README and holds only skill folders. Every
  skill folder holds only what the standard allows.
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
  index matches them, and the same content gives the same bytes. The workflows
  pin every action to a commit.

External links are only fetched on request, because that needs the network:

```bash
LINKS_ONLINE=1 python3 -m unittest discover -s tests -v
```

## Layout

```
agent-skills/
  README.md
  CHANGELOG.md        # the version and what changed
  LICENSE
  .claude-plugin/
    marketplace.json  # generated, one plugin per skill and per MCP server for Claude Code
  .github/
    scripts/skills.py # checks the skills, packs the ZIPs, writes both JSON files
    workflows/        # CI on every push, the release assets on every release
  tests/              # the checks above, standard library only
  <category>/
    README.md         # the category's skills, what they need, the setup
    <skill-name>/
      SKILL.md        # required: header with name and description, then the instructions
      references/     # optional: longer reference texts the instructions point to
      scripts/        # optional: helper scripts
```

### Rules for a new skill

- It goes into the category that fits, or into a new one with a short English
  name in lower case. A new category gets its own README.md and a row in the
  table above.
- The folder name equals `name` in the header: lower-case letters, digits and
  single hyphens, at most 64 characters. A name is used only once in the whole
  repository, because the ZIPs and plugins carry it without the category.
- `description` says what the skill does and when an agent should use it, in at
  most 1,024 characters. It is the only part an agent reads up front.
- The category's README lists the skill and names what it needs to give a
  useful answer.
- After adding, renaming or changing the header of a skill, regenerate the
  marketplace file with `python3 .github/scripts/skills.py marketplace`.
- English, no semicolons, no emojis. The answer follows the user's language.
- Gaps in the data are named, not covered up. The skill says what it does not
  do, and the category's README carries the disclaimer for its field.

## Disclaimer

The skills are provided as they are, without warranty. A result can contain
errors, so check it before relying on it. Each category's README adds what
applies to its field.

## License

[MIT](LICENSE)
