---
description: Start a new Git Flow hotfix branch
---

Create a new Git Flow hotfix branch from `main`. The branch should be named `hotfix/$ARGUMENTS` where `$ARGUMENTS` is the hotfix version (e.g., `0.7.4.1`). Ensure a clean working tree and an up-to-date `main`, then create and push the branch.

Example usage: /gitflow-hotfix-start 0.7.5
This should create and checkout branch hotfix/0.7.5 from main, then push it to remote.

```bash
git fetch --all --prune
[ -z "$(git status --porcelain)" ] || { echo "Working tree dirty" >&2; exit 1; }
git checkout main
git pull --ff-only

git checkout -b hotfix/$ARGUMENTS
git push -u origin hotfix/$ARGUMENTS

# Next steps (on the hotfix branch): bump patch version, update CHANGELOG/README, run: make check
```
