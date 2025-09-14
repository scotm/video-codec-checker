---
description: Start a new Git Flow feature branch
---

Create a new Git Flow feature branch from the `develop` branch. The branch should be named `feature/$ARGUMENTS` where `$ARGUMENTS` is the feature name provided by the user. Ensure a clean working tree and an up-to-date `develop`, then create and push the new branch.

Example usage: /gitflow-feature-start bpp-consolidation
This should create and checkout branch feature/bpp-consolidation from develop, then push it to remote.

```bash
git fetch --all --prune
[ -z "$(git status --porcelain)" ] || { echo "Working tree dirty" >&2; exit 1; }
git checkout develop
git pull --ff-only

git checkout -b feature/$ARGUMENTS
git push -u origin feature/$ARGUMENTS
```
