---
name: send-pr
description: >-
  Commits, pushes and raises a PR. Use this skill when the user asks to "ship", "commit, push and raise PR", or similar commands.
metadata:
  disable-model-invocation: true
---

# Commit, Push and Raise PR

This skill handles the complete workflow of committing staged/unstaged changes, pushing to the remote, and raising a Pull Request.

## Workflow

1. **Analyse Changes** - Review all pending changes (staged and unstaged) to understand the scope and nature of the work
2. **Commit** - Create a well-formed conventional commit
3. **Push** - Push the current feature branch to origin
4. **Raise PR** - Create a Pull Request

## Commit Message Format

Use Conventional Commits format:
```
<type>: <description>

[optional body with more detail]
```

### Types
- `feat:` - new functionality
- `fix:` - bug fixes
- `refactor:` - code restructuring without behaviour change
- `docs:` - documentation only
- `test:` - adding or updating tests
- `chore:` - maintenance tasks, dependency updates

### Rules
- First line must be **50 characters or fewer** to avoid GitHub truncation
- Description should be lowercase, imperative mood ("add feature" not "added feature")
- Body (if needed) should be wrapped at 72 characters
- Determine the target branch by checking which of the following exists on the remote, in priority order: `develop`, `main`, `master`. Use the first one found.

## Pull Request Format

The PR title should match the first line of the commit message (including the conventional commit prefix).

Use this template for the PR body:
```markdown
## Summary
[2-3 sentences describing what this PR accomplishes and why]

## Changes
[Bullet points of the key modifications, grouped logically]

## Test Plan
- [ ] [Specific scenario to verify]
- [ ] [Another test case]
- [ ] [Edge case to check]

## Notes for Reviewers
[Any context that will help reviewers: areas of uncertainty, alternative approaches considered, architectures and patterns worthy of note, or specific files to scrutinise]
```

## Execution Steps

1. Run `git status` and `git diff` to understand all pending changes
2. Analyse the changes to determine the appropriate commit type and craft a meaningful message
3. Stage all changes with `git add -A`
4. Commit with the crafted message
5. Push the branch with `git push -u origin HEAD`
6. Determine the target branch - `develop`, `main`, or `master` in that order of priority.
6. Create the PR using `gh pr create --base <target branch> --title "<commit first line>" --body "<PR body>"`

## Important Notes

- Derive the commit message and PR content entirely from analysing the actual changes - do not ask the user to describe them
- The test plan should contain **specific, actionable** test cases derived from the changes, not generic placeholders
- If changes span multiple concerns and would benefit from separate commits, note this to the user but proceed with a single commit unless instructed otherwise
