---
name: commit
description: "Commits changes in a git repository in small, checked steps on the right branch, for any language or toolchain. Finds the project's own checks (format, lint, types, tests, lock files) and runs them before every commit, decides whether a change belongs on the current branch or on a new one, keeps secrets and ignored files out, and writes the message from the actual diff. Pushing, pull requests and merging wait for the user's word. Use this skill whenever the user asks to commit, to save the work in git, to split work into commits or to put a change on a branch, and whenever the project's rules say to commit after each step. Answers in the user's language."
license: MIT
---

# Commit

## What this skill is for

A commit is a record someone reads later. It should hold one change, pass the project's checks on its own and sit on the branch whose subject it belongs to. This skill makes every commit like that, whatever the language of the project.

Three attitudes carry everything else:

**First: the project's rules come first.** Projects differ on when to commit, how to write the message and which checks count. Some want a commit after every finished step without asking, others only when the user says so. The skill reads the rules before it acts and follows them over its own defaults.

**Second: green before recorded.** Every commit passes the same checks CI runs. A commit that is red on its own breaks bisecting and reverting, even when the branch is green at the end.

**Third: local is the agent's, remote is the user's.** A commit stays on the machine and can still be changed. A push puts it on a server, starts CI and is seen by others. A merge changes the main line. Both wait for the user's word.

## Language of the answer

The report follows the user's language. Commit messages, branch names and changelog entries follow the language of the project, which is usually English.

## Procedure

### Step 1: Read the project's rules

Look for the rules before the first change:

