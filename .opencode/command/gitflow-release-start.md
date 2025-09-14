---
description: Start a new Git Flow release branch
---

Create a new Git Flow release branch from `develop`. The branch should be named `release/$ARGUMENTS` where `$ARGUMENTS` is the release version (e.g., `0.7.5`). Ensure a clean working tree and an up-to-date `develop`, then create and push the branch.

Example usage: /gitflow-release-start 1.0.0
This should create and checkout branch release/1.0.0 from develop, then push it to remote.

```bash
git fetch --all --prune
[ -z "$(git status --porcelain)" ] || { echo "Working tree dirty" >&2; exit 1; }
git checkout develop
git pull --ff-only

git checkout -b release/$ARGUMENTS
git push -u origin release/$ARGUMENTS

# Next steps (on the release branch):
# - Bump version in pyproject.toml
# - Update README (What's New: last two releases) and CHANGELOG.md
# - Run: make check
```
