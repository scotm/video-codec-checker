---
description: List active Git Flow feature branches
---

List all active Git Flow feature branches (local and remote), with last commit subject, relative date, and author. Sorted by most recent.

Local feature branches:
```bash
git for-each-ref --sort=-committerdate --format='%(HEAD) %(color:yellow)%(refname:short)%(color:reset) - %(contents:subject) %(color:blue)%(committerdate:relative)%(color:reset) (%(authorname))' refs/heads/feature
```

Remote feature branches:
```bash
git for-each-ref --sort=-committerdate --format='  %(color:yellow)%(refname:short)%(color:reset) - %(contents:subject) %(color:blue)%(committerdate:relative)%(color:reset) (%(authorname))' refs/remotes/origin/feature
```
