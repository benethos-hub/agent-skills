---
name: prepare-for-compaction
description: "Prepares a working session for a context compaction or a new session. Moves what only the conversation holds into the agent's persistent memory: the user's decisions in their own words, corrections, permissions and how far they reach, traps of the environment and the exact state of the work. Measures every fact before writing it down, refreshes the memories the session touched, tidies what the new state replaces and leaves the project's files alone. Use this skill whenever the user asks to prepare for a compact, a compaction, a context reset or a handover to the next session, also in short forms such as 'prepare compact' or 'auf compact vorbereiten'. Answers in the user's language."
license: MIT
---

# Prepare for compaction

## What this skill is for

A compaction replaces the conversation with a summary. What lives only in the conversation is then gone or blurred: a decision the user made in passing, a correction, a permission for one pull request, a trap in the shell. The next session starts from the summary and the persistent memory, and from nothing else.

This skill turns the handover into a piece of work, not an acknowledgement. Three attitudes carry everything else:

**First: memory only.** Preparing changes the agent's memory and nothing in the project. No file in the working tree, no commit, no push. Another session may work in the same checkout, and a write would land on its branch. Checking the project's documents against the code is a task of its own, done when the user asks for it.

**Second: measured, not remembered.** Every state written down is looked up right before: branch, commit, pull requests, releases. A wrong memory looks exactly like a right one, and the next session acts on it.

**Third: the user's decisions stay the user's.** Something is recorded as a decision only when the user made it, with their words and the date. The agent's own choices are marked as its own.

## Language of the answer

The report at the end follows the user's language. The memory files keep the language they are already written in. Quote the user's words in their original language, so the next session can tell a quote from a paraphrase.

## What the skill needs

- A persistent memory the agent can write: files that survive into the next session, ideally one fact per file and an index that is loaded at the start. Without one, write the handover as a message the user can keep and paste into the next session, and say so.
- Read access to the project's version control. For work with a hosting service such as GitHub, its command line helps to see pull requests and releases.

## Procedure

Work through the steps in order and ask nothing on the way. What stays unclear goes into memory as an open point.

### Step 1: Read what memory holds

Read the index and every memory the session touched or relied on: the project state, the rules for how to work, the decision notes. Mark each one as still true, stale or wrong. Note duplicates and finished lists as candidates for step 5, but change nothing yet.

### Step 2: Measure the current state

Run read-only commands only, for example:

- `git status`, `git branch --list`, `git log --oneline -5`, `git stash list`
- the pull requests of the last days with their state: `gh pr list --state all --limit 10`
- the newest tag and release: `gh release list --limit 3`
- jobs, servers or containers this session started and that still run

Write down the exact values: commit hashes, pull request numbers, versions.

### Step 3: Collect what only the conversation holds

Go through the conversation from the start and list:

- **Decisions of the user**, with their words, the absolute date and what they settle.
- **Corrections and rules for working**, each with the reason and the incident behind it. A rule without its reason gets applied wrongly at the edges.
- **Permissions and their reach.** A permission to merge or to release covers the one item it was given for. Note which ones are used up.
- **What waits for the user:** a push, a merge, a release, an answer. Name the exact question that is open.
- **Work in progress:** branch, uncommitted changes, what is done, what comes next, where to pick up.
- **Environment facts and traps:** a shell quirk, a tool path, a command that hangs, and what works instead.
- **Outside state:** a test account and its deadline, a service still running, a file left in a temporary folder.

Leave out what the project already records: its history, changelog, documentation and instruction files such as `AGENTS.md` or `CLAUDE.md`. Leave out every secret. A memory says where a token lives, never its value.

### Step 4: Write and refresh

- **Update before adding.** Look for a memory that already covers the point and change it. One fact per memory.
- **The project state on top.** The state memory gets the new state first, with the absolute date, the commit and the pull request numbers. Shorten or remove what the new state replaces. A state memory that only grows turns into a diary nobody reads to the end.
- **Absolute dates.** "Yesterday" becomes a date. A time span such as "for weeks" or "for a whole release" is written only after looking it up in the history.
- **Rules with why and how.** Each rule says why it exists and how to apply it.
- **The index.** Every touched memory gets its index line refreshed, so the line names the new state.
- **Nothing about compaction in the project.** The project's files record the project, not how the agent manages its context.

### Step 5: Tidy up what the new state replaces

Only now, with the new state written, remove what it replaces. Tidying first would leave nothing behind if the session broke off in between. Tidying after leaves at worst a duplicate.

The step stays within the candidates of step 1 and the memories step 4 touched:

- **Shorten the replaced state.** An older state in the state memory that the new one fully covers is cut down to what still matters or removed.
- **Merge duplicates.** Two memories on the same point become one. The index keeps one line for it.
- **Delete with proof only.** A memory goes when it is proven wrong, or when everything in it is recorded elsewhere: a finished list with no open point that the history and the changelog cover, a release note the release itself holds.
- **Never delete a rule of the user.** A correction or a rule for how to work may be merged with another, never dropped.
- **When in doubt, keep it.** A memory that may still matter stays. Mark it as old instead.

Every deletion and every merge goes into the report.

### Step 6: Check what was written

Read the changed memories again. Hashes, numbers and names match step 2. Links between memories resolve, also those that pointed to a deleted or merged memory. The index has one line per memory and no line for a deleted one. No secret slipped in.

### Step 7: Report

Keep it short:

1. Which memories are new and which changed, by name.
2. Which memories were deleted or merged, each with the reason.
3. The state in two or three lines: branch, commit, what is open, what waits for the user's word.
4. That the session can be compacted now.

When the memory as a whole has grown hard to read, say so in one line and offer to tidy it as a task of its own.

No further question at the end. The user starts the compaction.

## After the compaction

The next session reads the state memory first and checks it against the repository before its first action. A permission from before counts only as far as the memory says it reaches. When the memory says to wait for the user, the session waits.

## What this skill does not do

- It does not compact. The user starts that.
- It changes no file of the project and makes no commit, push, merge or release.
- It does not check the project's documents against the code.
- It does not tidy the whole memory. Going through every old memory is a task of its own, done only when the user asks for it, with a list of what would go for the user to approve first.
- It stores no secret.
- It invents no reasons. A side effect of the implementation is not written down as a decision.

---

# Appendix: traps

The cases below are the ones that went wrong in practice. Check each before writing.

## 1. A status report is no permission

"It is merged" reports what the user did. It is not a yes to the next step, even when the question before it offered that step. The memory records the permission only when the user gave it for that exact action.

## 2. A permission for one item

A permission to merge pull request 12 says nothing about pull request 13. Write the item it was given for and that it is used up afterwards.

## 3. A parallel session

Another session may work in the same repository. Its branch, its pull request or its merge can look like this session's work. Check the state of every pull request named in memory before calling it open or merged.

## 4. Invented time spans

"Since weeks" or "nobody has missed it" reads like an observation. In a young repository it can be impossible. Look it up in the history or leave it out.

## 5. Side effects dressed up as decisions

What the implementation happened to do is not a decision. Write it as an open point or as the agent's own choice, never as something the user decided.

## 6. A memory of outside behaviour

A memory of how an outside service or library behaves is a hint, not evidence. Note when it was measured, so the next session knows how old it is.

## 7. Quick check before reporting

- Every state comes from a command run in step 2, not from the conversation.
- Every decision carries the user's words and a date.
- Every permission names its item and whether it is used up.
- Nothing was deleted that is not recorded elsewhere or proven wrong, and the report names every deletion.
- No file of the project changed. `git status` shows the same as before step 1.
