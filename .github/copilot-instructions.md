---
description: 'Azure DevOps wiki Markdown and Mermaid conventions'
applyTo: '**/*.md'
---

# Azure DevOps Wiki Conventions

Our documentation lives in an Azure DevOps project wiki. Apply these rules to any Markdown
intended for that wiki.

## Diagrams

**Always use the `::: mermaid` container fence.** A ```` ```mermaid ```` block does not render
in Azure DevOps — it shows as a plain code block.

```text
::: mermaid
flowchart TD
    A[Client] --> B[API]
:::
```

**Azure DevOps runs Mermaid 8.13.9.** Only these types render:
`flowchart` / `graph`, `sequenceDiagram`, `stateDiagram-v2`, `gantt`, `pie`, `journey`,
`requirementDiagram`.

Never emit `erDiagram`, `gitGraph`, `C4Context` / `C4Container` / `C4Component`, `mindmap`,
`timeline`, `quadrantChart`, or any `*-beta` type. If the user asks for one, say that Azure
DevOps cannot render it and offer a flowchart equivalent instead of silently producing
something broken.

Never emit syntax newer than 8.13.9: `A@{ shape: ... }`, Markdown strings in labels,
in-diagram YAML frontmatter, `%%{init: ...}%%`, `~~~` links, or `click` handlers.

**Do not trust the VS Code preview.** It ships modern Mermaid; Azure DevOps does not.
Validate before committing:

```bash
python3 .github/skills/ado-wiki-mermaid/scripts/validate_ado_mermaid.py <file.md>
```

## Diagram quality

- Cap a diagram at ~16 nodes. Split larger systems across wiki subpages.
- Quote reserved words used as node ids: `End["end"]`, never bare `end`.
- Every `classDef` that sets `fill:` must also set `color:` — the wiki has a dark theme.
- Maximum two levels of `subgraph` nesting.
- No blank lines inside a `::: mermaid` fence.
- Derive nodes from real code, config, or infrastructure. Never invent a component.

## Page structure

- One `.md` file per page; a folder of the same name holds its subpages.
- `.order` controls sibling ordering.
- Page links are root-relative without the extension: `[Text](/Parent/Child)`.
- Attachments: `/.attachments/name.png` — leading slash.
- Add `[[_TOC_]]` to any page with three or more `##` sections.

## Writing

- Lead with what the reader needs to do, then the detail.
- One `#` H1 per page, matching the page name.
- Prefer a table over prose for anything with more than three parallel facts.
- Fenced code blocks always declare a language.
- Keep a diagram's `.mmd` source under `docs/diagrams/` when it is generated from code.

For the full reference — escaping, theming, ER/C4 substitute patterns, troubleshooting —
see `.github/skills/ado-wiki-mermaid/references/ado-wiki-reference.md`.
