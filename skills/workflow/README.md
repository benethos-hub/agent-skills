# Workflow skills

Skills for long working sessions with an agent. They keep decisions,
permissions and the state of the work safe across a context compaction and
into the next session. They change no file of the project.

**Contents**

- [Skills](#skills)
- [Quick start](#quick-start)
- [Setup in detail](#setup-in-detail)
  - [1. Install the skills](#1-install-the-skills)
  - [2. Give the agent a memory](#2-give-the-agent-a-memory)
  - [3. Check the setup](#3-check-the-setup)
- [Using prepare-for-compaction](#using-prepare-for-compaction)
- [Privacy](#privacy)
- [Disclaimer](#disclaimer)

## Skills

| Skill | What for | Needs |
|---|---|---|
| [prepare-for-compaction](prepare-for-compaction/SKILL.md) | Moves what only the conversation holds into the agent's memory before a compaction, with every state measured first, the replaced state tidied up and nothing in the project touched | a persistent memory, read access to git |

## Quick start

The shortest way for each client, simplest first:

| Client | Steps |
|---|---|
| Claude Code | Add the marketplace and install the bundle `workflow`. Claude Code brings its own memory. |
| Other agents | Unpack the ZIP into the agent's skills directory. The agent needs a memory it can write. |
| claude.ai and Claude Desktop | Upload the ZIP under Settings, Skills. Without a memory the skill writes the handover as a message to keep. |

For Claude Code these are the two commands:

```bash
claude plugin marketplace add benethos-hub/agent-skills
claude plugin install workflow@benethos-agent-skills
```

## Setup in detail

### 1. Install the skills

**Claude Code.** The bundle installs every skill of this category. The
marketplace has to be added once before:

```bash
claude plugin marketplace add benethos-hub/agent-skills
claude plugin install workflow@benethos-agent-skills
```

Install either the bundle or single skills, not both. A skill that comes
from both is loaded twice.

**Single skills.** Each skill also comes on its own, as a ZIP from the newest
release and as a plugin of its own:

| Skill | Download | Claude Code |
|---|---|---|
| prepare-for-compaction | [prepare-for-compaction.zip](https://github.com/benethos-hub/agent-skills/releases/latest/download/prepare-for-compaction.zip) | `claude plugin install prepare-for-compaction@benethos-agent-skills` |

The links always reach the newest release. Every release on the
[releases page](https://github.com/benethos-hub/agent-skills/releases) also
carries each ZIP under a name with its version, `<skill-name>-X.Y.Z.zip`, for
a fixed version.

In claude.ai and Claude Desktop, upload the ZIP in the settings under Skills.
Other agents and updates are covered under
[Installing](../../README.md#installing) in the main README.

### 2. Give the agent a memory

The skill writes into the agent's persistent memory: files that survive into
the next session. Claude Code has one per project and loads its index at the
start of every session. Other agents differ, so check the agent's
documentation.

Without such a memory the skill still works. It then writes the handover as
a message, and you paste it into the next session.

### 3. Check the setup

In a session with some work behind it, say:

> Prepare for compaction.

The agent should run read-only commands such as `git status` first, then
write or update its memory, then tidy what the new state replaces, then
report which memories changed and the state of the work. `git status` in the
project shows no change afterwards.

## Using prepare-for-compaction

Ask for it before you compact or end a long session. Short forms work too,
such as "prepare compact". The skill asks nothing on the way. What stays
unclear is written down as an open point.

The skill tidies only what this session's new state replaces: an older state,
duplicates, a memory proven wrong. It never deletes a rule you gave, and the
report names every deletion. Tidying the whole memory is a task of its own.
Ask for it separately, and the agent shows you a list of what would go first.

Afterwards start the compaction yourself. The skill does not start it.

## Privacy

The memory stays where the agent keeps it, usually on your machine. The skill
writes no secret into it, only where a secret lives. Everything else the
memory holds comes from your conversation, so treat it like the conversation.

## Disclaimer

The skill writes down what the conversation and the repository show. A
memory can still be wrong or out of date. Check it before relying on it for a
step that is hard to undo.
