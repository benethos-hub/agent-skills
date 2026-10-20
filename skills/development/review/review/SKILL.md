---
name: review
description: "Reviews a codebase or a range of changes for bugs, security, refactoring on code level and refactoring on folder, architecture and design level, in any language. Checks every finding in the code before listing it and writes one file of work packages, one package per branch in a sensible order, each finding with its place, evidence, change and test. The file is written for a less capable model or a fresh session to work through without asking back, so the user's decisions are settled first and written in. Changes nothing in the project. Use this skill whenever the user asks for a review, an audit, a security check, a bug hunt or a refactoring check, or for a list of changes or a to-do list that another model or session should work through. Answers in the user's language."
license: MIT
---

# Review

## What this skill is for

A review is worth what the next person can do with it. Here the next person is often another model: the strongest model reviews, a less capable or cheaper one builds. That model was not there. It does not know the code as well, it cannot ask the reviewer, and it follows what it reads. This skill writes a review it can follow: one file of work packages, each package a branch, each finding a change with its place, its evidence and its test.

Three attitudes carry everything else:

**First: checked, not suspected.** A finding enters the file only after it was read in the code, and reproduced where that is possible. A suspicion that could not be checked is marked as such, with what would confirm it. A list padded with guesses costs the next model more than it saves.

**Second: written for someone who was not there.** Every finding stands on its own. It names the file and the function, says what to change and how to prove it, and quotes the evidence instead of pointing to a scratch file that may be gone. Every decision the user has to make is made before the file is handed over, so the next model never has to judge what the user would want.

**Third: read only.** The review changes nothing in the project. No fix, no commit, no branch. The user asked for a list, and a fix made on the way is one nobody reviewed.

## Language of the answer

The file and the report follow the user's language. Code, paths, branch names and suggested commit messages stay in the language of the project, which is usually English. Quote the user's decisions in their own words.

## What the skill needs

- Read access to the repository and a shell to run the project's checks and small reproductions.
- Subagents help: one per category of the review, run in parallel. Without them the categories are worked one after another.
- A persistent memory for the file, ideally one the next session loads at its start. Without one, the file goes into the chat for the user to pass on.

## Procedure

Work through the steps in order. Ask the user only in step 6, all questions at once.

### Step 1: Settle scope and baseline

- **Scope.** What the user named: the whole repository, a branch, a pull request, or the changes since a tag. Without a word, review the whole repository and read the changes since the last release most closely.
- **The state.** Note the branch and the exact commit: `git rev-parse --short HEAD`, `git status`, the newest tag. The file names that commit, so the next model can tell how far the code has moved since.
- **The baseline.** Run the project's checks the way CI runs them: format, lint, types, tests, lock files. Find them in the CI configuration, a task runner or the instruction files. Note each result. A red check is a finding of its own, and the first one.

### Step 2: Read the rules and the history

- **The project's rules.** Instruction files such as `AGENTS.md`, `CLAUDE.md` and `CONTRIBUTING.md`, the architecture and design documents, the decision records, the changelog. What the project decided is the yardstick. A finding that undoes a recorded decision is not a finding. When there is a new reason to reopen it, it goes to the user as a question in step 6.
- **Earlier reviews.** Look in the agent's memory and the history for earlier review files and their done sections. Build two lists from them: **already fixed** (report only when it came back) and **decided, not to be flagged** (accepted behaviour, rejected proposals). Both go into every prompt of step 4.
- **The architecture rules.** When the project has its own, they apply. When it has none, [references/architecture.md](references/architecture.md) is the guide, and a finding drawn from it is a proposal, not a violation.

### Step 3: Run the tools

Use what the ecosystem offers, through the project's runner:

| Kind | What it finds |
|---|---|
| Dependency audit | known vulnerabilities in the locked packages |
| Dead code | functions, classes and settings nothing reaches |
| Complexity and size | long functions, large modules and classes, deep nesting |
| Secret scan | keys, tokens and passwords in the tree and the history |
| Type and lint checks at a stricter level | casts, ignores, broad exceptions |

Tool output is a lead, not a finding. Each hit is checked in the code like any other.

### Step 4: Fan out

Start one read-only subagent per category, in parallel. The prompts are in [references/prompts.md](references/prompts.md).

| Category | Looks for | Required |
|---|---|---|
| Security | ways in, leaks of secrets or private data, missing checks, unsafe defaults | yes |
| Bugs | wrong results, crashes, races, edge cases, error paths | yes |
| Refactoring, code level | duplicates, unclear names, long functions, wrong abstractions, lying comments | yes |
| Refactoring, structure level | folders, packages, layers, dependencies between them, where code belongs | yes |
| Documentation | documents that no longer match the code | when asked, or before a release |
| Tests | gaps, tests that pass for the wrong reason, flaky timing, duplicated fixtures | when asked |

Split a large codebase by area instead, one agent per area with all categories, when the categories would each have to read everything.

Every prompt names the commit, the hot zone, the rules to read first, the two lists of step 2, and the format of a finding. Every agent gets a scratch folder of its own and writes nowhere else. Agents that share a folder overwrite each other's scripts, and a script run with the wrong path can destroy a file outside the project.

