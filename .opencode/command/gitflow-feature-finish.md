---
description: Finish a Git Flow feature branch
---

Finish a Git Flow feature branch by merging it into `develop` and cleaning up. Prefer opening a PR so CI can validate before merge; a direct-merge fallback is included.

Example: /gitflow-feature-finish bpp-consolidation

Preferred (PR-based, recommended):
```bash
# Ensure branch exists on remote
git fetch --all --prune
git checkout feature/$ARGUMENTS || git checkout -b feature/$ARGUMENTS origin/feature/$ARGUMENTS
git push -u origin feature/$ARGUMENTS

# Create PR into develop and merge after checks pass
gh pr create -B develop -H feature/$ARGUMENTS -t "Merge feature/$ARGUMENTS" -b "Finishes feature $ARGUMENTS"
gh pr merge --merge --delete-branch

# Update local develop
git checkout develop && git pull --ff-only
```

Direct merge fallback (no PR):
```bash
# Guardrails and update
git fetch --all --prune
[ -z "$(git status --porcelain)" ] || { echo "Working tree dirty" >&2; exit 1; }
git checkout develop
git pull --ff-only

# Merge and validate locally
git merge feature/$ARGUMENTS   # Resolve conflicts if any
make check                     # ruff, mypy, pytest

# Publish and clean up
git push origin develop
git branch -d feature/$ARGUMENTS
git push origin --delete feature/$ARGUMENTS || true
```
