---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
---

# Find Skills

Discover and install skills from the open agent skills ecosystem.

## When to Use

Use when the user asks how to do a task, wants to find/search for a skill, or wants to extend agent capabilities with specialized tools, templates, or workflows.

## Skills CLI

The Skills CLI (`npx skills`) is the package manager for agent skills.

- `npx skills find [query]` - Search by keyword
- `npx skills add <package>` - Install a skill
- `npx skills check` - Check for updates
- `npx skills update` - Update all installed skills

Browse at: https://skills.sh/

## Workflow

### 1. Check the Leaderboard First

Before running a CLI search, check the [skills.sh leaderboard](https://skills.sh/) — it ranks skills by total installs, surfacing popular, battle-tested options. Top sources include `vercel-labs/agent-skills` (React, Next.js, web design) and `anthropics/skills` (frontend design, document processing).

### 2. Search via CLI

If the leaderboard doesn't cover the need:

```bash
npx skills find [query]
```

Example: user asks about React performance → `npx skills find react performance`

### 3. Verify Quality Before Recommending

Do not recommend based solely on search results. Check:

- **Install count** — prefer 1K+; be cautious under 100
- **Source reputation** — official sources (`vercel-labs`, `anthropics`, `microsoft`) are more trustworthy
- **GitHub stars** — treat repos with <100 stars with skepticism

### 4. Present Options

For each relevant skill, tell the user: name and purpose, install count and source, the install command, and a skills.sh link.

### 5. Install

If the user wants to proceed:

```bash
npx skills add <owner/repo@skill> -g -y
```

`-g` installs globally (user-level), `-y` skips confirmation prompts.

## When No Skills Are Found

Acknowledge no match was found, offer to help directly, and suggest `npx skills init` if they want to create their own skill.
