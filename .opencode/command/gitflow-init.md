---
description: Initialize Git Flow develop branch
---

Create and push the initial `develop` branch from `main`. Use once when setting up Git Flow.

Example usage: /gitflow-init
This should create and checkout the develop branch from main, then push it to remote.

```bash
git fetch --all --prune
[ -z "$(git status --porcelain)" ] || { echo "Working tree dirty" >&2; exit 1; }
git checkout -B develop main
git push -u origin develop
```
