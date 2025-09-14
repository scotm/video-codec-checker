---
description: Review PR comments and address concerns systematically
---

Review all comments on the current PR, create tasks for each concern, and implement fixes.

This command will:
1. List all open PRs
2. View comments on the specified PR
3. Create a todo list from the comments
4. Make code changes to address each comment
5. Commit and push the changes

Example usage: /review-comments-and-tasks

```bash
# List open PRs
echo "Open PRs:"
gh pr list --state open

# Get PR number from user input or current branch
PR_NUMBER=${ARGUMENTS:-$(gh pr view --json number -q .number 2>/dev/null || echo "")}

if [ -z "$PR_NUMBER" ]; then
    echo "Please specify a PR number as an argument"
    exit 1
fi

echo "Reviewing comments on PR #$PR_NUMBER"

# View comments on the PR
echo "Comments on PR #$PR_NUMBER:"
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments

# Create todo list from comments
echo "Creating todo list from comments..."
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments | jq -r '.[] | "- [ ] Address comment on " + .path + " at line " + (.line|tostring) + ": " + .body' > /tmp/todo.md

echo "Todo list created:"
cat /tmp/todo.md

# Implementation steps would go here:
# 1. Parse each comment to understand the concern
# 2. Create specific tasks in a todo list
# 3. Address each task by modifying the relevant files
# 4. Commit the changes with descriptive messages
# 5. Push to the PR branch

echo "Manual steps required:"
echo "1. Review each comment and understand the concern"
echo "2. Make the necessary code changes"
echo "3. Commit and push the changes"
echo "4. Mark comments as resolved in the GitHub UI"

# Clean up
rm -f /tmp/todo.md
```