- Instruction files such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md` and the agent's memory for this project.
- When to commit: after each step or only when asked. When unknown, commit only when asked.
- The message style: language, tense, a prefix scheme, a required trailer such as `Co-Authored-By`.
- The changelog: whether there is one, and what goes into it.
- Branch protection: whether the main branch takes direct commits or only pull requests.
- The commit identity: `git config user.name` and `user.email` as the repository sets them. When the project keeps a private address out of its history, check that the repository-local identity is set before the first commit.

### Step 2: Find the checks

Find what CI runs and run the same locally, through the project's own runner. Look in this order:

1. The CI configuration, such as `.github/workflows/`, `.gitlab-ci.yml` or `Jenkinsfile`. It is the truth, because it decides whether a pull request can merge.
2. A task runner: `Makefile`, `justfile`, `Taskfile.yml`, the scripts in `package.json`, `composer.json` or `pyproject.toml`.
3. A pre-commit configuration such as `.pre-commit-config.yaml` or `lefthook.yml`.
4. The instruction files from step 1.

Sort what you find into the usual kinds:

| Kind | Examples |
|---|---|
| Format check | `ruff format --check`, `prettier --check`, `cargo fmt --check`, `gofmt -l` |
| Lint | `ruff check`, `eslint`, `cargo clippy`, `go vet`, `shellcheck` |
| Types | `mypy`, `tsc --noEmit`, `phpstan` |
| Tests | `pytest`, `npm test`, `cargo test`, `go test ./...` |
| Lock and dependencies | `uv lock --check`, `npm ci`, `cargo check --locked` |
| Project checks | link checks, a check for private data, a generated file that must match its source |

Run the tools the way the project runs them, through its runner and its locked versions, not a global install. When the project has no checks at all, say so once in the report and commit without them.

### Step 3: Choose the branch

Check where you stand: `git status`, `git branch --show-current`, `git log --oneline -5`.

- **The main branch.** When it is protected or the project works with pull requests, never commit on it. Create a branch from an up-to-date main.
- **A branch whose pull request is merged or closed.** Do not commit there. A push would bring the deleted branch back. Ask the hosting service for the state, for example `gh pr view <n> --json state`, then start a new branch from the updated main.
- **An open branch with a subject.** Decide by the subject, not by the file type:
  - **Belongs on it:** the work itself, fixes and review findings that come up while doing it, tests for it, the changelog entry, documentation the change made wrong.
  - **Does not belong:** a new feature, a new design idea, a document for something this branch does not build.
- **A change that does not belong.** Say so in one sentence before writing code: the current branch, its subject, and that the request is a new one. Then work on a new branch from main, unless the user wants it on the current one.

A new branch gets a short name with a type prefix the project uses, such as `feat/`, `fix/`, `docs/`, `ci/` or `chore/`. Before working on a branch that may be shared, run `git log --oneline main..HEAD` and look for commits that are not yours. Another session or person may work there too.

### Step 4: Plan the commits

One logical change per commit:

- A list of findings becomes one commit per item, and an item that bundles several bugs becomes one commit per bug.
- A feature becomes a commit per layer or step, for example the data model, then the interface, then the documentation.
- Each step carries its own tests and its own changelog entry.
- Files the checks hold equal go into one commit, such as a version number in several places. Splitting them leaves red commits.
- A fix to an earlier commit of the same branch is a new commit, not an amend. Amend only a commit that was never pushed, and only when the project does so.

Never put a whole branch into one commit.

### Step 5: Prepare what goes in

1. **Ignore rules first.** When a change adds or moves files, check the ignore files before staging: `.gitignore`, and for container builds `.dockerignore`. Check anything that looks secret with `git check-ignore -v <path>` and look at `git status --ignored`. Adjust the rules in the same commit.
2. **Stage by path.** Add the files of this step by name, not with `git add -A` across unrelated changes. Then read `git diff --staged` in full.
3. **No secrets.** No token, password, key or `.env` content in the diff. No private address of the user.
4. **No leaks across projects.** When the project must stand on its own, it carries no names of other private projects, no local paths such as a home directory and no private email address. Search the staged diff for them.
5. **The changelog entry.** Add it only for what a user of the project would notice: behaviour, interface, configuration, dependencies, packaging. Work notes, research and process rules do not belong there.

### Step 6: Run the checks

Run every check from step 2 on the staged state, and fix until all are green.

- Read each exit code. A pipe such as `| tail` returns the exit code of the last command and can let a red run through. Write the output to a file, check the code, then read the file.
- When a test is new, check that it fails without the fix. Set the source file back to its old state, leaving the test in place, run the test, then restore the source.
- When CI fails on one version only, such as one language version in a matrix, reproduce it locally on exactly that version before changing code.
- A generated file the project checks in is generated again and compared.

A failing check is never skipped or switched off to get a commit through. Hooks are not bypassed with flags like `--no-verify`.

### Step 7: Write the message

Write it from the staged diff, not from memory of the work.

- **Subject:** imperative, short, says what the commit changes, in the project's style.
- **Body:** what changed and why, as far as the reason is known. A reason the user gave is stated as theirs. A reason the agent made up is left out.
- **No invented history.** No "for weeks", "since the last release" or "nobody missed it" unless the history was looked up with `git log`.
- **The trailer** the project or the session requires.

Pass the message through a file or standard input, for example `git commit -F <file>`. A message quoted inline on a command line can lose quotes, backslashes or line breaks in the shell.

### Step 8: Check the commit

- `git show --stat HEAD` holds the intended files and nothing else.
- `git status` shows no leftover change of this step.
- The author is the expected identity.

### Step 9: Report and stop

Report in a few lines: the branch, each new commit with its subject, the checks that ran and their result, and anything skipped with its reason. Then stop.

## After the commit

Each of these steps waits for the user's word. A word for one step does not cover the next.

- **Push.** Before pushing more commits to a branch with a pull request, check that the pull request is still open. Before the first push of a branch, look at `git log --oneline main..HEAD` once more and name every commit that is not yours.
- **Pull request.** Open it with a description of what changed. When the user merges themselves, report the link and do not wait for the checks.
- **Merge.** Only with an explicit permission for this pull request. A permission for one pull request does not carry over to the next. Wait for the required checks, then merge the way the project does, often as a squash.
- **After the merge.** Ask the hosting service for the state in a call of its own. Only when it says merged, switch to main, pull with `--ff-only` and delete the local branch. Never chain the cleanup to a state you printed without checking it.
- **Release.** Never part of this workflow. The user decides when to release.

## What this skill does not do

- It does not push, open a pull request or merge without the user's word.
- It does not release, tag or change repository settings.
- It does not change the project's checks to get a commit through.
- It does not rewrite pushed history or force-push.
- It does not add improvements nobody asked for. An idea goes into the report as a proposal.

---

# Appendix: traps

The cases below are the ones that went wrong in practice. Check each before committing.

## 1. A status report is no permission

"It is merged" reports what the user did. It does not allow the next step, such as a release or another merge.

## 2. A pushed branch whose pull request was merged

Pushing to it brings the deleted branch back on the server, and the commit needs a new pull request. Check the state before every push.

## 3. A printed state is not a checked state

A chain like `gh pr view ... && git branch -D ...` runs on even when the state says open, because printing does not fail. Check the state, read it, then clean up.

## 4. Backslashes and line breaks through the shell

A heredoc or an inline string can halve backslashes or turn `\n` into a real line break. Edits with backslashes go through the agent's file editing tool or a script file. A patch script checks that each replacement matched exactly once.

## 5. Line endings

Writing files on Windows can turn line endings into CRLF. Keep the endings the repository uses, and let a `.gitattributes` rule normalise them.

## 6. Ignore rules a commit too late

A `.env` beside a new configuration file, or a new build folder, reaches the history because the ignore rules were updated afterwards. What is in a pushed history stays there.

## 7. The editor's view is stale

An editor may show a file as tracked or changed when git no longer does. Trust `git status`, `git ls-files` and `git check-ignore -v`, not the file tree.

## 8. Quick check before reporting

- Every commit holds one change and passed every check on its own.
- Every commit sits on the branch whose subject it belongs to.
- No secret, private path or private address is in the diff.
- The changelog has an entry for each user-facing change.
- Nothing was pushed, merged or released without the user's word.
