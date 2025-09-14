---
description: Check Git Flow branch status
---

Check current Git Flow status: current branch, local/remote feature/release/hotfix branches, and recent commits on `develop` and `main`.

```bash
# Refresh refs
git fetch --all --prune

# Current branch and short status
git status -sb

# Local feature/release/hotfix branches (most recent first)
git for-each-ref --sort=-committerdate --format='%(HEAD) %(color:yellow)%(refname:short)%(color:reset) - %(color:blue)%(committerdate:relative)%(color:reset) %(contents:subject)' refs/heads/feature refs/heads/release refs/heads/hotfix

# Remote feature/release/hotfix branches
git for-each-ref --sort=-committerdate --format='  %(color:yellow)%(refname:short)%(color:reset) - %(color:blue)%(committerdate:relative)%(color:reset) %(contents:subject)' refs/remotes/origin/feature refs/remotes/origin/release refs/remotes/origin/hotfix

# Recent history on integration and production
git log --decorate --oneline --graph -n 10 develop || true
git log --decorate --oneline --graph -n 10 main || true
```
