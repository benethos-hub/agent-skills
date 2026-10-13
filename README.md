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

Download this repository, as a ZIP from GitHub or with `git clone`. Then
install each skill you want by its own folder, `<category>/<skill-name>/`. The categories only order this repository, and agents look for a
skill's folder directly in their skills directory, not inside a category.

### Claude in the browser and in Claude Desktop

Pack the skill's folder into a ZIP, so that the archive holds
`<skill-name>/SKILL.md`. Upload it in the settings under Skills. The skill
is then available in your account and is used when a task fits.

### Claude Code

Copy the skill's folder to `~/.claude/skills/` to use it in every project, or to
`.claude/skills/` inside one project.

### Other agents

Copy the skill's folder into the agent's skills directory. Its location differs
from agent to agent and has changed over time, so check the agent's
documentation.

### Updates

An installed skill is a copy and does not update itself. After a change here,
replace the folder or upload the new ZIP.

## Layout

```
agent-skills/
  README.md
  LICENSE
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
  hyphens.
- `description` says what the skill does and when an agent should use it. It is
  the only part an agent reads up front.
- The category's README lists the skill and names what it needs to give a
  useful answer.
- English, no semicolons, no emojis. The answer follows the user's language.
- Gaps in the data are named, not covered up. The skill says what it does not
  do, and the category's README carries the disclaimer for its field.

## Disclaimer

The skills are provided as they are, without warranty. A result can contain
errors, so check it before relying on it. Each category's README adds what
applies to its field.

## License

[MIT](LICENSE)
