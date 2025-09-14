---
description: List active Git Flow release branches
---

List active Git Flow release branches (local and remote), with last commit subject, relative date, and author. Sorted by most recent.

Local release branches:
```bash
git for-each-ref --sort=-committerdate --format='%(HEAD) %(color:yellow)%(refname:short)%(color:reset) - %(contents:subject) %(color:blue)%(committerdate:relative)%(color:reset) (%(authorname))' refs/heads/release
```

Remote release branches:
```bash
git for-each-ref --sort=-committerdate --format='  %(color:yellow)%(refname:short)%(color:reset) - %(contents:subject) %(color:blue)%(committerdate:relative)%(color:reset) (%(authorname))' refs/remotes/origin/release
```
