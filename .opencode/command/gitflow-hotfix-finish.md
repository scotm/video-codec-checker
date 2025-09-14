---
description: Finish a Git Flow hotfix branch
---

Finish a Git Flow hotfix by integrating into `main` and `develop`, tagging `v$ARGUMENTS`, and cleaning up. Prefer PRs so CI validates before merge; a direct-merge fallback is included.

Example: /gitflow-hotfix-finish 0.7.4.1

Preferred (PR-based, recommended):
```bash
git fetch --all --prune

# PR: hotfix -> main
gh pr create -B main -H hotfix/$ARGUMENTS -t "Hotfix $ARGUMENTS" -b "Merge hotfix/$ARGUMENTS into main"
gh pr merge --merge --delete-branch   # or --squash

# Tag and publish GitHub Release (creates tag if missing and pushes it)
make release VERSION=$ARGUMENTS TITLE="v$ARGUMENTS: hotfix"

# PR: hotfix -> develop (carry fixes forward)
gh pr create -B develop -H hotfix/$ARGUMENTS -t "Back-merge hotfix $ARGUMENTS" -b "Merge hotfix/$ARGUMENTS into develop"
gh pr merge --merge --delete-branch || true

# Update locals
git checkout main && git pull --ff-only
git checkout develop && git pull --ff-only
```

Direct merge fallback (no PR):
```bash
git fetch --all --prune
[ -z "$(git status --porcelain)" ] || { echo "Working tree dirty" >&2; exit 1; }

# Merge to main and tag
git checkout main
git pull --ff-only
git merge hotfix/$ARGUMENTS     # Resolve conflicts
git push origin main

git tag -a v$ARGUMENTS -m "v$ARGUMENTS: hotfix"
git push origin v$ARGUMENTS

# Merge back to develop
git checkout develop
git pull --ff-only
git merge hotfix/$ARGUMENTS     # Resolve conflicts
git push origin develop

# Cleanup
git branch -d hotfix/$ARGUMENTS || true
git push origin --delete hotfix/$ARGUMENTS || true
```
