# <img src="https://raw.githubusercontent.com/benethos-hub/agent-skills/main/assets/brand/icon.svg" alt="" width="40" height="40"> Development skills

[![CI](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/benethos-hub/agent-skills/badges/coverage.json&logo=githubactions&logoColor=white)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/benethos-hub/agent-skills?logo=opensourceinitiative&logoColor=white)](https://github.com/benethos-hub/agent-skills/blob/main/LICENSE)

[![Release](https://img.shields.io/github/v/release/benethos-hub/agent-skills?label=Release&logo=github&logoColor=white)](https://github.com/benethos-hub/agent-skills/releases/latest)

[![Sponsor](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/sponsor.svg)](https://github.com/sponsors/BeneODev)
[![PayPal](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/paypal.svg)](https://paypal.me/BeneODev)

Skills for working in a repository with an agent, in any language. They
follow the project's own rules and checks, and they leave pushing, merging
and releasing to you.

**Contents**

- [Subcategories](#subcategories)
- [Installing](#installing)
- [What the skills need](#what-the-skills-need)
- [Disclaimer](#disclaimer)

## Subcategories

The skills are ordered by what they work on. Each subcategory has its
own README with its skills and how to use them.

| Subcategory | What for | Skills |
|---|---|---|
| [git](git/README.md) | Commits in small, checked steps on the right branch | [commit](git/commit/SKILL.md) |
| [review](review/README.md) | A checked review written as work packages, and building it branch by branch | [review](review/review/SKILL.md), [work-through-review](review/work-through-review/SKILL.md) |
| [maintenance](maintenance/README.md) | Packages, images, CI actions and the runtime kept current, each bump measured and checked | [refresh-dependencies](maintenance/refresh-dependencies/SKILL.md) |

## Installing

In Claude Code one command brings every development skill:

```bash
claude plugin marketplace add benethos-hub/agent-skills
claude plugin install development@benethos-agent-skills
```

Smaller choices are the bundle of a subcategory, such as `development-git`,
or single skills. The README of each subcategory names both.

Take one of the three: the bundle of the category, the bundles of
subcategories, or single skills. A skill that comes from two of them is
loaded twice.

For every other client, the ZIP downloads and updates work the same for all
skills of this repository. The [main README](../../README.md#installing)
covers them.

## What the skills need

A shell with git, and the tools the project itself uses for its checks, such
as its package manager or task runner. The skills find those checks in the CI
configuration, a task runner or the project's instruction files, such as
`AGENTS.md` or `CLAUDE.md`. For pull requests and merges they use the command
line of the hosting service, for example `gh` for GitHub.

In claude.ai and Claude Desktop the agent has no access to your repository.
The skills can then only describe the steps.

## Disclaimer

The skills follow the project's rules and checks as far as they find them. A
green check is not a review. Look at the commits before you push them.
