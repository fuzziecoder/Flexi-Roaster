# Contributing to FlexiRoaster

Thank you for your interest in contributing to FlexiRoaster! This project is participating in **Apertre'26**, and we're excited to have you on board.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Contribution Process](#contribution-process)
- [Issue Guidelines](#issue-guidelines)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Commit Message Format](#commit-message-format)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Mandatory Tags](#mandatory-tags)

---

## 📜 Code of Conduct

### Expected Behavior
- Be respectful and inclusive in all interactions
- Provide constructive feedback and accept it gracefully
- Focus on what is best for the community and the project
- Show empathy towards other community members
- Use welcoming and inclusive language

### Unacceptable Behavior
- Harassment, trolling, or personal attacks
- Publishing others' private information without consent
- Any conduct that could reasonably be considered inappropriate

Violations may result in temporary or permanent bans from the project.

---

## 🚀 Getting Started

1. **Fork the repository** to your GitHub account
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Flexi-Roaster.git
   cd Flexi-Roaster
   ```
3. **Set up the upstream remote**:
   ```bash
   git remote add upstream https://github.com/fuzziecoder/Flexi-Roaster.git
   ```
4. **Install dependencies** following the [README.md](README.md) setup instructions

---

## 🔄 Contribution Process

### Step 1: Find an Issue
- Browse the [Issues](../../issues) page
- Look for issues tagged with `apertre3.0`
- Filter by difficulty: `Easy`, `Medium`, or `Hard`
- Comment on the issue to express interest and get assigned

### Step 2: Fork & Create Branch
```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create your feature branch
git checkout -b <branch-type>/<short-description>
```

### Step 3: Make Changes
- Write clean, documented code
- Follow existing code style and conventions
- Add tests for new features when applicable
- Update documentation if needed

### Step 4: Commit Changes
```bash
git add .
git commit -m "<type>(<scope>): <description>"
```

### Step 5: Push & Create PR
```bash
git push origin <your-branch-name>
```
Then create a Pull Request on GitHub.

---

## 📝 Issue Guidelines

### Creating New Issues
1. **Check existing issues** to avoid duplicates
2. **Use descriptive titles** that summarize the problem or feature
3. **Provide detailed information**:
   - For bugs: Steps to reproduce, expected vs actual behavior, screenshots
   - For features: Use case, proposed solution, alternatives considered
4. **Apply appropriate labels**:
   - `apertre3.0` (mandatory for Apertre'26)
   - Difficulty: `Easy`, `Medium`, or `Hard`
   - Type: `bug`, `enhancement`, `documentation`, etc.

### Issue Templates
When available, use the provided issue templates for consistency.

---

## 🌿 Branch Naming Conventions

Use the following format for branch names:

```
<type>/<short-description>
```

### Types
| Type | Description |
|------|-------------|
| `feature` | New feature or enhancement |
| `bugfix` | Bug fix |
| `hotfix` | Urgent fix for production |
| `docs` | Documentation changes |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

### Examples
```
feature/add-pipeline-scheduler
bugfix/fix-websocket-disconnect
docs/update-api-documentation
refactor/optimize-database-queries
```

---

## 💬 Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
| Type | Description |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, missing semi-colons, etc. |
| `refactor` | Code change without new features or bug fixes |
| `test` | Adding or correcting tests |
| `chore` | Maintenance or tooling changes |
| `perf` | Performance improvement |

### Examples
```
feat(pipeline): add scheduled execution support

fix(websocket): resolve connection timeout on slow networks

docs(readme): update installation instructions

refactor(api): simplify authentication middleware
```

### Rules
- Use present tense ("add feature" not "added feature")
- Use lowercase for the entire message
- Keep the subject line under 72 characters
- Reference issue numbers in the footer when applicable: `Closes #123`

---

## 🔀 Pull Request Guidelines

### Before Submitting
- [ ] Ensure your code follows the project's coding standards
- [ ] Run all tests and ensure they pass
- [ ] Update documentation if you've changed APIs or added features
- [ ] Rebase your branch on the latest `main` to avoid conflicts

### PR Title Format
```
<type>(<scope>): <short description>
```

### PR Description
Include in your PR description:
1. **What**: Brief summary of changes
2. **Why**: The motivation for these changes
3. **How**: Technical approach taken
4. **Testing**: What tests were added/modified
5. **Screenshots**: For UI changes, include before/after screenshots

### Mandatory Requirements
- [ ] PR title follows the commit message format
- [ ] All checks/CI pass
- [ ] At least one reviewer approval (if required)
- [ ] No merge conflicts

---

## 🏷️ Mandatory Tags

> **Important for Apertre'26 Participants**

All issues and Pull Requests must include the following tags to be eligible for points:

### Required Tags

| Tag | Description |
|-----|-------------|
| `apertre3.0` | **Mandatory** - Identifies this as an Apertre'26 contribution |

### Difficulty Tags (Choose One)

| Tag | Points | Description |
|-----|--------|-------------|
| `Easy` | 3 points | Simple fixes, documentation updates, minor changes |
| `Medium` | 5 points | Moderate complexity, new features, significant refactoring |
| `Hard` | 10 points | Complex features, architectural changes, major implementations |

### ⚠️ Important Notes
- PRs without `apertre3.0` tag will **NOT** receive points
- PRs must have exactly **ONE** difficulty tag
- Maintainers will assign difficulty tags based on issue complexity

---

## 💡 Tips for Contributors

1. **Start small**: Begin with `Easy` issues to get familiar with the codebase
2. **Ask questions**: Don't hesitate to ask for clarification on issues
3. **Stay updated**: Regularly sync your fork with the upstream repository
4. **Be patient**: Reviews may take time; use the wait to help others
5. **Document**: Good documentation is as valuable as good code

---

## 🤝 Need Help?

- 💬 Comment on the issue you're working on
- 📧 Reach out to maintainers
- 🔍 Check existing PRs for reference

---

Thank you for contributing to FlexiRoaster and participating in Apertre'26! 🎉
