# The review file

One file holds the whole review. The model that works it through reads it from the top and needs nothing else. Keep the order of the sections below.

## Template

```markdown
# Review of <project>, <date>

Written for: the session that works through this file. It holds everything
needed to build the packages in order.

- **Reviewed:** branch `<branch>` at `<commit>` (<version or tag>).
- **Scope:** <whole repository | changes since <tag> | pull request <n>>,
  read most closely: <hot zone>.
- **Baseline:** <each check and its result, such as "lint, types, 212 tests:
  green">.
- **Findings:** <n> High, <n> Medium, <n> Low. <n> packages.
- **Reviewed by:** <model>, with <n> subagents, every finding checked in the
  code by the reviewer.

## Rules for working through

- One branch per package, in the order below.
- One commit per finding. A finding that names several defects gets one
  commit per defect.
- Before building a finding, check it against the current code. When it is
  wrong or already fixed, skip it and say why in the report.
- Every commit passes the project's checks. A new test fails without the fix.
- A changelog entry only for what a user of the project would notice.
- Nothing beyond the list. A new finding goes into the report, not into
  the code.
- Push, pull request and merge wait for the user's word. No release.

## Decisions

- **D1** (<date>, the user: "<their words>"): <what is decided, which
  findings it settles>.

## Package 1: Security

- **Branch:** `fix/<short-name>`
- **Goal:** <one sentence>
- **Checks:** <the project's checks, plus a live check if one is needed>
- **Changelog:** <yes, under Fixed | no>
- **Depends on:** <nothing | package n>

### 1. Security, Medium, confirmed

- **Where:** `<path>:<line>`, `<function or class>`
- **Problem:** <what is wrong, in one or two sentences>
- **Scenario:** <the concrete input or sequence and what goes wrong>
- **Evidence:** <the quoted code, or how it was reproduced and what came out>
- **Change:** <what to change, precise enough to build without judging>
- **Test:** <the test that proves it, and that it fails without the change>
- **Must not change:** <behaviour or output that stays the same, if any>

## Package 5: Structure

<same frame, and the findings add:>

- **Size:** S | M | L
- **Risk:** <what could change in behaviour, interface or stored data>
- **Move:** <from where to where, which imports follow>
- **Compare:** <the output captured before and after that must be equal,
  such as the public interface, the command line help or the API schema>

## The user's call

Findings the next model does not build until the user decided them. Each
with the options and a recommendation.

## Deliberately not proposed

<what was considered and left out, each with its reason, so the next review
does not propose it again>

## Checked and clean

<the areas checked without a finding, one line each, so the next review
knows the coverage>

## Done

| Finding | Commit | Pull request | Note |
|---|---|---|---|
```

## Rules for the content

- **Numbers run once across all packages.** Finding 14 is finding 14 in every message about this review.
- **Severity, category and confidence in the heading** of each finding, so the order of the file can be checked at a glance.
- **Precise places.** A path from the repository root, a line, and the name of the function or class, since lines move when earlier findings are fixed.
- **One change per finding.** Two independent changes are two findings.
- **Change, not direction.** "Check the order of start and end and reject the request when start is later" is buildable. "Improve the validation" is not.
- **A test for every bug and security finding.** For a refactoring, the comparison that shows nothing changed.
- **Plausible findings say what would confirm them**, such as "write the test with two users first" or "check against the live service".
- **The user's words in quotes**, with the date. Your own choices are marked as yours.

## Example findings

From real reviews, with the project's names replaced.

> ### 1. Security, Medium, confirmed
>
> - **Where:** `settings/loader.py:88`, `key_saved_since_startup`
> - **Problem:** The function reads the settings file again on every call. When the file is not valid UTF-8, the raised error carries the absolute path of the file, and that error reaches the client.
> - **Scenario:** Start without a key, save a settings file in another encoding, call any tool. The answer names the user's home directory.
> - **Evidence:** Reproduced with a Latin-1 file: the answer contained the full path.
> - **Change:** Catch the error in `key_saved_since_startup`, raise a sentence without the path, log the path locally.
> - **Test:** A settings file in Latin-1, the answer holds no path. Fails without the change.

> ### 7. Bug, Low, confirmed
>
> - **Where:** `mailbox/threads.py:212`, `list_threads`
> - **Problem:** Paging compares only the received time with a strict greater-than.
> - **Scenario:** Two messages of one thread arrive in the same second and fall on neighbouring pages. The thread is listed twice.
> - **Evidence:** Read in the code, reproduced with two messages of equal time and a page size of one.
> - **Change:** Compare the pair of received time and id.
> - **Test:** Two messages of equal time, page size one, each thread once.

> ### 21. Structure, Medium, confirmed
>
> - **Where:** `providers/cloud/provider.py`, class `CloudProvider` (444 lines, 29 methods)
> - **Problem:** One class holds folders, drafts, sending and sync. The other providers split these into modules.
> - **Size:** M
> - **Risk:** none in behaviour, the class keeps its public methods.
> - **Move:** `folders.py`, `drafts.py`, `changes.py` beside `provider.py`, as the other providers have them. `provider.py` delegates.
> - **Compare:** the provider's public methods and the full test run, before and after.
