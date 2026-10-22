# <img src="https://raw.githubusercontent.com/benethos-hub/agent-skills/main/assets/brand/icon.svg" alt="" width="40" height="40"> Maintenance skills

[![CI](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/benethos-hub/agent-skills/badges/coverage.json&logo=githubactions&logoColor=white)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/benethos-hub/agent-skills?logo=opensourceinitiative&logoColor=white)](https://github.com/benethos-hub/agent-skills/blob/main/LICENSE)

[![Release](https://img.shields.io/github/v/release/benethos-hub/agent-skills?label=Release&logo=github&logoColor=white)](https://github.com/benethos-hub/agent-skills/releases/latest)

[![Sponsor](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/sponsor.svg)](https://github.com/sponsors/BeneODev)
[![PayPal](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/paypal.svg)](https://paypal.me/BeneODev)

Skills for keeping a project current in any language: packages, container
images, CI actions and the runtime, each measured at its source and checked.
What you excluded stays as it is, and pushing, merging and releasing stay with
you.

**Contents**

- [Skills](#skills)
- [Installing](#installing)
- [Using refresh-dependencies](#using-refresh-dependencies)
- [Privacy](#privacy)

## Skills

| Skill | What for | Needs |
|---|---|---|
| [refresh-dependencies](refresh-dependencies/SKILL.md) | Refreshes every pin of a project, from the lock file to the base images, CI actions and runtime, and checks each bump the way its kind needs | git, the project's tools, network access to the registries |

## Installing

In Claude Code the bundle `development-maintenance` brings every skill of this
subcategory:

```bash
claude plugin install development-maintenance@benethos-agent-skills
```

Each skill also comes on its own:

| Skill | Download | Claude Code |
|---|---|---|
| refresh-dependencies | [refresh-dependencies.zip](https://github.com/benethos-hub/agent-skills/releases/latest/download/refresh-dependencies.zip) | `claude plugin install refresh-dependencies@benethos-agent-skills` |

The steps are the same for every skill. The
[development README](../README.md#installing) says what the skills need, and
the [main README](../../../README.md#installing) covers each client.

## Using refresh-dependencies

Ask in your own words, such as "deps refresh", "update the dependencies" or
"what is outdated here?". The skill looks at everything the project pins:
lock files and manifests, the base images of every Dockerfile, images in
compose files, CI actions and job images, the runtime version and tools
pinned in scripts. It reads each newest version from the registry or the
release list of its project. It does not wait for a dependency bot.

Write down what must not change, and the skill leaves it alone. It reads the
project's instruction files, such as `AGENTS.md` or `CLAUDE.md`, the agent's
memory, the configuration of a dependency bot and comments next to a pin.
An image that follows its major line on purpose, or a package held back
until an upstream fix, is named in the report as excluded and not proposed
again.

Before it changes anything, the skill shows the list of what it found and
asks once about what is yours to decide: a major version, a migration such as
a new database major, a new runtime line, a wider version range. Patches,
rebuilt images and minor versions within the ranges it takes on its own.

Each kind of pin gets its own commit and the check it needs: release notes for
every minor or major, the project's checks and a smoke test before and after
for packages, a build and a real request for images. The report names what was
taken, what stayed excluded and what is still unchecked. Push, pull request
and merge wait for your word.

## Privacy

The skill queries public registries and release lists with the names and
versions of what the project uses, nothing else. It reads no secret files such
as `.env`, and it removes only the images and tags it created for its checks.
