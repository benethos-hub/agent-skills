# Prompts for the subagents

Each subagent gets the common part and the part of its category. Fill in the angle brackets. Keep the prompts in English, whatever language the user writes, since code and paths are English too.

## Common part

```text
Read-only review. Do not change, create or delete any file in the
repository, and do not commit. Do not open secret files such as .env.
Do not write to live systems or real accounts.

Your scratch folder is <folder>. Write scripts and notes only there,
under names that start with <prefix>. Transcripts, configuration and
memory of the agent are never an input you change and never an output
path.

Repository: <path>, branch <branch> at <commit>.
Scope: <scope>. Look hardest at what changed since <tag or commit>:
<git diff --stat or the list of files>.

Read first, to know what is intended: <instruction files, architecture
and design documents, the sections of the specification that apply>.
A mismatch between these documents and the code is a finding too.

Already fixed in earlier reviews. Do not report them unless they came
back:
<list>

Decided and NOT to be flagged:
<list>

Report only findings you verified by reading the code, and reproduce a
finding of Medium or above with a small script in your scratch folder
where that is possible. Check library behaviour in the installed source,
do not guess. For each finding give:

- severity: High, Medium, Low or Note
- confidence: confirmed (reproduced or beyond doubt) or plausible (and
  what would confirm it)
- place: path from the repository root, line, function or class
- the problem in one or two sentences
- a concrete scenario: input or sequence, and what goes wrong
- evidence: the quoted code, or the reproduction and its output
- the change, in one or two sentences, precise enough to build
- the test that proves it

Then list in one line each what you checked and found clean, so the
caller knows the coverage. Keep speculation out and do not pad the list.
No preamble.
```

## Security

```text
Category: security. Check at least:
- every way in: requests, command line arguments, files read, messages
  from other systems. Is each input checked before use?
- authentication and authorisation: is every path checked, in one place,
  and does a check in one front end also hold for the others?
- secrets: how they are read, kept, logged, passed on. Can one reach a
  log line, an error message, a client or the repository?
- private data in errors and answers: paths, addresses, internal ids.
- injection into queries, shells, templates, headers, file paths.
- network: outgoing requests to addresses a caller controls, redirects,
  TLS checks, proxies from the environment.
- defaults: what happens when a setting is missing. Safe or open?
- dependencies and build: known vulnerabilities, unpinned versions,
  actions or images without a fixed reference.
Rate by what an attacker could actually reach, not by what is possible
in theory.
```

## Bugs

```text
Category: bugs. Check at least:
- edge cases: empty, one, many, the limit, the limit plus one, equal
  values, time zones, leap days, encodings.
- error paths: what happens when a call fails half way. Is state left
  behind, is the error swallowed, does the caller learn of it?
- concurrency: shared state, order of operations, retries, timeouts,
  resources that are opened and not closed.
- paging, sorting and limits: duplicates, gaps, results cut off without
  saying so.
- contracts: does the code do what its documentation, its types and its
  interface promise?
- long running behaviour: collections that only grow, caches without a
  limit, leaks.
For each finding give the shortest sequence that triggers it.
```

## Refactoring, code level

```text
Category: refactoring on code level. Check at least:
- the same logic in more than one place, and helpers that exist twice.
- names that say something else than the code does, and comments that
  no longer match.
- long functions, long parameter lists, flag arguments that switch
  between two behaviours.
- broad exception handling that hides errors.
- casts, ignores and suppressions that cover a real type problem.
- constants repeated as literals, and messages that state a value the
  code holds elsewhere.
- dead code the tools or a name search find.
Give each finding a size (S, M or L) and its risk: what could change in
behaviour, an interface or stored data. Say what must stay byte for byte
the same. Do not propose rewrites for their own sake. Name the proposals
you would NOT make because the churn outweighs the gain, with the reason.
```

## Refactoring, structure level

```text
Category: refactoring on folder, architecture and design level. Read the
project's own architecture rules first. When it has none, use these:
<the contents of references/architecture.md, or the sections that apply>

Check at least:
- the tree on disk against the documented layout.
- the direction of dependencies between layers and packages, and cycles.
- code in the wrong place: a decision in the data layer, transport
  details in the business logic, a check that exists per front end.
- third-party libraries imported in more than one place, and their
  types or errors leaking past a wrapper.
- packages cut by pattern instead of by subject, uneven packages, a
  shared helper package that became a drawer.
- what a swap of one technology would touch. More than one module means
  the seam is in the wrong place.
- tests: their layout against the code, duplicated fixtures, tests that
  reach into another test.
For each finding say where the code is, where it belongs and which
imports follow. Give size and risk as for code level. Say which rules a
test could check from now on. Name the moves you would NOT make, with
the reason.
```

## Documentation

```text
Category: documentation. Check every Markdown file and the user-facing
help against the code: commands, settings and their defaults, figures,
tables, examples, diagrams, links. A sentence that was true before the
recent changes and is not any more is a finding. Measured figures with a
date are records, not mistakes. Report the exact sentence and the
correct statement.
```

## Tests

```text
Category: tests. Check at least:
- branches and error paths no test reaches, in the hot zone first.
- tests that pass for the wrong reason: a mock that returns what is
  asserted, a check that skips itself when a key is missing.
- timing: sleeps and waits that make a test flaky.
- duplicated fixtures and helpers, tests that import from other tests.
- tests that reach into private parts where the public interface would
  do.
For each gap name the test to add and what it would catch.
```
