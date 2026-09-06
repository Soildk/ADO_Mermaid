---
name: ado-wiki-mermaid
description: Create and fix Mermaid diagrams that actually render in an Azure DevOps project wiki. Use when writing, reviewing, or troubleshooting diagrams in Azure DevOps wiki pages, .md wiki content, or wiki subpages — including architecture, flow, sequence, state, Gantt, pie, user journey, and requirement diagrams. Enforces the Azure DevOps Mermaid 8.13.9 subset and the ::: mermaid fence, and rejects syntax that silently fails to render.
license: MIT
metadata:
  version: "1.0"
  based_on: SpillwaveSolutions/design-doc-mermaid (MIT) — retargeted from GitHub/Confluence to Azure DevOps
  target: Azure DevOps Services project wiki, Mermaid 8.13.9
---

# Azure DevOps Wiki Mermaid

Author diagrams that render on the **first** save in an Azure DevOps project wiki.

Azure DevOps pins Mermaid to **8.13.9** (Sprint 200, Oct 2022) and uses a **non-standard fence**.
Most Mermaid guidance on the internet targets Mermaid 10/11 on GitHub and will produce diagrams
that render as a raw text block or an error box in ADO. This skill is the ADO-correct subset.

## ⛔ The two rules that break everything

### Rule 1: Use the `::: mermaid` fence

Azure DevOps wiki does **not** render ```` ```mermaid ```` blocks. It uses a container fence:

```text
::: mermaid
flowchart TD
    A[Client] --> B[API]
:::
```

- Opening line is exactly `::: mermaid`
- Closing line is exactly `:::`
- There is a **space** between `:::` and `mermaid`

If a diagram renders as plain text, this is the cause 90% of the time.
(A `` ```mermaid `` fence is a long-standing feature request, not current behavior.
If your organization is on a newer Azure DevOps Server build that supports it, verify on
one page before switching the whole wiki.)

### Rule 2: Only these diagram types exist

Verified against the Sprint 200 release note that set the 8.13.9 version.

**✅ Supported**

| Type | Keyword |
|---|---|
| Flowchart | `flowchart TD` / `graph TD` |
| Sequence | `sequenceDiagram` |
| State | `stateDiagram-v2` |
| Gantt | `gantt` |
| Pie | `pie` |
| User journey | `journey` |
| Requirement | `requirementDiagram` |

**❌ Not supported — will NOT render**

| Type | Use instead |
|---|---|
| `erDiagram` | Explicitly excluded (experimental in 8.13.9). Use a `flowchart` with `1..*` edge labels, or a Markdown table. |
| `gitGraph` | Explicitly excluded (experimental in 8.13.9). Use a `flowchart LR`. |
| `C4Context` / `C4Container` / `C4Component` | Does not exist in 8.13.9. Use a `flowchart` with `subgraph` boundaries. |
| `mindmap`, `timeline`, `quadrantChart`, `sankey`, `block`, `xychart` | All post-8.13.9. Use flowchart, Gantt, or a table. |
| `classDiagram` | Renders in practice but is **not** in the Sprint 200 list. Treat as unverified: check on one page before relying on it across the wiki. |

**Never suggest a diagram type outside the supported table.** If the user asks for an ER diagram
or a C4 model, say plainly that Azure DevOps cannot render it and offer the flowchart equivalent.

## Version-gated syntax (8.13.9)

Everything below is newer than 8.13.9 and must not be emitted:

- **YAML frontmatter config** — `---\nconfig:\n  theme: ...\n---` inside the diagram. Not supported.
- **`%%{init: {...}}%%`** directives — unreliable in ADO; avoid entirely.
- **New node shapes** — `A@{ shape: rect }` syntax is Mermaid 11. Use `A[text]`, `A(text)`, `A[(text)]`, `A{text}`, `A((text))`.
- **`~~~` invisible links**, `&` multi-node chaining edge cases, and elk layout — avoid.
- **Markdown strings in labels** — `` A["`**bold**`"] `` is Mermaid 9.4+. Use plain text.
- **`click` handlers** — ADO blocks JavaScript. They will never fire.

