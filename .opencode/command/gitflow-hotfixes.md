---
description: List active Git Flow hotfix branches
---

List active Git Flow hotfix branches (local and remote), with last commit subject, relative date, and author. Sorted by most recent.

Local hotfix branches:
```bash
git for-each-ref --sort=-committerdate --format='%(HEAD) %(color:yellow)%(refname:short)%(color:reset) - %(contents:subject) %(color:blue)%(committerdate:relative)%(color:reset) (%(authorname))' refs/heads/hotfix
```

Remote hotfix branches:
```bash
git for-each-ref --sort=-committerdate --format='  %(color:yellow)%(refname:short)%(color:reset) - %(contents:subject) %(color:blue)%(committerdate:relative)%(color:reset) (%(authorname))' refs/remotes/origin/hotfix
```