### Step 5: Check what came back

Go through every finding yourself:

1. **Read it in the code.** The place exists, the code does what the finding says, and nothing elsewhere already prevents it.
2. **Reproduce it** when it is Medium or above: a small script or test, run outside the project tree, in a scratch folder. Note how.
3. **Mark the confidence:** *confirmed* (reproduced or read beyond doubt), *plausible* (read, not reproduced, with what would confirm it), or drop it.
4. **Merge duplicates** that two agents found from different sides.
5. **Hold it against the two lists** of step 2. A finding on the decided list is dropped.
6. **Set the severity:**
   - **High:** data loss, a security breach, a crash, a wrong result in normal use.
   - **Medium:** a wrong result in an edge case, a defence missing on a plausible path.
   - **Low:** hygiene, a misleading name or message, a small inconsistency.
   - **Note:** no action, kept for the record.

A refactoring finding also gets a size (S, M or L) and its risk: what could change in behaviour, in an interface, in stored data.

Drop what does not earn its place. A refactoring for its own sake, a split of a long file only for its length when the project sets no limit, a move whose churn outweighs the gain. Name the larger of these under "Deliberately not proposed", so the next review does not propose them again.

### Step 6: Settle the user's decisions

Collect everything the next model must not decide alone:

- A change of behaviour users would notice, or of a public interface, a stored format or an API.
- A choice between security variants. Recommend the most secure one first.
- A rename, a new setting, a new dependency, a change to CI.
- Writes to a live system or a real account for a check.
- Whether to build a finding that is only plausible.
- How deep a refactoring goes.
- How the branches are cut, when that is not obvious.

Ask all of them in one round, each with the facts, the options and a recommendation. Write each answer into the file with the date and the user's words. When the user is not there to answer, the questions go into a package of their own, "The user's call", which the next model does not build.

### Step 7: Cut the work packages

A package is one branch and one pull request. Order them so each one is green and mergeable on its own:

1. **Security.**
2. **Bugs.** Small fixes without a live check first, then those that need one.
3. **Documentation** that the fixes changed, after them, so it describes the new state.
4. **Refactoring on code level.**
5. **Refactoring on structure level** last, largest moves at the end. These change no behaviour, and the package says what must stay byte for byte the same.

Split a category into more packages when it is large or touches unrelated areas. Merge small ones when they share their files. Number the findings once across all packages, so the user can answer "12" or "package 3, finding 14".

### Step 8: Write the file

The form is in [references/list-format.md](references/list-format.md): a header, the rules for working through, the decisions, the packages, then "The user's call", "Deliberately not proposed", "Checked and clean" and "Done".

- The file stands on its own. Copy evidence in, do not link to scratch files.
- No release step. Releasing is the user's, never part of the list.
- No time spans that were not looked up. "For weeks" or "since the last release" only after `git log`.
- No reasons the user did not give. A reason is the user's, the code's or yours, and the file says which.

**Where it goes.** Into the agent's persistent memory as one file, named after the project and the date, such as `review-2026-10-20.md`, with a line in the memory's index. The next session finds it there. Without a memory, give the whole file in the chat. Never write it into the project unless the user asks for that.

### Step 9: Report and stop

Report in a few lines: the commit reviewed, the baseline, the findings by severity, the packages in order, the decisions taken, and where the file is. Tell the user how to hand it over, for example: open a new session with the other model and say "work through the review list review-2026-10-20". Then stop.

## What this skill does not do

- It fixes nothing, commits nothing and opens no branch.
- It does not release and puts no release into the list.
- It does not reopen the project's recorded decisions on its own.
- It does not list what it could not check as if it had.
- It does not write the file into the project unless asked.

---

# Appendix: traps

The cases below are the ones that went wrong in practice. Check each before handing over.

## 1. A finding from a summary

A subagent reports what it believes it read. Its file and line can be off, its scenario can miss a guard two calls up. Every finding is read in the code by the reviewer before it goes into the file.

## 2. A recorded decision reported as a bug

An accepted behaviour looks like a defect to someone who did not read the decision. The decided list goes into every prompt, and the reviewer checks against it again.

## 3. A fixed finding reported again

Without the list of what earlier reviews fixed, the same finding comes back each round. The next model then searches for a bug that is gone.

## 4. Evidence in a scratch file

A scratch folder may be cleaned before the next session starts. Quote the code and describe the reproduction in the file itself.

## 5. A question left for the next model

"Clarify with the user" in a finding makes the next model stop or guess. Settle it now, or put the finding into "The user's call".

## 6. Parallel agents in one folder

Two agents that write scripts of the same name into one folder run each other's code. Give each agent its own folder, and tell it that transcripts and configuration of the agent are never an output path.

## 7. Quick check before reporting

- Every finding was read in the code, every Medium and above reproduced or marked plausible.
- Every finding names its place, its change and its test.
- No finding asks the next model to decide something that is the user's.
- The packages are in an order where each can merge on its own.
- No release step, no invented reason, no file changed in the project.
