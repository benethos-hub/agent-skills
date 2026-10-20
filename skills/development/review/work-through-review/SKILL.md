---
name: work-through-review
description: "Works through a review file of work packages, as the skill review writes it, one branch per package and one commit per finding, in any language. Checks every finding against the current code first, asks all open questions at the start and then works without stopping, skips a finding that turns out wrong and says why, runs the project's checks before each commit and marks each finding done in the file. Builds nothing beyond the list. Pushing, pull requests and merging wait for the user's word unless the user granted them for this list, and a release is never part of it. Use this skill whenever the user hands over a review list, a to-do list of findings or work packages from another session or model, or asks to work through, apply or implement review findings. Answers in the user's language."
license: MIT
---

# Work through a review

## What this skill is for

Another model or session reviewed the project and wrote a file of work packages. This skill builds them: package by package, finding by finding, each one checked, tested and committed on its own. The review did the judging. The work here is to build exactly what the file says, well, and to notice when the file is wrong.

Three attitudes carry everything else:

**First: the file is the order, the code is the truth.** The file says what to build. The code may have moved since it was written, and the reviewer may have been wrong. Every finding is checked against the current code before anything is built. A finding that does not hold is skipped with its reason, not bent until it fits.

**Second: questions first, then through.** Everything that needs the user is asked at the start, in one round. After that the work runs to the end without check-ins. What comes up on the way is parked and reported at the end.

**Third: nothing beyond the list.** A new finding, a nicer design, a cleanup next door: all of it goes into the report, none of it into the code. The user approved the list, not more.

## Language of the answer

Questions and the report follow the user's language. Code, branch names, commit messages and changelog entries follow the language of the project, which is usually English.

## What the skill needs

- The review file: in the agent's memory, pasted into the chat, or as a file the user names.
- Write access to the repository, git, and the tools of the project's checks.
- The command line of the hosting service, such as `gh`, for pushing and pull requests once the user allows them.

## Procedure

### Step 1: Read the file and the rules

- **Find the file.** Look in the memory's index for the newest review file of this project, or take the one the user named or pasted. When there are several and the user named none, ask which one.
- **Read it whole**, from the header to the done section: the reviewed commit, the rules for working through, the decisions, every package, "The user's call", "Deliberately not proposed".
- **Read the project's rules**: instruction files such as `AGENTS.md` or `CLAUDE.md`, the architecture document, the changelog conventions. Where the file and the project's rules disagree, the project's rules win, and the report says so.

### Step 2: Measure the state

- `git status`, `git branch --show-current`, `git log --oneline <reviewed commit>..main`.
- Which packages are done already: the done section of the file, the branches, the pull requests and their state, for example `gh pr list --state all`.
- Another session may work in the same repository. Commits and branches that are not from this session are named, not taken over.
- Run the project's checks on the current main. A red main is the first thing to report, before building on it.

### Step 3: Check every finding against the code

Before asking anything, go through every open finding:

1. Is the place still there? Lines move, so search by the function or class the finding names.
2. Does the code still do what the finding says? Read it, and run the reproduction when the file gives one.
3. Mark each one: **holds**, **already fixed** (by which commit), **wrong** (why), or **changed** (the problem is there, the described change no longer fits).

This turns the questions of step 4 into informed ones.

### Step 4: Ask everything at once

Ask in one round, each question with the facts, the options and a recommendation:

- Findings marked wrong or changed in step 3: skip, or build in a changed form.
- Decisions the file left open, and findings marked plausible when the file does not say whether to build them.
- How to cut the branches, when the file leaves it open: one after another from main, waiting for each merge, or stacked on each other so the work runs through.
- Whether pushing, opening pull requests and merging are allowed for this list. A permission given here covers this list and ends with it.
- Writes to a live system or a real account, when a package needs a live check.

Do not ask what the file decided. Do not ask about "The user's call": those findings are not built unless the user moves them into a package now. When nothing is open, say so in one line and start.

### Step 5: Build package by package

For each package, in the order of the file:

1. **The branch.** Create the branch the package names, from the current main, or from the previous package when the user chose stacking.
2. **Each finding, in the order of the package:**
   - Read the place again. Build the change the finding describes, as small as it can be.
   - Write the test the finding names. Check that it fails without the change: set the source back, leave the test, run it, restore the source.
   - For a refactoring, capture the output the finding says must not change before the move, then compare after. The comparison must be empty.
   - Run the project's checks, all of them, the way CI runs them. Fix until green. A check is never switched off or skipped.
   - Commit, one finding per commit, one defect per commit when a finding names several. Start the subject with what changes, and name the finding number in the body.
   - Add the changelog entry in the same commit when the package says so.
   - Mark the finding done in the file: number, commit, a note when it was built otherwise.
3. **The end of the package.** Run the checks once more on the whole branch. When the user allowed it, push and open the pull request, with the findings and their numbers in the description. Merge only with the permission for this list, after the required checks are green. Then go on to the next package.

### Step 6: When a finding does not fit

- **Already fixed:** skip it, name the commit that fixed it.
- **Wrong:** skip it, write why into the file and the report. Do not build something else in its place.
- **The described change does not work:** take the smallest change that solves the problem the finding names, mark it "built otherwise" with the reason, and name it in the pull request.
- **It needs a decision that is the user's:** park it, go on with the next finding, and ask at the end.
- **It reveals a new problem:** note it for the report. It is not built.

Small choices of your own, such as a name or the place of a test, are made and listed in the report as yours.

### Step 7: Report and stop

Report per package: the branch, each commit with its finding number, the checks and their result, the pull request if one was opened. Then:

- Skipped findings, each with its reason.
- Findings built otherwise, each with its reason.
- Your own choices.
- New findings, not built.
- Parked questions.
- What waits for the user: a push, a merge, a decision.

Update the done section of the file. Then stop. A release is not part of this skill, even when every package is merged.

## What this skill does not do

- It builds nothing the file does not name, and no finding from "The user's call" without the user's word.
- It does not change the decisions in the file.
- It does not switch off a check to get a commit through.
- It does not push, open pull requests or merge without the user's word, and a permission for one list does not carry over to the next.
- It does not release.

---

# Appendix: traps

The cases below are the ones that went wrong in practice. Check each before reporting.

## 1. A finding taken on trust

The reviewer read the code at another commit, or misread it. A finding built without checking can bring a bug where there was none. In practice a reviewer called a guard dead code that was not. Step 3 comes before every build.

## 2. Several findings in one commit

One commit for a whole package cannot be reverted in part and hides which change broke what. One finding, one commit.

## 3. Documentation before the fixes

Documentation written before the fixes describes the old state. Follow the order of the file, which puts it after them.

## 4. A refactoring that changes behaviour

A move that "only" moves code can change an order, a default or an output. Capture before, compare after, and stop when they differ.

## 5. A push to a merged branch

When the user merges quickly, a push to the branch after the merge brings the deleted branch back. Check that the pull request is still open before every push.

## 6. A permission that grew

"You may merge for this list" covers this list. The next list, a release or a change of repository settings each need their own word.

## 7. Quick check before reporting

- Every finding was checked against the current code before it was built.
- Every commit holds one finding and passed every check on its own.
- Every skipped or changed finding has its reason in the file and the report.
- Nothing was built beyond the list.
- Nothing was pushed, merged or released without the user's word.