## Authoring rules

1. **Derive from reality.** Nodes come from the code, config, pipeline, or resource group in front of you. Never invent a service to make a diagram look complete.
2. **Cap at ~16 nodes.** Beyond that, split into a parent overview page and child detail subpages — the wiki hierarchy is there for exactly this. Write `+N more` rather than silently truncating.
3. **Quote reserved words.** `end`, `default`, `graph`, `class`, `click`, `style` as a node id will break the parser. Write `End["end"]`, not `end`.
4. **Every `classDef` sets `color:`.** ADO wiki has a dark theme. A light `fill:` without an explicit dark `color:` produces unreadable text for half your colleagues.
5. **Keep `subgraph` nesting to two levels.** Deeper nesting lays out unpredictably in 8.13.9.
6. **No blank line inside the fence.** A blank line can terminate the container block early.
7. **Escape special characters in labels.** Use `#quot;` for quotes and `<br/>` for line breaks. Parentheses inside a `[]` label need quoting: `A["Service (v2)"]`.
8. **One diagram per concept.** Two clear diagrams beat one dense one.

## Workflow

1. Identify the diagram type from the request. Check it against the supported table. If it is unsupported, stop and offer the alternative.
2. Read the matching guide in `references/upstream-guides/diagrams/` only if you need type-specific patterns.
3. Write the diagram using the `::: mermaid` fence.
4. **Validate before handing it over:**

   ```bash
   python3 scripts/validate_ado_mermaid.py <file.md>
   ```

   This catches the wrong fence, unsupported diagram types, post-8.13.9 syntax, unquoted
   reserved words, and `classDef` without `color:`. Fix everything it reports.
5. If the user reports it still does not render, consult `references/ado-wiki-reference.md`
   troubleshooting section.

## ADO wiki page conventions

- **Page = file.** `Architecture.md` is the page; `Architecture/` is the folder holding its subpages.
- **`.order`** in each folder controls sibling page order.
- **Attachments** live in `.attachments/` at the wiki root. Link as `![alt](/.attachments/name.png)` — leading slash, root-relative.
- **Page links:** `[Text](/Parent/Child)` — root-relative, no `.md` extension, `%2D` for a literal hyphen in a page name.
- **Table of contents:** `[[_TOC_]]` on its own line.
- Keep the `.mmd` source in the repo under `docs/diagrams/` when a diagram is generated from code, so it can be regenerated rather than hand-patched.

## References

- `references/ado-wiki-reference.md` — full ADO constraints, escaping table, troubleshooting, flowchart substitutes for ER/C4.
- `references/upstream-guides/diagrams/` — per-type authoring patterns (sequence, activity, architecture, deployment).
- `references/upstream-guides/troubleshooting.md` — general Mermaid errors. **Note:** written for newer Mermaid; ignore any advice that conflicts with the version gates above.
- `references/templates/` — design-doc skeletons (architecture, API, database, system, feature).
- `scripts/validate_ado_mermaid.py` — the linter. No dependencies, Python 3 stdlib only.

## Attribution

The guides under `references/upstream-guides/` and the skeletons under `references/templates/`
come from [design-doc-mermaid](https://github.com/SpillwaveSolutions/design-doc-mermaid) by
Rick Hightower / Spillwave Solutions (MIT), retargeted here from GitHub/Confluence to Azure
DevOps. The authoring philosophy above — node budgets, reserved-word escaping, `classDef`
contrast, deriving diagrams from real code — originates with that skill.

Those files target newer Mermaid. **Where they conflict with this file or
`references/ado-wiki-reference.md`, the Azure DevOps rules win.** See `NOTICE` at the repo
root for file-by-file attribution.
