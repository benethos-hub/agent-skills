# Lookups per ecosystem

Commands that show what is newer, without changing anything. Run them through the project's own runner and its locked tool versions. Where a command needs a plugin, the project may not have it. Then fall back to the registry of the ecosystem.

## Contents

- [Packages](#packages)
- [Container images](#container-images)
- [CI actions](#ci-actions)
- [Runtimes](#runtimes)
- [Known vulnerabilities](#known-vulnerabilities)

## Packages

| Ecosystem | Lock file | What is newer | Refresh |
|---|---|---|---|
| Python, uv | `uv.lock` | `uv lock --upgrade --dry-run` | `uv lock --upgrade` |
| Python, Poetry | `poetry.lock` | `poetry show --outdated` | `poetry update` |
| Python, pip-tools | `requirements*.txt` | `pip list --outdated` in the environment | `pip-compile --upgrade` |
| Node, npm | `package-lock.json` | `npm outdated` | `npm update` |
| Node, pnpm | `pnpm-lock.yaml` | `pnpm outdated` | `pnpm update` |
| Node, Yarn | `yarn.lock` | `yarn outdated` (classic), `yarn upgrade-interactive` (Berry) | `yarn upgrade` or `yarn up` |
| Rust | `Cargo.lock` | `cargo update --dry-run` | `cargo update` |
| Go | `go.sum` | `go list -m -u all` | `go get -u ./...` then `go mod tidy` |
| PHP | `composer.lock` | `composer outdated --direct` | `composer update` |
| Ruby | `Gemfile.lock` | `bundle outdated` | `bundle update` |
| .NET | `packages.lock.json` | `dotnet list package --outdated` | `dotnet add package <name>` per package |
| Java, Maven | none | `mvn versions:display-dependency-updates` | edit `pom.xml` |
| Java, Gradle | `gradle.lockfile` | a versions plugin, if the project has one | `gradle dependencies --write-locks` |

A refresh within the ranges changes only the lock file. A raise of a range changes the manifest and reaches everyone who installs the project, so it is a question for the user (step 4).

Lock files can also sit next to scripts, actions or tools, not only at the root. Search for them by name.

A platform that installs its own packages, such as the plugin manager of a content system, keeps its versions outside the repository. List them, but update them through the platform and only where the project says so.

## Container images

### Without Docker

Every registry answers over HTTP. A pull token for a public image needs no login.

Docker Hub (official images under `library/<name>`):

```bash
# Tags, newest first by push date
curl -s "https://hub.docker.com/v2/repositories/library/python/tags/?page_size=100&ordering=last_updated"

# Digest of a tag: token, then a HEAD request on the manifest
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/python:pull" | jq -r .token)
curl -sI -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json" \
  "https://registry-1.docker.io/v2/library/python/manifests/3.15-slim" | grep -i docker-content-digest
```

GitHub Container Registry:

```bash
TOKEN=$(curl -s "https://ghcr.io/token?scope=repository:<owner>/<image>:pull" | jq -r .token)
curl -s -H "Authorization: Bearer $TOKEN" "https://ghcr.io/v2/<owner>/<image>/tags/list?n=1000"
```

The same HEAD request on `https://ghcr.io/v2/<owner>/<image>/manifests/<tag>` gives the digest. Other registries follow the same API, some without a token, such as `gcr.io`.

A tag list is often sorted by name or by age and split into pages. For the newest version, the release list of the project behind the image is easier, for example `gh release list -R <owner>/<repo>`.

### With tools

`docker buildx imagetools inspect <image>:<tag>`, `crane digest <image>:<tag>` and `skopeo inspect docker://<image>:<tag>` all show the digest.

### Which digest

The `Content-Type` of the answer should be an image index or manifest list. That digest covers every platform and is the one to pin, as `<image>:<tag>@sha256:<digest>`. The digest of a single platform, as `docker images --digests` shows it after a local pull, breaks the build on every other platform.

## CI actions

GitHub Actions:

```bash
# Newest releases
gh release list -R <owner>/<action> --limit 5

# The commit a tag points to, also for annotated tags
gh api repos/<owner>/<action>/commits/<tag> --jq .sha

# Does the major tag still move?
gh api repos/<owner>/<action>/git/matching-refs/tags/v<major> --jq '.[].ref'
```

Pin as `uses: <owner>/<action>@<sha> # v<x.y.z>`. When the major tag in the list is older than the newest release, the action stopped moving it.

Reusable workflows of the project's own organisation may be called by branch on purpose. That is a rule to find in step 1, not a pin to fix.

Images of CI jobs and services, such as `image:` in GitLab CI, are container images and follow the section above.

## Runtimes

`https://endoflife.date/api/<product>.json` lists every release line with its newest patch and its end of support, for example for `python`, `nodejs`, `go`, `php`, `ruby`, `postgresql` and many images. A new line is a question for the user, a new patch of the current line is not.

When a project moves to a new runtime line, the version often stands in many places: the version file, the CI matrix, the package classifiers, the image tags, the documentation and tests that compare these. Search for the old version string after the change.

## Known vulnerabilities

| Ecosystem | Audit |
|---|---|
| any lock file | `osv-scanner scan source -r .` |
| Python | `pip-audit` |
| Node | `npm audit`, `pnpm audit` |
| Rust | `cargo audit` |
| Go | `govulncheck ./...` |
| PHP | `composer audit` |
| Ruby | `bundle audit` |
| .NET | `dotnet list package --vulnerable` |

Use the audit the project's CI runs, when it has one.
