---
description: Finish a Git Flow release branch
---

Finish a Git Flow release by integrating into `main` and `develop`, tagging `v$ARGUMENTS`, and cleaning up. Prefer PRs so CI validates before merge; a direct-merge fallback is included.

Example: /gitflow-release-finish 1.0.0

Preferred (PR-based, recommended):
```bash
git fetch --all --prune

# PR: release -> main
gh pr create -B main -H release/$ARGUMENTS -t "Release $ARGUMENTS" -b "Merge release/$ARGUMENTS into main"
gh pr merge --merge --delete-branch   # or --squash

# Tag and publish GitHub Release (creates tag if missing and pushes it)
make release VERSION=$ARGUMENTS TITLE="v$ARGUMENTS: release"

# PR: release -> develop (carry version/doc bumps)
gh pr create -B develop -H release/$ARGUMENTS -t "Back-merge release $ARGUMENTS" -b "Merge release/$ARGUMENTS into develop"
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
git merge release/$ARGUMENTS     # Resolve conflicts
git push origin main

git tag -a v$ARGUMENTS -m "v$ARGUMENTS: release"
git push origin v$ARGUMENTS

# Merge back to develop
git checkout develop
git pull --ff-only
git merge release/$ARGUMENTS     # Resolve conflicts
git push origin develop

# Cleanup
git branch -d release/$ARGUMENTS || true
git push origin --delete release/$ARGUMENTS || true
```
