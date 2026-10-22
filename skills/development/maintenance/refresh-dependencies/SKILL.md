---
name: refresh-dependencies
description: "Refreshes everything a project pins, in any language: the packages in lock files and manifests, the container images in Dockerfiles and compose files, the actions and images of CI, the language runtime and the tools around it. Measures each newest version at its source instead of waiting for a dependency bot, leaves alone whatever the project's rules or the agent's memory exclude, asks about majors and migrations up front and checks every bump in the way its kind needs before it commits. Pushing, pull requests and merging wait for the user's word. Use this skill whenever the user asks for a dependency update, a deps refresh, an upgrade of packages, images, actions or the runtime, or wants to know what is outdated. Answers in the user's language."
license: MIT
---

# Refresh dependencies

## What this skill is for

A project depends on far more than its lock file. Base images, compose images, CI actions, the language version and tools pinned in some script all age as well. A refresh that only renews the lock file leaves a patched runtime or a security fix in the image behind. This skill finds every pin, measures what is newer, takes it and checks it.

Four attitudes carry everything else:

**First: everything pinned, not only the lock file.** Packages, images, actions, runtimes, tools and downloaded files with a checksum all count. What is pinned somewhere is part of the refresh.

**Second: measure, do not wait.** A dependency bot runs in weekly slots, proposes direct dependencies only and fails silently on what it cannot read. Its pull requests are a reminder at most. The newest version comes from its source, read during the refresh.

**Third: exclusions belong to the user.** What the project's rules or the agent's memory exclude stays exactly as it is. It is named in the report as excluded, with its source, and not proposed again without a new reason.

**Fourth: a bump is done when it is checked.** A green offline suite says that nothing broke here. It does not say that a dependency still behaves the same. Every bump gets the check its kind needs.

## Language of the answer

The report follows the user's language. Commit messages, branch names and changelog entries follow the language of the project, which is usually English.

## Procedure

### Step 1: Read the rules and collect the exclusions

Before looking at a single version, read what the project decided:

- Instruction files such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, design or specification documents, and the agent's memory for this project.
- The configuration of a dependency bot, such as `.github/dependabot.yml` or `renovate.json`: ignored packages, groups, version limits, a cooldown.
- Comments next to pins, such as "floats on purpose" or "held back until".
- When to commit and how, which checks count, and whether the main branch takes direct commits.

Write an exclusion list before going on. Each entry names the pin and its source, for example "`caddy:2` in the production compose file floats on purpose, memory of 2026-10-08". Typical exclusions are a runtime image that follows its major line on purpose, a package held at a version until an upstream fix, a version range kept wide on purpose and a rebuilt image tag the project does not follow alone.

An exclusion holds even when the item has a known vulnerability. Name the finding in the report and leave the decision to the user.

### Step 2: Find every pin

Search the whole repository, not only the usual places. The [lookup reference](references/lookups.md) lists the files and commands per ecosystem.

| Kind | Where it hides |
|---|---|
| Packages | lock files, manifests with exact versions, lock files of tools next to scripts or actions |
| Version ranges | the lower and upper bounds in manifests |
| Base images | every `FROM` of every Dockerfile and stage, `COPY --from=<image>` |
| Runtime images | compose files, Kubernetes manifests, deployment roles, `docker run` in scripts |
| CI | `uses:` of actions and reusable workflows, `image:` of jobs and services, tool versions passed to setup steps |
| Runtime | version files such as `.python-version`, `.nvmrc`, `.tool-versions`, `rust-toolchain.toml`, the `go` line, the CI matrix, classifiers, `engines`, the documentation that names the range |
| Tools | pre-commit hooks, linters and formatters in development groups, the package manager itself |
| Other pins | downloaded files with a version and checksum, vendored libraries, versions written into scripts or install commands |

Note for each pin how it is pinned: a range, an exact version, a tag, a tag with digest, a commit SHA with a version comment. The refresh keeps the style the project uses.

### Step 3: Measure what is newer

Ask each source, never memory. The reference has the commands.

- **Packages:** the package manager's dry run or outdated listing. It shows direct and transitive moves within the ranges.
- **Images:** the tag list of the registry, and the digest the pinned tag points to now. Both count. A newer tag is an update, and a new digest under the same tag is a rebuild, usually with security fixes of the base system. Pin the digest of the multi-platform index, not of one platform.
- **Actions:** the newest release of each, and the commit its tag points to. Check whether the major tag still moves. Some projects stopped publishing moving major tags, and a reference like `@v7` then stays on an old version without any sign.
- **Runtime:** the newest patch of the current line and whether a new minor line is out.
- **The bot:** its open pull requests and its failed runs. A failed run can mean that whole ecosystems get no proposals at all.

