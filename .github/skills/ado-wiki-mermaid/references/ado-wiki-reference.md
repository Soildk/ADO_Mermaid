# Azure DevOps Wiki — Mermaid Reference

Everything ADO-specific in one place. Verified against Microsoft Learn and the
Azure DevOps Sprint 200 release note (October 2022), which pinned Mermaid to **8.13.9**.

---

## 1. The fence

Azure DevOps wiki uses a **container fence**, not a code fence:

```text
::: mermaid
flowchart TD
    A[Client] --> B[API]
:::
```

| | |
|---|---|
| Opening | `::: mermaid` — colons, space, keyword |
| Closing | `:::` on its own line |
| Backtick fence | Renders as a plain code block. Does **not** draw. |

A standard ```` ```mermaid ```` fence is an open feature request on Developer Community,
not shipped behavior. If you are on Azure DevOps Server (on-prem) with a newer build,
test one page before converting the wiki.

**Do not leave a blank line inside the fence.** The container block can terminate early.
Use a `%%` comment line if you need visual separation.

---

## 2. Supported diagram types

From the Sprint 200 release note, verbatim: *"Flowchart, Sequence diagrams, Gantt charts,
Pie charts, Requirement diagrams, State diagrams, User Journey. Diagrams that are in
experimental mode such as Entity Relationship and Git Graph are not included."*

| Type | Keyword | Notes |
|---|---|---|
| Flowchart | `flowchart TD` / `graph TD` | The workhorse. Use for architecture, C4 substitutes, ER substitutes. |
| Sequence | `sequenceDiagram` | API calls, auth flows, deployments. |
| State | `stateDiagram-v2` | Always use `-v2`. |
| Gantt | `gantt` | Roadmaps, release timelines. |
| Pie | `pie` | Rarely worth a diagram; a table is usually clearer. |
| User journey | `journey` | UX flows with satisfaction scores. |
| Requirement | `requirementDiagram` | Traceability. Verbose; consider a table. |
| Class | `classDiagram` | ⚠️ Renders in practice but **not** in the official list. Verify before wiki-wide use. |

### Not available

| Type | Why | Substitute |
|---|---|---|
| `erDiagram` | Explicitly excluded | Flowchart with cardinality edge labels, or a Markdown table |
| `gitGraph` | Explicitly excluded | `flowchart LR` |
| `C4Context` and friends | Postdates 8.13.9 | Flowchart with `subgraph` boundaries |
| `mindmap` | Mermaid 9.3+ | Flowchart |
| `timeline` | Mermaid 9.4+ | `gantt` |
| `quadrantChart`, `sankey-beta` | Mermaid 10+ | Table or external image |
| `block-beta`, `xychart-beta`, `packet-beta`, `architecture-beta`, `kanban`, `radar-beta`, `treemap-beta` | Mermaid 11+ | Flowchart or table |

---

## 3. Syntax that postdates 8.13.9

Silent failure or an error box. None of it works.

| Feature | Introduced | Instead |
|---|---|---|
| `A@{ shape: rect }` | Mermaid 11 | `A[text]`, `A(text)`, `A[(text)]`, `A{text}`, `A((text))` |
| Markdown strings `["`**bold**`"]` | 9.4 | Plain text; `<br/>` for line breaks |
| YAML frontmatter config in-diagram | 10 | Nothing — style with `classDef` |
| `%%{init: {...}}%%` | exists in 8.x but unreliable in ADO | `classDef` |
| ELK layout | 10.8 | Default dagre |
| `~~~` invisible link | 9.1 | Restructure the diagram |
| New arrow types (`--o`, `--x` variants beyond basics) | varies | `-->`, `---`, `-.->`, `==>` |

---

## 4. Escaping and labels

| Need | Write |
|---|---|
| Line break in a label | `A["Line one<br/>Line two"]` |
| Double quote | `A["He said #quot;hi#quot;"]` |
| Parentheses in a label | `A["Service (v2)"]` — quote the whole label |
| Reserved word as id | `End["end"]` — never bare `end` |
| Unicode / emoji | Works, but keep it sparing; screen readers read it aloud |

**Reserved words that break the parser as bare node ids:**
`end`, `default`, `graph`, `subgraph`, `class`, `classDef`, `click`, `style`, `linkStyle`,
`direction`, `state`, `note`.

`end` is by far the most common cause of "my flowchart won't render".

---

## 5. Theming — the contrast trap

ADO wiki honours the user's light/dark theme, and the diagram background follows it.
A `classDef` with a light `fill:` and no `color:` produces black-on-black or
white-on-white for whoever is using the other theme.

**Always pair `fill:` with an explicit `color:`.**

```text
classDef external fill:#90EE90,stroke:#333,color:#000
classDef internal fill:#1f3a5f,stroke:#88a,color:#fff
class Client,Cdn external
class Api,Db internal
```

Stick to a small palette and reuse it across pages so the wiki reads as one document.

---

## 6. Substitute patterns

### ER diagram → flowchart

```text
::: mermaid
flowchart LR
    Customer["Customer<br/>id, name, email"]
    Order["Order<br/>id, total, placed_at"]
    Item["OrderItem<br/>sku, qty, price"]
    Customer -->|"1..*"| Order
    Order -->|"1..*"| Item
    classDef ent fill:#eef,stroke:#446,color:#000
    class Customer,Order,Item ent
