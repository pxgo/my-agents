---
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
---

# Find Skills

Discover and install skills from the open agent skills ecosystem.

## Skills CLI (`npx skills`)

- `npx skills find [query]` - Search by keyword
- `npx skills add <package>` - Install a skill
- `npx skills check` - Check for updates
- `npx skills update` - Update all installed skills

Browse at: https://skills.sh/

## Workflow

1. **Check the [leaderboard](https://skills.sh/) first** - ranks skills by installs, surfacing popular options. Top sources: `vercel-labs/agent-skills` (React, Next.js, web design), `anthropics/skills` (frontend, document processing).
2. **Search via CLI** if the leaderboard doesn't cover the need: `npx skills find [query]` (e.g. `npx skills find react performance`).
3. **Verify quality before recommending** - don't recommend based solely on search results. Prefer 1K+ installs; be cautious under 100. Favor official sources (`vercel-labs`, `anthropics`, `microsoft`). Treat repos with <100 GitHub stars with skepticism.
4. **Present options** - for each relevant skill: name and purpose, install count and source, the install command, and a skills.sh link.
5. **Install** if the user wants to proceed: `npx skills add <owner/repo@skill> -g -y` (`-g` global, `-y` skip confirmation).

## When No Skills Are Found

Acknowledge no match, offer to help directly, suggest `npx skills init` to create your own.
