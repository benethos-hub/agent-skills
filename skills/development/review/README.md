# <img src="https://raw.githubusercontent.com/benethos-hub/agent-skills/main/assets/brand/icon.svg" alt="" width="40" height="40"> Review skills

[![CI](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/benethos-hub/agent-skills/badges/coverage.json&logo=githubactions&logoColor=white)](https://github.com/benethos-hub/agent-skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/benethos-hub/agent-skills?logo=opensourceinitiative&logoColor=white)](https://github.com/benethos-hub/agent-skills/blob/main/LICENSE)

[![Release](https://img.shields.io/github/v/release/benethos-hub/agent-skills?label=Release&logo=github&logoColor=white)](https://github.com/benethos-hub/agent-skills/releases/latest)

[![Sponsor](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/sponsor.svg)](https://github.com/sponsors/BeneODev)
[![PayPal](https://raw.githubusercontent.com/benethos-hub/.github/main/profile/badges/paypal.svg)](https://paypal.me/BeneODev)

Skills for reviewing a project in any language and working the review
through: the strongest model checks for bugs, security and refactoring and
writes the work packages, another model builds them branch by branch.

**Contents**

- [Skills](#skills)
- [Installing](#installing)
- [The workflow](#the-workflow)
- [Using review](#using-review)
- [Using work-through-review](#using-work-through-review)
- [Privacy](#privacy)

## Skills

| Skill | What for | Needs |
|---|---|---|
| [review](review/SKILL.md) | A checked review for bugs, security and refactoring on code and structure level, written as one file of work packages that another model can build | git, the project's tools, subagents help |
| [work-through-review](work-through-review/SKILL.md) | Builds a review file package by package, one branch per package and one commit per finding, each finding checked against the code first | git, the project's tools |

## Installing

In Claude Code the bundle `development-review` brings every skill of this
subcategory:

```bash
claude plugin install development-review@benethos-agent-skills
```

Each skill also comes on its own:

| Skill | Download | Claude Code |
|---|---|---|
| review | [review.zip](https://github.com/benethos-hub/agent-skills/releases/latest/download/review.zip) | `claude plugin install review@benethos-agent-skills` |
| work-through-review | [work-through-review.zip](https://github.com/benethos-hub/agent-skills/releases/latest/download/work-through-review.zip) | `claude plugin install work-through-review@benethos-agent-skills` |

The steps are the same for every skill. The
[development README](../README.md#installing) says what the skills need, and
the [main README](../../../README.md#installing) covers each client.

## The workflow

A review takes judgement, building it takes care and time. The two skills
split that work between two models and two sessions:

1. **Review with the strongest model.** Open a session with the most capable
   model you have and ask for a review, for example "review the project for
   bugs, security and refactoring". It reads the project's rules, lets
   subagents search each category in parallel, checks every finding in the
   code itself and drops what it cannot confirm.
2. **Decide.** Before it writes the file, the review asks you everything
   that is yours to decide in one round: a change of behaviour, a security
   variant, a rename, how deep a refactoring goes. Each question comes with
   a recommendation. Your answers go into the file.
3. **The file.** One file holds the whole review: the commit it looked at,
   the rules for working through, your decisions, then the work packages in
   order. Each package is one branch: security first, then bugs, then the
   documentation the fixes changed, refactoring last. Each finding names its
   place, the evidence, the change and the test. The file goes into the
   agent's memory, or into the chat when there is none. Nothing in the
   project changes.
4. **Work through with another model.** Open a new session with a less
   capable or cheaper model and say "work through the review list". It checks
   every finding against the current code, asks what is still open at the
   start, then builds one branch per package and one commit per finding,
   each green on its own. A finding that turns out wrong is skipped with its
   reason.
5. **Merge.** Pushing, pull requests and merging wait for your word. You can
   allow them for one list at the start of step 4. A release is never part
   of it.

The file is written so the second model never has to guess what you want.
That is what lets a less capable model build it: the judging is done.

Both skills also work alone. The review is useful without a second model,
and the second skill builds any list of findings that names the places and
the changes.

## Using review

Ask for a review in your own words, such as "review this project", "security
and bug review since the last release" or "make a to-do list for another
model". Name the scope when you want less than the whole repository: a
branch, a pull request or the changes since a tag.

The skill measures the code against the project's own rules first: its
instruction files, such as `AGENTS.md` or `CLAUDE.md`, and its architecture
and design documents. Write down what the project decided, and the review
will not report it as a defect. When the project has no architecture rules,
the skill uses general rules on layers, packages and where code belongs, and
marks findings from them as proposals.

Earlier review files in the agent's memory tell the next review what was
already fixed and what was decided against, so it does not report them
again.

## Using work-through-review

Hand over the file in a new session: "work through the review list", or paste
it. The skill reads it whole, measures the state of the repository and checks
each finding against the code before it asks anything. Then it asks once,
works through without check-ins and reports per package at the end: the
commits, what it skipped and why, what it built otherwise, and new findings
it did not build.

It builds nothing beyond the list. A finding under "The user's call" waits
until you move it into a package.

## Privacy

The review reads the project, never its secret files such as `.env`, and
writes no live system. Reproductions run in a scratch folder outside the
project. The file quotes code, so it stays where the agent's memory is, and
does not go into the project unless you ask.