:::
```

For a full schema, a Markdown table per entity beats any diagram.

### C4 container view → flowchart with subgraphs

```text
::: mermaid
flowchart TD
    User["Customer"]
    subgraph System["Ordering System"]
        Web["Web App<br/>React"]
        Api["API<br/>.NET 8"]
        Db[("Database<br/>SQL Server")]
    end
    Stripe["Stripe<br/>External"]
    User --> Web
    Web --> Api
    Api --> Db
    Api --> Stripe
    classDef ext fill:#ddd,stroke:#666,color:#000
    class User,Stripe ext
:::
```

Two subgraph levels max. Deeper nesting lays out unpredictably in 8.13.9.

---

## 7. Wiki page mechanics

| Concept | Rule |
|---|---|
| Page | A `.md` file. `Architecture.md` = the page. |
| Subpages | A folder of the same name: `Architecture/` holds its children. |
| Sibling order | `.order` file in the folder, one page name per line. |
| Page link | `[Text](/Parent/Child)` — root-relative, no `.md` |
| Literal hyphen in a page name | `%2D` |
| Space in a page name | `-` in the URL |
| Attachment | `/.attachments/name.png` — leading slash, wiki root |
| Table of contents | `[[_TOC_]]` on its own line |
| Diagram source | Keep `.mmd` under `docs/diagrams/` in the repo when generated from code |

---

## 8. Troubleshooting

| Symptom | Cause |
|---|---|
| Renders as a grey code block | Backtick fence instead of `::: mermaid` |
| "Syntax error in graph" | Reserved word as node id (usually `end`), or an unquoted special character |
| Blank / cut-off diagram | Blank line inside the fence terminated the block |
| Nothing at all, no error | Unsupported diagram type (`erDiagram`, `C4Context`, `mindmap`, …) |
| Unreadable text | `classDef` with `fill:` and no `color:` |
| Works in VS Code preview, fails in ADO | VS Code ships modern Mermaid; you used post-8.13.9 syntax |
| Layout scrambled | subgraph nested more than two deep |

**The VS Code trap is the big one.** The VS Code Markdown preview and the Mermaid Live Editor
both run Mermaid 10/11. A diagram that looks perfect locally can fail in ADO. Run the
validator — that is precisely the gap it closes.

```bash
python3 scripts/validate_ado_mermaid.py path/to/page.md
python3 scripts/validate_ado_mermaid.py --recurse path/to/wiki --strict
```

---

## 9. Sources

- Markdown syntax for wikis — <https://learn.microsoft.com/en-us/azure/devops/project/wiki/markdown-guidance>
- Sprint 200 release note (the 8.13.9 pin and the supported-type list) — <https://learn.microsoft.com/en-us/azure/devops/release-notes/2022/wiki/sprint-200-update>
- Mermaid 8.13.9 docs — <https://github.com/mermaid-js/mermaid/releases/tag/8.13.9>

Re-verify the version if Microsoft ships a Mermaid upgrade; the constraints above loosen
considerably if ADO ever moves to Mermaid 10+.