Mark a release younger than three days as such. Many projects hold those back as a cooldown.

### Step 4: List, then ask once

Write the list of everything found, one row per pin: kind, place, current version, newest version, type of jump (rebuild, patch, minor, major) and state (take, excluded with source, question).

Then ask the user everything that is theirs to decide, in one round, each with a recommendation:

- a major version, which may break the interface
- a migration rather than an update, such as a new major of a database whose data format changes
- a new minor line of the runtime, which touches the matrix, the classifiers and the documentation
- a raise of a version range, which reaches everyone who installs the project
- an exclusion that is unclear or seems outdated

Patches, rebuilds and minor versions within the ranges are taken without asking, unless a rule says otherwise. After the answers, work through without further check-ins.

### Step 5: Take the baseline

While the old versions are still installed, run the project's checks and, if it has one, its live or smoke test. Keep the output. Without it a green run afterwards cannot be told apart from a good day of the far side.

### Step 6: Apply

Work on one branch from an up-to-date main, unless the project commits elsewhere. One commit per kind, each green on its own:

1. the lock file refresh
2. the base images, tag and digest together
3. the runtime images, where the project pins them
4. the CI actions, SHA with version comment
5. a new runtime line, in every place that names the version
6. the tools and other pins

A version string that appears in several places moves in all of them in the same commit. Search the repository for the old string afterwards. Use the pin style of the project. Do not pin what the project leaves floating on purpose, and do not loosen what it pins.

### Step 7: Check every bump

| Kind | Check |
|---|---|
| Every minor or major | read the release notes. A line about breaking changes concerns the users until proven otherwise |
| Packages | the project's checks, then the baseline run again, compared section by section and not by exit code. Watch the warnings and the error output, a new deprecation warning counts |
| A suspected change in behaviour | the old version side by side in a throwaway environment, the same call in both, the output compared |
| Images | build, read the versions inside, start, check the health and one real request, then remove only the tags you created. Never clean up with a general prune |
| CI | the referenced version resolves to the expected commit. The workflow itself only proves itself on the pull request, so say that |
| Runtime | the checks on the new version locally, when it can be installed |
| Security | the project's audit of known vulnerabilities |

Say what the checks do not prove. A suite that mocks the network stays green through any change of the remote side.

### Step 8: Changelog and commit

When the project keeps a changelog, say for each entry whom the change reaches: users of the package, users of the image, or only the development environment. A bump in a development tool reaches nobody who installs the project.

Commit the way the project commits, with the checks it runs. Pass the message through a file. Each commit names what moved, from which version to which.

### Step 9: Report and stop

Report in a short form:

- the bumps taken, as a table with old and new version
- the exclusions left alone, each with its source
- what was deferred or asked, and why
- the checks that ran, and what remains unchecked
- the branch and its commits

Then stop. Push, pull request and merge wait for the user's word, and a release is never part of this skill.

## What this skill does not do

- It does not touch what the project's rules or the agent's memory exclude.
- It does not push, open a pull request, merge or release without the user's word.
- It does not take a major version or a migration without the user's answer.
- It does not switch off a failing check or a warning to get a bump through.
- It does not remove images, containers or caches it did not create.

# Appendix: traps

The cases below went wrong in practice. Check each before reporting.

## 1. Only the lock file

A refresh renewed the lock file while the image still shipped an old runtime patch and an old package manager. Every kind from step 2 belongs in every refresh.

## 2. Same tag, new digest

A base image is rebuilt under the same tag with security fixes. A bot that watches tags does not notice, and an image pinned by digest stays on the old build. Compare the digest, not only the tag.

## 3. A frozen major tag

An action stopped publishing moving major tags. A reference to the major stayed green for three majors. Check the tag list of the action against its newest release.

## 4. A silent bot

A bot could not read the runtime version file of the project and failed every week for that ecosystem. Its silence looked like nothing to do. Read its runs, not only its pull requests.

## 5. A pinned image without a name

An image pulled by digest carries no tag on the host. It shows as `<none>`, cannot be removed by that name and may not count as dangling. Remove a test image by its digest reference.

## 6. Measured on the wrong machine

The same container behaviour differed between a local virtual machine and the server. Measure behaviour where it counts.

## 7. A major that is a migration

A new major of a database changes its data format. That is a migration with its own plan, not part of a refresh.

## 8. Warnings after a bump

A new version of a library made a dependency print deprecation warnings on every call, while every result stayed the same. Compare the error output before and after, not only the results.

## 9. Quick check before reporting

- Every kind of pin from step 2 was searched.
- Every newest version was measured at its source.
- Nothing on the exclusion list changed.
- Majors, migrations and new runtime lines were asked first.
- Every bump has its check, and the unchecked rest is named.
- Nothing was pushed, merged or released without the user's word.
