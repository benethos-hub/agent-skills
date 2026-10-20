# <img src="https://raw.githubusercontent.com/benethos-hub/agent-skills/main/assets/brand/icon.svg" alt="" width="40" height="40"> Git skills

[![CI](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/benethos-hub/agent-skills/badges/coverage.json&logo=githubactions&logoColor=white)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/benethos-hub/agent-skills?logo=opensourceinitiative&logoColor=white)](https://github.com/benethos-hub/agent-skills/blob/main/LICENSE)

[![Release](https://img.shields.io/github/v/release/benethos-hub/agent-skills?label=Release&logo=github&logoColor=white)](https://github.com/benethos-hub/agent-skills/releases/latest)

[![Sponsor](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/sponsor.svg)](https://github.com/sponsors/BeneODev)
[![PayPal](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/paypal.svg)](https://paypal.me/BeneODev)

Skills for git in any project: commits in small, checked steps on the branch
a change belongs to. Pushing, merging and releasing stay with you.

**Contents**

- [Skills](#skills)
- [Installing](#installing)
- [Using commit](#using-commit)
- [Privacy](#privacy)

## Skills

| Skill | What for | Needs |
|---|---|---|
| [commit](commit/SKILL.md) | Commits in small steps, each one passing the project's own checks, on the branch its subject belongs to, with the message written from the diff | git, the project's tools |

## Installing

In Claude Code the bundle `development-git` brings every skill of this
subcategory:

```bash
claude plugin install development-git@benethos-agent-skills
```

Each skill also comes on its own:

| Skill | Download | Claude Code |
|---|---|---|
| commit | [commit.zip](https://github.com/benethos-hub/agent-skills/releases/latest/download/commit.zip) | `claude plugin install commit@benethos-agent-skills` |

The steps are the same for every skill. The
[development README](../README.md#installing) says what the skills need, and
the [main README](../../../README.md#installing) covers each client.

## Using commit

Ask for a commit in your own words, such as "commit this" or "split this into
commits". When the project's rules say to commit after each step, the skill
applies on its own. Write those rules into the project's instruction file,
such as `AGENTS.md` or `CLAUDE.md`: when to commit, the message style, the
trailer, what goes into the changelog. Without them the skill commits only
when you ask.

The skill decides the branch by the subject of the change. Fixes and docs for
the work at hand go onto the current branch. A new feature gets a new branch
from the main line, and the agent says so before it starts. It never commits
onto a protected main line or onto a branch whose pull request is merged.

Every commit holds one change and passes the same checks as CI. The skill
finds them in the CI configuration, a task runner or the instruction files,
and does not switch off a failing check to get a commit through. It stops
after the commit and reports. Push, pull request and merge each wait for your
word, and a permission to merge covers only the pull request you named.

To check the setup, change something small and say "Commit this". The agent
should name the branch, run the project's checks, commit with a message that
describes the change, and stop. Nothing is pushed.

## Privacy

The skill searches each staged change for secrets, private paths and private
addresses before it commits, and checks the ignore rules for new files. What
reaches a pushed history stays there, so the check comes first.
