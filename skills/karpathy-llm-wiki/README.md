# karpathy-llm-wiki

**One skill to build your own Karpathy-style LLM wiki.**

[![Agent Skills](https://img.shields.io/badge/Agent_Skills-compatible-blue)](https://agentskills.io)

<p align="center">
  <img src="assets/karpathy-tweet.png" alt="Karpathy's tweet about LLM Wiki" width="560">
</p>

## Install

```bash
npx add-skill Astro-Han/karpathy-llm-wiki
```

Works with Claude Code, Cursor, Codex, and other tools that support the [Agent Skills](https://agentskills.io) standard.

## Quick Start

**1. Ingest your first source**

Give the skill a URL, a file, or paste text directly:

> "Ingest this article: https://example.com/attention-is-all-you-need"

The skill fetches the content into `raw/`, then compiles it into a wiki article under `wiki/`.

**2. Ask your wiki a question**

> "What do I know about attention mechanisms?"

The skill searches your wiki and answers with citations linking back to your articles.

**3. Keep it healthy**

> "Lint my wiki"

The skill checks for broken links, missing index entries, stale cross-references, and reports potential issues.

## How It Works

Inspired by [Karpathy's LLM Wiki idea](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):

> "The LLM writes and maintains the wiki; the human reads and asks questions."

The skill manages two directories in your project:

```
your-project/
├── raw/            ← Immutable source material (you or the LLM add, never modify)
│   └── 2026-04-03-source-article.md
├── wiki/           ← Compiled knowledge (LLM maintains)
│   ├── summaries/  ← Summary files for each raw article
│   │   └── 2026-04-03-slug_summary.md
│   ├── concepts/
│   │   └── concept-name.md
│   ├── index.md    ← One-page table of contents
│   └── log.md      ← Append-only operation log
```

Three operations:

| Operation | What it does |
|-----------|-------------|
| **Ingest** | Fetch a source into `raw/`, compile into `wiki/`, update index and cross-references |
| **Query** | Search the wiki and answer with citations. Optionally archive answers as wiki pages |
| **Lint** | Auto-fix broken links and index gaps. Report contradictions, orphan pages, stale content |

The wiki compounds over time. Each new source enriches existing articles, adds cross-references, and flags conflicts.

## Compatibility

This skill follows the [agentskills.io](https://agentskills.io) open standard. It works with any LLM coding tool that supports SKILL.md:

| Tool | Install method |
|------|---------------|
| Claude Code | `npx add-skill Astro-Han/karpathy-llm-wiki` |
| Cursor | `npx add-skill Astro-Han/karpathy-llm-wiki` (auto-converts) |
| Codex CLI | Copy to `.agents/skills/karpathy-llm-wiki/` |
| Others | Copy `SKILL.md` + `references/` to your tool's skill directory |

## Inspired By

This is an unofficial community implementation of the LLM Wiki workflow described in [Karpathy's idea file](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (April 2026). The core value is a battle-tested set of compilation principles and workflow templates, not the code itself.
